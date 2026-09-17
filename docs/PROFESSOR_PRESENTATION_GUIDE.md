# Roteiro de apresentação ao professor e propostas para o artigo

## 1. Resposta direta sobre o artigo da qualificação

O artigo da qualificação **não estava disponível nos arquivos acessíveis desta tarefa**. Portanto, esta análise não compara o sistema com o texto já escrito e não confirma se metodologia, resultados e referências do artigo estão alinhados com a implementação atual. Para fazer essa revisão, é necessário enviar o PDF ou DOCX do artigo.

O roteiro abaixo foi produzido a partir do código, dos artefatos de treinamento, dos manifests dos datasets, das métricas congeladas e da auditoria executada no sistema.

## 2. Mensagem principal da apresentação

> Desenvolvemos um protótipo acadêmico de apoio computacional à análise de lesões dermatoscópicas. O sistema combina CNN, Vision Transformer e um modelo híbrido em um Ensemble ponderado, incorpora triagem de qualidade e domínio, estima incerteza, permite abstenção e produz mapas de explicabilidade restringidos por um localizador auxiliar de lesão. O sistema não substitui o médico e não possui validação clínica prospectiva.

Essa frase resume corretamente a contribuição sem prometer diagnóstico autônomo.

## 3. O que foi desenvolvido

### 3.1 Pipeline de dados

O pipeline principal usa o **HAM10000**, com 10.015 imagens dermatoscópicas e sete classes: `akiec`, `bcc`, `bkl`, `df`, `mel`, `nv` e `vasc`. As classes `akiec`, `bcc` e `mel` foram agrupadas como malignas para a tarefa binária. O manifesto registra 7.470 grupos de lesão, seed 42 e divisão agrupada, reduzindo o risco de imagens correlacionadas da mesma lesão aparecerem simultaneamente em treino e teste.[1]

O conjunto de teste congelado contém 1.527 imagens. Ele não foi usado para escolher os pesos do Ensemble nem os hiperparâmetros.

### 3.2 Modelos

Foram implementados três componentes:

| Modelo | Arquitetura | Papel |
|---|---|---|
| CNN | ResNet-50 | Captura padrões locais, textura, bordas e estruturas dermatoscópicas |
| ViT | `vit_small_patch16_224` | Modela relações globais entre regiões da imagem |
| Hybrid | ResNet-50 + tokens + atenção multi-head | Combina representação convolucional e atenção global por um gate aprendido |

Cada modelo possui uma cabeça multitarefa com duas saídas: classificação fina em sete classes e classificação binária benigna/maligna. A supervisão multitarefa procura preservar informação dermatológica mais rica do que uma saída exclusivamente binária.

O treinamento contempla transferência de aprendizado, focal loss, pesos por número efetivo de amostras, amostragem balanceada apenas no treino, AdamW, clipping de gradiente, scheduler cosseno e calibração de temperatura. Validação e teste mantêm sua distribuição original.

### 3.3 Ensemble

O Ensemble combina as probabilidades malignas dos três modelos. Os pesos foram escolhidos no conjunto de validação:

```text
CNN     = 0,10
ViT     = 0,55
Hybrid  = 0,35
```

A probabilidade agregada pode ser descrita por:

```text
p_ensemble = 0,10·p_CNN + 0,55·p_ViT + 0,35·p_Hybrid
```

O Ensemble é a saída principal do sistema. As previsões individuais permanecem visíveis para permitir inspeção de concordância e divergência.

### 3.4 Incerteza e abstenção

Cada checkpoint executa Test-Time Augmentation com três amostras. O sistema calcula entropia preditiva e variância TTA. O Ensemble recomenda abstenção quando ocorre pelo menos uma destas condições:

- quantidade configurada de modelos individuais vota pela abstenção;
- entropia agregada ultrapassa 0,75;
- variância TTA ultrapassa 0,03.

Na configuração auditada, são exigidos dois votos individuais. A abstenção é uma barreira operacional; não transforma um resultado aceito em certeza clínica.

### 3.5 Triagem de qualidade e fora do domínio

Antes da inferência, o sistema verifica resolução, proporção, nitidez, exposição, contraste, uniformidade e características estatísticas de cor/luminância. Uma referência robusta construída com o HAM10000 calcula distância fora do domínio. Imagens incompatíveis podem ser rejeitadas antes da classificação.

A distância OOD usa centro robusto e escala robusta das características do HAM10000. O limiar foi definido pelo percentil 99,5 das distâncias na validação. Isso é uma barreira estatística, não um reconhecedor semântico universal de todos os objetos possíveis.

### 3.6 Aplicação completa

A interface foi construída com React, TypeScript e Vite. O backend usa Express e tRPC; a validação de contratos usa Zod. O servidor TypeScript chama os módulos Python por processos controlados, com timeout e sem aceitar caminhos arbitrários fornecidos por usuários. Métricas são exibidas com Recharts. Há suporte a Drizzle/MySQL/MariaDB, mas a demonstração local atual usa fallback em memória, sem persistência após reiniciar o servidor.

## 4. O gate de localização: os pontos técnicos essenciais

### 4.1 O que ele é

O gate é uma **máscara binária auxiliar de localização de lesão**, produzida por uma pequena rede encoder-decoder semelhante a uma U-Net. Ela possui blocos convolucionais com canais 16, 32, 64 e bottleneck 96, conexões de skip e convoluções transpostas no decoder.

O localizador foi treinado com o **ISIC 2016 Part 1**, que fornece imagens dermatoscópicas e máscaras binárias de lesão.[2] O experimento usou seed 42, divisão 720/90/90 e resolução de entrada 160 × 160. A avaliação registrada foi Dice 0,8245 e IoU 0,7667 no teste do próprio ISIC 2016.

### 4.2 O que ele não é

O gate **não participa da classificação**. Ele não altera a classe, a probabilidade ou o score dos modelos. Sua função é exclusivamente restringir a visualização de explicabilidade.

Essa distinção deve ser enfatizada:

```text
Imagem ──► CNN / ViT / Hybrid ──► classe e probabilidade
   └─────► segmentador ISIC ─────► máscara usada apenas nos mapas XAI
```

Portanto, não se deve afirmar que o gate aumentou a acurácia do classificador sem um experimento específico que altere o caminho de classificação.

### 4.3 Como a máscara é produzida

1. A imagem é redimensionada para 160 × 160.
2. O segmentador retorna uma probabilidade por pixel.
3. A probabilidade é binarizada conforme o preset escolhido.
4. Mantém-se o maior componente conectado.
5. Aplica-se fechamento morfológico para preencher pequenas falhas.
6. Calcula-se a fração de área prevista.
7. Máscaras muito pequenas ou muito grandes são rejeitadas.

### 4.4 Presets de sensibilidade

| Preset | Limiar | Kernel | Aplicação |
|---|---:|---:|---|
| `strict` | 0,65 | 3 × 3 | Imagens limpas; reduz inclusão de fundo |
| `balanced` | 0,50 | 5 × 5 | Padrão recomendado |
| `permissive` | 0,35 | 7 × 7 | Pelos, sombra ou iluminação irregular; pode incluir mais fundo |

Na demonstração foi usado `balanced`. O modo permissivo não melhora o classificador; apenas reduz a possibilidade de cortar partes da região prevista na visualização.

### 4.5 Como o gate é aplicado aos mapas

A saliência original é normalizada e multiplicada pela máscara:

```text
S_gate(x,y) = normalize(S(x,y)) · 1[M(x,y) > 0,5]
```

Assim, pixels fora da máscara recebem saliência zero. A cor do overlay usa opacidade proporcional à saliência:

```text
alpha(x,y) = 0,70 · S_gate(x,y)^0,75
```

Quando a saliência é zero, o pixel da fotografia permanece exatamente igual ao original. Essa correção foi necessária porque uma versão anterior usava opacidade fixa e pintava o fundo mesmo sem evidência.

### 4.6 Relação com os métodos XAI

- **CNN:** Grad-CAM sobre o último mapa convolucional.
- **ViT:** atribuição `token × gradient`; quando o mapa é praticamente uniforme, usa gradiente da entrada como fallback.
- **Hybrid:** combina Grad-CAM do ramo CNN, atribuição de tokens e rollout de atenção.
- **Ensemble:** combina as saliências brutas dos três componentes com os pesos do Ensemble.

O gate restringe esses mapas, mas não os converte em segmentação clínica.

### 4.7 Critérios de segurança do gate

O sistema verifica se o checkpoint existe, mantém o maior componente conectado, aplica morfologia e rejeita áreas fora dos limites configurados. Se o segmentador estiver ausente, falhar ou produzir área inválida, o código registra a indisponibilidade. Na implementação atual, o mapa não restringido pode ser preservado como fallback; para uma versão clínica, seria mais seguro sinalizar explicitamente a ausência do gate ou suprimir o mapa.

### 4.8 Limitações científicas do gate

- Dice e IoU foram medidos no ISIC 2016, não em todo o HAM10000.
- Existe mudança de domínio entre datasets, equipamentos e protocolos.
- Pelos, régua, bolhas, sombras e iluminação podem alterar a máscara.
- Uma máscara visualmente plausível não prova fidelidade da explicação.
- Grad-CAM e atribuições por gradiente não demonstram causalidade.
- O gate pode omitir evidência usada pelo classificador que esteja fora da região prevista.

### 4.9 Resposta curta para o professor

> O gate é um segmentador auxiliar treinado com máscaras do ISIC 2016. Ele gera uma região provável de lesão, pós-processada pelo maior componente conectado e fechamento morfológico. Essa máscara multiplica apenas os mapas de saliência, zerando visualmente o fundo. Ela não altera a predição dos classificadores. Usamos o modo balanced, limiar 0,50 e kernel 5 × 5. No ISIC 2016, o segmentador obteve Dice 0,8245 e IoU 0,7667, mas reconhecemos que esses valores não garantem o mesmo desempenho no HAM10000 nem validade clínica.

## 5. Resultados que podem ser apresentados

| Modelo | Acurácia | Sensibilidade | Especificidade | AUROC | AUPRC | ECE |
|---|---:|---:|---:|---:|---:|---:|
| CNN | 0,7302 | 0,7333 | 0,7294 | 0,8293 | 0,5332 | 0,0544 |
| ViT | 0,7256 | 0,8533 | 0,6944 | 0,8500 | 0,5565 | 0,0456 |
| Hybrid | 0,7439 | 0,7967 | 0,7311 | 0,8370 | 0,4833 | 0,2269 |
| Ensemble | **0,7498** | **0,8233** | **0,7319** | **0,8600** | **0,5709** | **0,0706** |

O Ensemble apresentou o maior AUROC e AUPRC. O ViT apresentou maior sensibilidade, mas menor especificidade. O Hybrid teve ECE elevado, indicando pior calibração. Não esconda esse resultado; use-o como motivação para calibração e análise futura.

Na auditoria funcional, os quatro heatmaps foram gerados em 600 × 450. A diferença máxima fora da saliência foi zero, confirmando que o fundo não é mais colorido artificialmente.

## 6. Ferramentas e tecnologias usadas

### Ciência de dados e visão computacional

- Python 3.11;
- PyTorch e torchvision;
- `timm` para ResNet-50 e ViT;
- NumPy e pandas;
- scikit-learn para métricas e avaliação;
- OpenCV para pós-processamento morfológico e overlays;
- Pillow para leitura e transformação de imagens;
- Matplotlib para colormaps e visualização.

### Aplicação

- TypeScript;
- React 19;
- Vite e esbuild;
- Express;
- tRPC;
- Zod;
- Tailwind CSS e componentes Radix UI;
- Recharts;
- Drizzle ORM e MySQL/MariaDB como opção de persistência.

### Engenharia e validação

- VS Code;
- Git e GitHub;
- pnpm;
- Vitest;
- pytest;
- testes TypeScript, build de produção e auditoria end-to-end;
- scripts PowerShell para validar Python, dependências, checkpoints e inicialização no Windows.

## 7. Sequência recomendada da apresentação

### Slide 1 — Problema

Explique a relevância do câncer de pele e a variabilidade visual das lesões. Posicione o sistema como apoio acadêmico à análise dermatoscópica.

### Slide 2 — Objetivo

Apresente o objetivo: comparar e combinar modelos CNN, Transformer e híbrido, incorporando incerteza, triagem de domínio e explicabilidade.

### Slide 3 — Dados

Mostre HAM10000, sete classes, tarefa binária, 10.015 imagens, divisão por grupo e teste congelado. Explique desbalanceamento e risco de leakage.

### Slide 4 — Arquitetura

Mostre CNN, ViT, Hybrid e Ensemble. Explique cabeça multitarefa e pesos 0,10/0,55/0,35.

### Slide 5 — Barreiras de segurança

Apresente triagem de qualidade/OOD, TTA, entropia, variância e abstenção.

### Slide 6 — Explicabilidade e gate

Explique o gate ISIC, sua separação do classificador, os presets e as limitações. Mostre imagem original, máscara e os quatro mapas.

### Slide 7 — Resultados

Mostre a tabela comparativa. Destaque AUROC 0,86, sensibilidade 0,8233 e AUPRC 0,5709 do Ensemble. Explique que a acurácia isolada não é suficiente em dados desbalanceados.

### Slide 8 — Demonstração

1. Faça upload de uma imagem HAM10000.
2. Mostre a triagem aceita.
3. Compare os três modelos e o Ensemble.
4. Mostre confiança e incerteza.
5. Mostre os quatro heatmaps.
6. Abra histórico e métricas.
7. Se desejar, teste uma imagem claramente inadequada para mostrar rejeição, sem prometer rejeição universal.

### Slide 9 — Limitações e próximos passos

Apresente mudança de domínio, ausência de validação clínica prospectiva, diversidade tonal insuficiente no HAM10000, imperfeição do gate, histórico local volátil e necessidade de avaliação por especialistas.

## 8. Perguntas prováveis do professor

### “Por que usar três modelos?”

CNN captura padrões locais; ViT captura dependências globais; Hybrid procura combinar ambas as representações. O Ensemble reduz dependência de um único viés arquitetural.

### “Como evitaram vazamento de dados?”

A divisão foi feita por grupo de lesão, com seed 42. O teste foi congelado e os pesos do Ensemble foram escolhidos na validação.

### “O gate melhora a acurácia?”

Não. Na implementação atual ele modifica somente a visualização XAI. Para afirmar ganho de acurácia seria necessário inserir a máscara no caminho do classificador e realizar ablação controlada.

### “O heatmap prova que o modelo decidiu corretamente?”

Não. Ele indica sensibilidade local aproximada do modelo. Não é prova causal nem segmentação clínica.

### “Por que treinar o gate em outro dataset?”

O ISIC 2016 possui máscaras de segmentação oficiais. O HAM10000 principal é usado para classificação. Essa separação permite treinar localização supervisionada, mas introduz mudança de domínio que deve ser declarada.

### “Por que 160 × 160?”

Foi uma escolha de viabilidade computacional em CPU e de padronização dos checkpoints. O custo é possível perda de detalhes finos; resoluções maiores devem ser avaliadas em experimentos futuros.

### “O sistema funciona para fotografia de celular?”

O modelo foi treinado principalmente em dermatoscopia. Fotografias clínicas comuns são outro domínio e exigem validação externa e, possivelmente, novo treinamento.

### “Pode ser usado clinicamente?”

Não. Falta validação externa ampla, estudo prospectivo, avaliação de especialistas, análise regulatória e monitoramento de segurança.

## 9. O que pode ser adicionado ao artigo

### 9.1 Contribuições metodológicas

Inclua como contribuições:

1. comparação entre CNN, ViT e arquitetura híbrida;
2. Ensemble ponderado selecionado em validação;
3. cabeça multitarefa binária e multiclasses;
4. triagem robusta de qualidade e fora do domínio;
5. incerteza por TTA e política de abstenção;
6. XAI específico por arquitetura;
7. gate auxiliar de localização treinado com ISIC 2016;
8. protótipo full-stack reproduzível com auditoria end-to-end.

### 9.2 Seção específica sobre o gate

Adicione uma subseção intitulada **“Gate auxiliar de localização para restrição espacial da explicabilidade”** contendo:

- dataset ISIC 2016 e licença;
- arquitetura do segmentador;
- divisão 720/90/90 e seed 42;
- resolução 160 × 160;
- Dice e IoU;
- limiar, componente conectado e morfologia;
- equação de aplicação do gate;
- presets de sensibilidade;
- declaração de que a classificação não é alterada;
- limitações de mudança de domínio.

### 9.3 Experimentos adicionais recomendados

Antes de submeter um artigo, adicione:

- ablação **sem gate versus strict versus balanced versus permissive**;
- Dice/IoU do segmentador em um subconjunto HAM10000 com máscaras confiáveis;
- métricas de fidelidade XAI, como deletion, insertion e pointing game;
- estabilidade dos mapas sob pequenas transformações;
- intervalos de confiança por bootstrap;
- teste estatístico entre modelos;
- validação externa no ISIC 2019 ou conjunto autorizado equivalente;
- avaliação de diversidade tonal no DDI ou Fitzpatrick17k, respeitando os termos de uso; o DDI contém diagnósticos confirmados por biópsia e representação Fitzpatrick I–VI.[3]
- análise de erros por classe, dispositivo, localização anatômica e qualidade;
- estudo de concordância com dermatologistas.

### 9.4 Figuras sugeridas

1. Diagrama completo do pipeline.
2. Fluxo separado de classificação e gate XAI.
3. Distribuição das classes e splits.
4. Curvas ROC e precisão-recall.
5. Matriz de confusão binária e multiclasses.
6. Curva de calibração.
7. Comparação visual dos quatro mapas.
8. Máscara do gate e comparação dos três presets.
9. Exemplos de acerto, erro, abstenção e rejeição OOD.

### 9.5 Afirmações que devem ser evitadas

Não escreva que:

- o sistema diagnostica câncer;
- todo objeto não dermatológico será recusado;
- os heatmaps provam causalidade;
- o gate é uma segmentação clínica perfeita;
- o Ensemble é superior clinicamente apenas por AUROC interno;
- o HAM10000 demonstra equidade entre tons de pele;
- os resultados internos generalizam para fotografia clínica ou celular.

## 10. Fechamento recomendado

> Os resultados mostram viabilidade técnica e um pipeline reproduzível de classificação, incerteza e explicabilidade em dermatoscopia. A principal contribuição não é somente a predição, mas a integração de mecanismos de controle: triagem de domínio, abstenção, comparação entre arquiteturas e restrição espacial dos mapas. O próximo passo é validar externamente o desempenho, a calibração, a fidelidade das explicações e a robustez entre subgrupos antes de qualquer aplicação clínica.

## Referências

[1]: https://doi.org/10.7910/DVN/DBW86T "HAM10000 Dataset, Harvard Dataverse"
[2]: https://challenge.isic-archive.com/data/ "ISIC Challenge Datasets"
[3]: https://ddi-dataset.github.io/ "Diverse Dermatology Images Dataset"
