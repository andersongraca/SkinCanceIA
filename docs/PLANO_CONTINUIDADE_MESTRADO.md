# Plano de Continuidade do Mestrado

**Projeto:** SkinCancerCADDermoIA
**Finalidade:** orientar a conclusão da dissertação após o exame de qualificação
**Data-base:** 17 de setembro de 2026

## 1. Decisão central

O trabalho continuará no **mestrado** com um objetivo delimitado: transformar o protótipo já desenvolvido em uma dissertação cientificamente coerente, reproduzível, auditável e compatível com as exigências do parecer. A dissertação não precisa converter o sistema em produto clínico nem provar generalização nacional. Ela deve demonstrar corretamente o que foi implementado, quantificar o desempenho interno, identificar limitações e responder de modo verificável às críticas da qualificação.

> **Produto final do mestrado:** um baseline auditável de classificação de imagens dermatoscópicas com CNN, Vision Transformer, modelo Hybrid e Ensemble, acompanhado de calibração, incerteza, triagem OOD, política de abstenção, XAI restringida por localização auxiliar e aplicação full-stack, sem reivindicação de diagnóstico ou validação clínica.

## 2. Pergunta e objetivo da dissertação

### 2.1 Pergunta de pesquisa recomendada

**Como CNN, Vision Transformer, modelo híbrido e Ensemble se comportam em uma avaliação interna e reprodutível do HAM10000 quanto a discriminação, calibração, incerteza, classificação seletiva e explicabilidade, e quais são os limites de transporte para outros domínios e populações?**

### 2.2 Objetivo geral recomendado

> Desenvolver e avaliar, em protocolo experimental reprodutível, um protótipo acadêmico de apoio à classificação de imagens dermatoscópicas que compare CNN, Vision Transformer, modelo híbrido e Ensemble ponderado quanto a discriminação, calibração, incerteza e comportamento das saliências, sem reivindicar uso diagnóstico autônomo.

### 2.3 Objetivos específicos

1. Documentar o HAM10000, o agrupamento por lesão, as sete classes, a tarefa binária, a seed e as partições.
2. Comparar CNN ResNet-50, ViT, Hybrid e Ensemble no mesmo teste congelado.
3. Recalcular métricas e intervalos de confiança a partir das predições por imagem.
4. Avaliar calibração por ECE, Brier score e curvas de confiabilidade.
5. Avaliar entropia, variância por Test-Time Augmentation e risco–cobertura da abstenção.
6. Caracterizar a triagem de qualidade e OOD em painel independente e limitado.
7. Avaliar Grad-CAM, atribuição de tokens, mapa Hybrid e mapa do Ensemble com testes mínimos de fidelidade, estabilidade e sanidade.
8. Comparar os modos `sem gate`, `strict`, `balanced` e `permissive`, mantendo o gate separado do caminho de classificação.
9. Auditar software, artefatos, dependências, versões, logs e reprodutibilidade.
10. Discutir explicitamente mudança de domínio, tons de pele, população brasileira e lesões acrais.

## 3. Correções obrigatórias do parecer

| Exigência | Ação | Evidência de conclusão |
|---|---|---|
| Duplicações no Capítulo 2 | Remover 2.5–2.7 redundantes e manter uma seção de datasets, CNN e Transformers | Comparação textual; sumário e PDF recompilados |
| Erros linguísticos | Corrigir “solução promissora”, “O pré-processamento”, erros da seleção da RSL e revisar o documento integral | Busca no fonte e inspeção visual do PDF |
| Citações | Converter `[49]` e citações numéricas residuais para ABNT autor-data | Conferência cruzada entre texto e bibliografia |
| HAM10000 | Corrigir “100000” para “10000 Training Images” e informar separadamente 10.015 imagens | Fonte, PDF e tabela de dados coerentes |
| Compilação | Corrigir `\tilde{A}`, remover preâmbulo impresso e revisar caracteres | Log de compilação e inspeção página a página |
| Fluxo da RSL | Recuperar no Parsifal identificação, duplicatas, triagem, texto completo e 51 incluídos | Fluxograma com números reconciliados |
| Viés demográfico | Inserir limitação e protocolo de validação externa por tom de pele e localização | Discussão, limitações e trabalhos futuros revisados |

## 4. Atualização necessária do conteúdo técnico

O artigo de qualificação descreve uma proposta com ISIC-2019 e Django. A dissertação deve registrar a versão efetivamente desenvolvida:

- **Classificação:** HAM10000, 10.015 imagens, sete classes, 7.470 grupos de lesão e teste congelado de 1.527 imagens.
- **Modelos:** CNN ResNet-50, Vision Transformer, Hybrid e Ensemble ponderado.
- **Pesos do Ensemble:** 0,10 para CNN, 0,55 para ViT e 0,35 para Hybrid, selecionados na validação.
- **Gate XAI:** localizador auxiliar treinado no ISIC 2016; Dice 0,8245 e IoU 0,7667 no teste desse dataset. O gate afeta apenas a visualização.
- **Aplicação:** React, TypeScript e Vite no frontend; Express, tRPC e Zod no backend; módulos Python/PyTorch para inferência.
- **Persistência:** banco opcional; fallback em memória na demonstração local, com perda do histórico após reinício.

Os resultados internos auditados do Ensemble são acurácia 0,7498, sensibilidade 0,8233, especificidade 0,7319, AUROC 0,8600, AUPRC 0,5709 e ECE 0,0706. Esses valores não podem ser apresentados como acurácia clínica ou comparados diretamente aos números próximos de 99% da literatura sem harmonizar dataset, tarefa e protocolo.

## 5. Plano experimental do mestrado

### 5.1 Avaliação interna reprodutível

As predições de cada imagem do teste congelado devem ser exportadas com identificador do grupo de lesão, rótulo verdadeiro, probabilidades e decisão de CNN, ViT, Hybrid e Ensemble. A partir desse arquivo, devem ser calculados acurácia, sensibilidade, especificidade, AUROC, AUPRC, macro-F1, balanced accuracy, Brier score, ECE e matrizes de confusão. Intervalos de confiança de 95% devem usar bootstrap agrupado pela lesão, preservando a dependência entre imagens correlacionadas.

### 5.2 Calibração e incerteza

A dissertação deve apresentar curvas de confiabilidade e Brier score de todos os modelos. O ECE 0,2269 do Hybrid deve ser discutido como sinal de calibração inferior. A regra atual de abstenção deve ser convertida em curva risco–cobertura, com AURC, cobertura e erro condicional, sem escolher limiares no teste final.

### 5.3 OOD e qualidade

O teste OOD deve usar painel rotulado com pelo menos quatro categorias: imagens dermatoscópicas válidas, imagens dermatológicas de outro domínio, imagens degradadas e objetos não dermatológicos. Devem ser reportados falsos aceites e falsos rejeites. O resultado não deve ser descrito como reconhecimento universal de qualquer imagem externa.

### 5.4 Gate e XAI

Os modos `sem gate`, `strict`, `balanced` e `permissive` devem ser comparados quanto a área da máscara, taxa de máscara inválida e estabilidade. Para XAI, deve haver pelo menos um teste de fidelidade, um de estabilidade sob transformações e um teste de sanidade por randomização. A análise visual permanece útil como evidência qualitativa, mas não substitui métricas nem prova causalidade.

### 5.5 Eficiência e engenharia

A latência deve ser medida por etapa e repetida no mesmo hardware. Devem ser registrados processador, memória, sistema operacional, versão do Python, PyTorch, Node e dependências. A barra da interface é uma estimativa de progresso, não telemetria científica. A auditoria de software deve registrar testes aprovados, ignorados, cobertura, build, hashes dos checkpoints, falhas e comportamento sem banco.

## 6. Resposta ao viés demográfico apontado pela banca

A resposta no mestrado terá duas partes. A primeira é obrigatória: declarar que o HAM10000 usado não oferece metadados suficientes para demonstrar equidade por tom de pele, população brasileira ou localização acral. A segunda é experimental, se tecnicamente viável: realizar validação externa exploratória.

O **PAD-UFES-20** é uma base brasileira com 2.298 imagens clínicas obtidas por smartphones, 1.373 pacientes, 1.641 lesões e metadados que incluem tipo de pele Fitzpatrick e localização. Aproximadamente 58% das amostras possuem confirmação por biópsia.[1] Como suas imagens são clínicas e o classificador foi treinado em dermatoscopia, o experimento mede principalmente **mudança de domínio**. Uma queda de desempenho seria um resultado científico esperado e relevante, não um fracasso.

O **DDI** contém imagens patologicamente confirmadas e grupos comparáveis de tons Fitzpatrick. Em avaliação publicada, um modelo HAM10000 teve AUROC 0,72 em Fitzpatrick I–II e 0,57 em V–VI, demonstrando que bom desempenho na base original não garante equidade externa.[2] O DDI pode ser usado para avaliar disparidade somente após verificar licença, tarefa e mapeamento de rótulos.

A relevância de lesões acrais deve ser discutida sem alegar cobertura atual. Uma coorte brasileira de melanoma acral plantar mostrou maioria de participantes pardos e negros e ressaltou que dados nacionais ainda são escassos.[3] No mestrado, isso fundamenta a limitação e a necessidade de dados específicos; a construção de coorte multicêntrica pertence a pesquisa posterior.

## 7. Auditoria a escrever na dissertação

A auditoria deve ser dividida em duas subseções.

### 7.1 Auditoria científica

Ela deve verificar proveniência dos dados, ausência de vazamento, separação treino–validação–teste, escolha dos pesos do Ensemble, predições por imagem, recomputação de métricas, intervalos de confiança, calibração, erros por classe, incerteza, OOD, gate e XAI. A organização pode seguir **TRIPOD+AI**, que enfatiza transparência, dados de avaliação separados, calibração, fairness, subgrupos e ciência aberta.[4]

### 7.2 Auditoria de software

Ela deve verificar TypeScript, Vitest, Pytest, build, versões, hashes, carga dos checkpoints, quatro mapas, upload, timeouts, erros, persistência, reinício, logs, segurança de caminhos e reconstrução do ambiente. Essa auditoria demonstra funcionamento do protótipo; não comprova desempenho clínico.

A avaliação de risco de viés deve usar **PROBAST+AI**, separando qualidade do desenvolvimento e risco de viés da avaliação nos domínios participantes/fontes, preditores, desfecho e análise.[5]

## 8. Estrutura final recomendada da dissertação

1. **Introdução:** problema, lacuna, viés de representação, objetivos, contribuições e escopo.
2. **Fundamentação:** dermatoscopia, datasets, CNN, ViT, Hybrid, Ensemble, calibração, incerteza, OOD, XAI e métricas.
3. **Revisão Sistemática:** protocolo, fluxo reconciliado, resultados, lacunas e viés demográfico.
4. **Metodologia e sistema:** HAM10000, splits, arquiteturas, treino, Ensemble, TTA, abstenção, OOD, gate, XAI e aplicação.
5. **Resultados:** métricas internas, intervalos, calibração, risco–cobertura, OOD, gate/XAI, eficiência e testes.
6. **Discussão:** interpretação, comparação com literatura, mudança de domínio, equidade, limites clínicos e ameaças à validade.
7. **Conclusão e trabalhos futuros:** resposta à pergunta, contribuições comprovadas e agenda posterior delimitada.
8. **Apêndices:** manifestos, splits, hiperparâmetros, scripts, checklist TRIPOD+AI/PROBAST+AI, logs e auditoria.

## 9. Cronograma proposto

| Período | Atividades | Entregáveis |
|---|---|---|
| 17–30/09/2026 | Correções do parecer, RSL, escopo e congelamento de versão | Manuscrito corrigido e matriz de resposta |
| 01–15/10/2026 | Predições, métricas, bootstrap, calibração e figuras | Metodologia e resultados internos fechados |
| 16–31/10/2026 | Risco–cobertura, OOD, gate, XAI, latência e auditoria | Resultados complementares reproduzíveis |
| 01–10/11/2026 | PAD-UFES-20/DDI se viável; análise de domínio e limitações | Resposta empírica ou protocolo justificado |
| 11–20/11/2026 | Discussão, limitações, conclusão e trabalhos futuros | Primeira versão integral |
| 21–30/11/2026 | Revisão do orientador, ABNT e revisão linguística | Versão de pré-depósito |
| 01–07/12/2026 | Auditoria final, compilação e inspeção visual | PDF e pacote reproduzível finais |
| 08–15/12/2026 | Slides, demonstração e defesa simulada | Apresentação e plano de contingência |

As datas devem ser ajustadas ao calendário oficial. Se não houver tempo para uma avaliação externa válida, ela não deve ser improvisada: a dissertação deve manter a limitação e apresentar protocolo reprodutível para execução futura.

## 10. Critérios de aceite para a defesa

O mestrado estará pronto para defesa quando:

- todas as exigências do parecer tiverem ação e evidência;
- o PDF não contiver duplicações, erros de compilação ou citações inconsistentes;
- dados, modelos, software e resultados corresponderem à versão real;
- métricas e intervalos puderem ser reproduzidos a partir das predições;
- auditoria científica e auditoria de software estiverem separadas;
- limitações sobre tons de pele, lesões acrais e população brasileira estiverem explícitas;
- os mapas XAI forem descritos como aproximações, não causalidade;
- o sistema for chamado de protótipo acadêmico, não sistema diagnóstico;
- fonte, PDF, código, manifestos, splits, logs e hashes estiverem arquivados.

## 11. Atividades reservadas para uma pesquisa de doutorado

Não pertencem ao Plano de Continuidade do mestrado: criar coorte brasileira multicêntrica; realizar validação prospectiva; avaliar uso assistido por dermatologistas; implantar aprendizado federado; estudar privacidade diferencial; executar modo silencioso em hospital; desenvolver monitoramento pós-implantação; ou buscar enquadramento regulatório. Essas atividades formam uma agenda posterior, dependente de ingresso no doutorado, orientação, parcerias, ética e financiamento.

## Referências

[1]: https://data.mendeley.com/datasets/zr7vgbcyr2/1 "PAD-UFES-20"

[2]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9374341/ "Disparities in dermatology AI performance on a diverse, curated clinical image set"

[3]: https://www.scielo.br/j/abd/a/XFLJ37RNwYSY6kBwPGQgSyj/?lang=en "Plantar acral melanoma: a Brazilian cohort"

[4]: https://www.bmj.com/content/385/bmj-2023-078378 "TRIPOD+AI statement"

[5]: https://www.bmj.com/content/388/bmj-2024-082505 "PROBAST+AI"
