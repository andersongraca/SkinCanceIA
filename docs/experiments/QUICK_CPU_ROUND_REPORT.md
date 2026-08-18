# Relatório da rodada rápida em CPU

## Objetivo e escopo

Esta rodada foi executada como uma verificação operacional reproduzível do backend científico, sem substituir o treinamento final recomendado em GPU. O objetivo foi confirmar que os três caminhos de modelagem — CNN baseada em ResNet-50, Vision Transformer e arquitetura híbrida CNN–ViT — conseguem treinar, salvar checkpoints, produzir logits no conjunto de teste congelado e alimentar o Ensemble Learning com calibração e intervalos de confiança.

> **Interpretação:** os resultados abaixo são evidências de funcionamento integrado e uma linha de base operacional. Como cada modelo foi treinado por apenas uma época, com resolução de 160×160 e backbone congelado, eles não devem ser apresentados como a versão final de desempenho da dissertação.

## Protocolo

| Item | Configuração |
|---|---|
| Dataset | HAM10000 autorizado para uso acadêmico não comercial |
| Divisão | Treino, validação e teste congelado definidos previamente |
| Imagens no teste | 1.527 |
| Resolução | 160×160 pixels |
| Épocas | 1 por modelo |
| Dispositivo | CPU |
| Backbone | Pré-treinado, congelado nesta rodada |
| Amostragem | Balanceada por amostragem com reposição, usando inverso da frequência com suavização pela raiz quadrada |
| Calibração | Temperatura separada para saída multiclasse e binária |
| Ensemble | Média ponderada dos logits/probabilidades, com pesos escolhidos na validação |
| Bootstrap | 1.000 reamostragens, seed 42, IC de 95% |

## Resultados de validação

O escore usado para selecionar o melhor checkpoint foi a AUROC binária na validação. O ViT obteve o maior valor isolado nesta rodada, enquanto o híbrido apresentou valor intermediário e a CNN o menor dos três; a seleção de pesos do ensemble foi feita separadamente na validação, sem utilizar rótulos do teste.

| Modelo | AUROC binária na validação | Sensibilidade | Especificidade | Backbone congelado |
|---|---:|---:|---:|---|
| CNN | 0,8409 | — | — | Sim |
| ViT | 0,8554 | — | — | Sim |
| Híbrido CNN–ViT | 0,8490 | 0,6701 | 0,8343 | Sim |

## Pesos selecionados e teste congelado

Os pesos selecionados na validação foram 15% para a CNN, 45% para o ViT e 40% para o híbrido. A avaliação final foi realizada uma única vez no teste congelado, preservando a separação entre ajuste de pesos e estimativa de desempenho.

| Métrica do ensemble | Estimativa no teste |
|---|---:|
| AUROC binária | 0,8670 |
| Sensibilidade binária | 0,8367 |
| Especificidade binária | 0,7343 |
| F1 binário | 0,5724 |
| AUROC macro multiclasse | 0,9018 |
| F1 macro multiclasse | 0,4361 |
| Acurácia multiclasse | 0,6215 |
| Balanced accuracy multiclasse | 0,6120 |
| ECE binário | 0,0399 |
| Brier binário | 0,1539 |

O ensemble apresentou maior sensibilidade que especificidade nesta configuração, característica compatível com uma triagem orientada à redução de falsos negativos, mas que exige acompanhamento dos falsos positivos e calibração de limiar conforme o objetivo clínico. O sistema não constitui diagnóstico médico e a classificação deve ser interpretada como apoio à decisão e encaminhamento.

## Intervalos de confiança por bootstrap

Os intervalos foram calculados a partir das previsões salvas do ensemble no teste congelado, com 1.000 reamostragens e seed 42.

| Métrica | Estimativa bootstrap | IC 95% |
|---|---:|---:|
| AUROC binária | 0,8670 | 0,8477–0,8864 |
| Sensibilidade binária | 0,8365 | 0,7926–0,8765 |
| Especificidade binária | 0,7349 | 0,7102–0,7596 |
| F1 binário | 0,5720 | 0,5319–0,6086 |
| AUROC macro multiclasse | 0,9018 | 0,8886–0,9139 |
| F1 macro multiclasse | 0,4340 | 0,3945–0,4725 |

O arquivo estruturado com os valores completos está em [`QUICK_CPU_BOOTSTRAP_CI.json`](./QUICK_CPU_BOOTSTRAP_CI.json). Os resultados do teste estão em `ml_artifacts/ham10000/quick_cpu/ensemble/test_metrics.json`, e as previsões utilizadas no bootstrap estão em `ml_artifacts/ham10000/quick_cpu/ensemble/test_predictions.npz`.

## Classes raras e limitações de interpretação

A distribuição do teste permanece desbalanceada. As classes df e vasc possuem, respectivamente, 10 e 29 imagens no teste congelado. Portanto, métricas por classe dessas categorias apresentam elevada incerteza amostral e não devem ser interpretadas como evidência robusta de desempenho clínico. A classe nv concentra a maior parte dos exemplos e pode influenciar métricas agregadas, especialmente acurácia e F1 ponderado.

O HAM10000 não fornece rótulos validados de tom de pele ou classificação de Fitzpatrick e não deve sustentar afirmações de equidade para pessoas negras ou para qualquer subgrupo tonal. Uma análise de viés adequada requer validação externa com anotações tonais autorizadas, como DDI ou outro conjunto compatível, além de protocolo explícito para desempenho por subgrupo.

## Próxima etapa científica

A versão final recomendada deve ser treinada na máquina com GPU disponível, usando resolução de 224×224, mais épocas, descongelamento progressivo do backbone após a fase inicial, seleção de hiperparâmetros exclusivamente na validação, avaliação única no teste congelado e repetição dos intervalos de confiança. A rodada rápida permanece versionada como evidência de integração e como referência de reprodutibilidade do pipeline.
