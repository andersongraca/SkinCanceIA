# Plano técnico para o back-end de classificação dermatoscópica

## 1. Diretriz científica

O back-end atual é um protótipo de integração: os modelos retornam valores aleatórios, as métricas são fixas e os heatmaps não são gerados. A próxima implementação deverá substituir essa simulação por um pipeline reprodutível, sem declarar desempenho antes da execução dos experimentos. O objetivo não será apenas aumentar a acurácia, mas medir **generalização, calibração, incerteza, equidade e fidelidade das explicações**.

A escolha por uma arquitetura híbrida é coerente com a literatura: uma CNN captura textura, cor e bordas em escala local, enquanto um Transformer modela relações espaciais de longo alcance. Um estudo de referência combinou extração convolucional, ViT e focal loss para lidar com o desequilíbrio do ISIC 2018 [1][ref1]. Trabalhos mais recentes reforçam a utilidade de preservar detalhes espaciais durante a tokenização e fundir características locais e globais [2][ref2]. Esses trabalhos serão usados como referências metodológicas e não como justificativa para copiar uma arquitetura sem ablação.

## 2. Escopo de saída do modelo

O HAM10000 possui 10.015 imagens dermatoscópicas e sete categorias diagnósticas, mas a interface atual foi desenhada para uma decisão binária entre lesão benigna e maligna [4][ref4]. Para conciliar o desenho da dissertação com o contrato atual do sistema, a implementação deverá usar **aprendizado multitarefa**: uma cabeça multiclasses para as sete categorias e uma cabeça binária para o risco maligno. A API continuará retornando `benign` ou `malignant`, mas também poderá retornar probabilidades multiclasses, permitindo avaliação científica sem alterar o front-end.

| Saída | Finalidade | Compatibilidade |
| --- | --- | --- |
| `classification` | Decisão binária final: `benign` ou `malignant` | Preserva o contrato atual |
| `confidence` e `probabilities` | Probabilidade binária calibrada | Preserva o contrato atual |
| `fineGrainedClass` e `fineGrainedProbabilities` | Sete classes HAM/ISIC | Novo campo opcional no back-end |
| `uncertainty` | Entropia, variância e indicador de rejeição | Novo campo opcional |
| `modelVersion` | Rastreabilidade dos pesos e do pré-processamento | Compatível com o banco existente |
| `heatmapPaths` | Mapas CNN, ViT, híbrido e ensemble | Compatível com `heatmapPath`, com extensão JSON opcional |

O mapeamento binário deverá ser explicitamente configurável e documentado. A definição inicial recomendada é considerar MEL, BCC e AKIEC como classes de maior preocupação clínica, mas essa regra não deve ser codificada definitivamente sem confirmação do orientador e do patologista, pois a taxonomia de “maligno” pode depender do objetivo clínico da dissertação.

## 3. Arquitetura recomendada

A arquitetura principal será composta por três modelos comparáveis e um ensemble. A CNN será um backbone residual moderno com atenção de canal leve, o ViT será treinado com transferência de aprendizado e o híbrido combinará características intermediárias, em vez de simplesmente fazer média de duas confidências.

| Componente | Proposta | Justificativa | Explicabilidade |
| --- | --- | --- | --- |
| CNN | ResNet-50 pré-treinada, com camada de classificação substituída, ECA/CBAM opcional e dropout estocástico | Mantém comparabilidade com o nome já usado no protótipo e oferece mapas convolucionais estáveis | Grad-CAM++ ou Grad-CAM na última camada convolucional |
| ViT | ViT-S/16 ou DeiT-S/16 pré-treinado, com cabeça multitarefa | Captura dependências globais; o patch size precisa ser registrado no experimento | Transformer attribution/rollout com gradientes e Integrated Gradients como comparação |
| Híbrido | Mapa intermediário da CNN convertido em tokens, encoder Transformer, concatenação com token CLS e fusão com gate aprendido | Faz fusão em nível de representação e evita pesos fixos de 0,5/0,5 | Mapa CNN, atribuição de tokens e mapa híbrido ponderado por contribuição |
| Ensemble | Média logit/probabilidade calibrada dos modelos, com pesos definidos apenas na validação | Evita votação baseada em limiar arbitrário e permite estimar variância entre modelos | Mapa agregado acompanhado da contribuição de cada ramo |

A forma recomendada para a fusão híbrida é obter `f_cnn` por pooling global do mapa convolucional e `f_vit` pelo token CLS. Um módulo de gating calcula `g = sigmoid(MLP([f_cnn, f_vit]))`; a representação final é `f = g * norm(f_cnn) + (1-g) * norm(f_vit)`, seguida por um bloco MLP com normalização e dropout. Durante o treinamento, cabeças auxiliares CNN e ViT recebem perdas próprias, enquanto a cabeça híbrida recebe a perda principal. Essa supervisão profunda reduz o risco de um dos ramos tornar-se inútil.

## 4. Treinamento e regularização

O treinamento deverá começar com os backbones congelados por algumas épocas, seguir para descongelamento progressivo e terminar com fine-tuning discriminativo. A configuração inicial recomendada é AdamW, warm-up curto, decaimento coseno, weight decay controlado, gradient clipping, mixed precision quando houver GPU e early stopping pela métrica definida a priori. O uso de focal loss ou class-balanced focal loss será comparado com cross-entropy ponderada, pois o ISIC 2018 apresenta forte desequilíbrio entre classes [1][ref1].

As transformações deverão ser aplicadas somente ao conjunto de treinamento. Serão comparadas duas políticas: uma conservadora, com rotação, espelhamento, crop, variação moderada de brilho/contraste e normalização; e uma política avançada, com MixUp/CutMix, RandAugment e regularização de oclusão. Hair removal, CLAHE e filtros de nitidez deverão ser tratados como **ablação**, não como pré-processamento obrigatório, porque podem retirar ou introduzir sinais artificiais. Cada transformação precisará ser registrada na configuração do experimento.

A temperatura do softmax não será interpretada como confiança clínica sem calibração. Após o treinamento, o limiar binário e a temperatura deverão ser ajustados no conjunto de validação, mantendo o teste intocado. A camada de incerteza poderá combinar temperatura escalada, entropia preditiva e variância de um pequeno ensemble ou de Monte Carlo Dropout. Revisões de classificação médica apontam Monte Carlo Dropout, ensembles e temperature scaling como estratégias recorrentes para incerteza e calibração [9][ref9].

## 5. Protocolo de dados e generalização

Nenhuma divisão aleatória simples deverá ser aceita se houver identificador de lesão, paciente ou série. As imagens do mesmo paciente/lesão precisam permanecer no mesmo grupo para impedir vazamento. O HAM10000 contém imagens provenientes de diferentes locais, modalidades e fontes, e há identificadores comuns para imagens da mesma lesão [4][ref4]. O pipeline deverá deduplicar por identificador e por hash perceptual antes da divisão.

O protocolo mínimo será composto por treino, validação e teste interno estratificados por classe e agrupados por lesão/paciente. O teste deverá ser congelado e usado uma única vez por versão final. Se houver dados disponíveis, será incluído um teste externo por origem ou conjunto, pois diferenças de aquisição, iluminação, idade e localização geram mudança de domínio em dermatoscopia e podem reduzir o desempenho fora da distribuição de treino [3][ref3]. O arquivo de metadados deverá registrar a origem, local anatômico, idade, sexo, tipo de aquisição, identificador da lesão e qualquer proxy de fototipo disponível.

A preocupação levantada no parecer sobre tons de pele deve transformar-se em análise explícita. A revisão sistemática mais recente encontrou desempenho inferior em grupos Fitzpatrick IV–VI em comparação com I–III e recomenda relatório estratificado e validação externa [6][ref6]. Se o conjunto não possuir fototipo confiável, o relatório deverá declarar essa limitação, evitar imputação individual e usar somente subgrupos observáveis ou dados externos devidamente documentados.

## 6. Métricas e ablações

A avaliação não deverá depender de acurácia isolada. Para a saída binária serão calculados AUROC, AUPRC, sensibilidade, especificidade, precisão, F1, balanced accuracy, MCC, Brier score e ECE. Para as sete classes serão calculados macro-F1, balanced accuracy, AUROC one-vs-rest macro, AUPRC macro e métricas por classe. Serão apresentados intervalos de confiança por bootstrap estratificado no teste, além de matriz de confusão normalizada.

| Experimento | CNN | ViT | Híbrido | Ensemble | Objetivo |
| --- | ---: | ---: | ---: | ---: | --- |
| Baseline supervisionado | Sim | Sim | Sim | Opcional | Estabelecer referência reproduzível |
| Cross-entropy ponderada | Sim | Sim | Sim | Sim | Comparar com perda simples para desbalanceamento |
| Focal/class-balanced loss | Sim | Sim | Sim | Sim | Avaliar ganho real nas classes minoritárias |
| Sem e com atenção de canal | Sim | — | Sim | Opcional | Medir contribuição da atenção local |
| Late fusion versus feature fusion | — | — | Sim | — | Justificar a inovação do híbrido |
| Sem e com MixUp/CutMix | Sim | Sim | Sim | Opcional | Avaliar regularização e robustez |
| Teste interno versus externo | Sim | Sim | Sim | Sim | Medir mudança de domínio |
| Com e sem calibração | Sim | Sim | Sim | Sim | Verificar se confiança acompanha acerto |

A seleção da melhor configuração deverá ser feita apenas pela validação, priorizando sensibilidade para malignidade e calibração, e não pelo maior resultado observado depois de consultar o teste. Resultados não executados permanecerão identificados como “a avaliar”.

## 7. Heatmaps e validação das explicações

Para a CNN, Grad-CAM/Grad-CAM++ será calculado usando o logit da classe-alvo na última camada convolucional. O método Grad-CAM é apropriado para gerar mapas class-discriminativos a partir dos gradientes que chegam à última camada convolucional [7][ref7]. Para o ViT, a implementação principal deverá usar atribuição baseada em gradiente e agregação de atenção, mantendo uma alternativa de Integrated Gradients. A implementação oficial de Transformer Interpretability Beyond Attention Visualization calcula relevância por camada, incorpora gradientes nas cabeças e agrega as camadas por rollout [8][ref8].

O mapa híbrido deverá ser gerado separadamente para cada ramo e depois normalizado na mesma escala. A combinação não deverá ser uma média visual fixa: a contribuição deverá refletir o gate ou a decomposição de logit, com o mapa final acompanhado dos mapas individuais. Como mapas de atenção podem destacar artefatos, será implementada uma avaliação de fidelidade por inserção/deleção e, quando houver máscaras de lesão, uma comparação quantitativa com IoU/pointing game. Estudos comparativos em imagens médicas mostram que mapas de atenção podem conter artefatos e que a escolha do método deve ser avaliada quantitativamente, não apenas por aparência [10][ref10].

O resultado será apresentado como **explicação da evidência usada pelo modelo**, não como segmentação clínica nem como prova de causalidade. A aplicação deve registrar a classe explicada, o valor do logit, a versão dos pesos, o pré-processamento, o método de XAI e o timestamp para que o mapa seja reproduzível.

## 8. Integração no back-end sem modificar a interface

A integração deve seguir o padrão tRPC já usado no projeto. Será acrescentada uma mutação protegida de análise que receba o arquivo validado, persista o original em storage, execute a inferência e salve os resultados no banco. O armazenamento deve guardar apenas referências e URLs/chaves; os bytes das imagens e heatmaps não devem ser inseridos em colunas do banco [ref-storage].

| Camada | Alteração prevista | Front-end |
| --- | --- | --- |
| `server/services` | Substituir simulações por adaptador de inferência real, pré-processamento, calibração e XAI | Nenhuma |
| `server/db.ts` | Conectar inserção de imagem, diagnóstico e métricas | Nenhuma |
| `server/routers.ts` | Adicionar mutação protegida de análise e consultas detalhadas | Nenhuma nesta fase |
| `drizzle/schema.ts` | Acrescentar campos opcionais para probabilidades, incerteza e heatmaps múltiplos | Nenhuma |
| `server/storage.ts` | Reutilizar helper existente para imagens e mapas | Nenhuma |
| `client/src` | Não alterar | Mantido |

A estratégia de execução do modelo ainda depende da disponibilidade de pesos e do ambiente de implantação. Como o repositório atual contém Node.js/TensorFlow.js, há duas opções: converter modelos treinados para um formato executável no Node, como ONNX/TensorFlow.js, ou adicionar um serviço Python de inferência com PyTorch. A escolha final deverá ser feita depois de confirmar onde estão os pesos, se há GPU e se o ambiente de produção aceita outro runtime. Não serão adicionados pesos grandes ao repositório sem confirmação de licença e infraestrutura.

## 9. Critérios para avançar para implementação

A implementação poderá começar quando forem confirmados: o conjunto de dados e seus arquivos de metadados; a definição binária/multiclasse; os pesos existentes ou a necessidade de treinamento; a disponibilidade de GPU; o ambiente de implantação; e a autorização para criar uma migração de banco. Até essa confirmação, qualquer métrica exibida pelo protótipo deverá ser tratada como dado de demonstração, não como resultado da dissertação.

## Referências

[ref1]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9818899/ "Nie et al., A Deep CNN Transformer Hybrid Model for Skin Lesion Classification of Dermoscopic Images Using Focal Loss, Diagnostics, 2022"
[ref2]: https://www.nature.com/articles/s41598-025-18570-1 "Halawani et al., Enhanced early skin cancer detection through fusion of vision transformer and CNN features using hybrid attention of EViT-Dens169, Scientific Reports, 2025"
[ref3]: https://doi.org/10.1016/j.nbt.2023.04.006 "Fogelberg et al., Domain shifts in dermoscopic skin cancer datasets: Evaluation of essential limitations for clinical translation, New Biotechnology, 2023"
[ref4]: https://pmc.ncbi.nlm.nih.gov/articles/PMC6091241/ "Tschandl et al., The HAM10000 dataset, Scientific Data, 2018"
[ref5]: https://challenge.isic-archive.com/data/ "ISIC Challenge Datasets, página oficial"
[ref6]: https://pmc.ncbi.nlm.nih.gov/articles/PMC12735087/ "Tjiu and Lu, Equity and Generalizability of Artificial Intelligence for Skin-Lesion Diagnosis, Medicina, 2025"
[ref7]: https://openaccess.thecvf.com/content_iccv_2017/html/Selvaraju_Grad-CAM_Visual_Explanations_ICCV_2017_paper.html "Selvaraju et al., Grad-CAM, ICCV, 2017"
[ref8]: https://github.com/hila-chefer/Transformer-Explainability "Chefer et al., Transformer Interpretability Beyond Attention Visualization, implementação oficial CVPR 2021"
[ref9]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9382553/ "Kurz et al., Uncertainty Estimation in Medical Image Classification: Systematic Review, JMIR Medical Informatics, 2022"
[ref10]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11999707/ "Rahnfeld et al., A comparative study of explainability methods for whole slide classification using vision transformers, PLOS Digital Health, 2025"
[ref-storage]: https://github.com/andersongraca/SkinCancerCADDermoIA/blob/master/server/storage.ts "Helper de storage já presente no repositório"
