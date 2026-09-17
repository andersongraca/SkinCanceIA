# Auditoria pré-apresentação do SkinCancerCADDermoIA

**Data:** 17 de setembro de 2026

**Autor:** Manus AI

**Branch auditado:** `feat/scientific-ml-backend`

**Commit funcional:** `cb03a0e`

## Conclusão

O sistema está **operacional para uma demonstração acadêmica local**. A auditoria executou checagem TypeScript, testes de backend, build de produção, testes Python, inferência com os três checkpoints, combinação do Ensemble, geração dos quatro mapas de explicabilidade, upload pela rota local, histórico em memória e carregamento das métricas reais do HAM10000.

A auditoria identificou e corrigiu um defeito visual importante. Os mapas usavam opacidade fixa e, por isso, coloriam pixels sem saliência. Isso podia aparentar ativação fora da lesão. O renderizador agora usa opacidade proporcional à saliência e mantém pixels externos **idênticos à imagem original**. O teste quantitativo confirmou diferença máxima igual a zero fora da saliência nos quatro mapas.

O resultado demonstra o funcionamento técnico do protótipo. Ele **não constitui validação clínica**, não prova causalidade e não autoriza uso diagnóstico.

## Resultado dos testes

| Verificação | Resultado | Evidência principal |
|---|---:|---|
| TypeScript | Aprovado | `tsc --noEmit` sem erros |
| Vitest | Aprovado | 9 testes aprovados |
| Build de produção | Aprovado | Vite e esbuild concluídos |
| Testes Python | Aprovado | 12 aprovados e 3 ignorados |
| Inferência real | Aprovado | CNN, ViT, Hybrid e Ensemble executados |
| Heatmaps | Aprovado | Quatro arquivos PNG, todos em 600 × 450 |
| Fundo fora da saliência | Aprovado | Diferença máxima de pixel igual a 0 |
| Upload e classificação local | Aprovado | Resposta `classified` |
| URLs públicas dos mapas | Aprovado | Quatro URLs `/api/ml-artifacts/...` |
| Histórico local | Aprovado | Um diagnóstico recuperado após a execução |
| Métricas da interface | Aprovado | Quatro modelos, 1.527 amostras cada |
| Triagem OOD funcional | Aprovado | Imagem não dermatológica rejeitada |

Os três testes Python ignorados dependem de uma cópia preparada do dataset HAM10000 e de ativos OOD públicos que não fazem parte do repositório Git. Eles não representam falha de código. O build emitiu somente um aviso de bundle JavaScript maior que 500 kB; esse aviso afeta otimização de carregamento, não o funcionamento da apresentação.

## Auditoria dos mapas de explicabilidade

A imagem auditada foi `ISIC_0027419.jpg`, com 600 × 450 pixels. O gate de segmentação ISIC foi carregado em modo `balanced`, com limiar 0,50 e kernel morfológico 5 × 5. A área pós-processada ocupou aproximadamente 22,0% da imagem de entrada do modelo.

| Mapa | Dimensão | Fração com saliência | Desvio-padrão da saliência | Diferença máxima fora da saliência | Resultado |
|---|---:|---:|---:|---:|---:|
| CNN — Grad-CAM | 600 × 450 | 10,22% | 23,56 | 0 | Aprovado |
| ViT — atribuição de tokens | 600 × 450 | 22,42% | 5,94 | 0 | Aprovado |
| Hybrid — mapa combinado | 600 × 450 | 15,33% | 16,76 | 0 | Aprovado |
| Ensemble — mapa agregado | 600 × 450 | Composição dos três mapas | — | 0 | Aprovado |

A inspeção visual confirmou que o fundo não é mais pintado artificialmente. O Grad-CAM e o Ensemble destacam sub-regiões dentro da lesão pigmentada. O ViT produz uma atribuição mais esparsa. O Hybrid produz uma região mais ampla. Essa diferença é esperada porque os métodos usam representações distintas.

> Os heatmaps mostram evidência usada pelos modelos. Eles não são máscaras clínicas da lesão e não devem ser apresentados como prova de que o modelo “olhou corretamente” em sentido causal.

O localizador auxiliar treinado com ISIC 2016 é útil como barreira visual, mas sua máscara é imperfeita.[2] Um refinamento cromático experimental foi avaliado e descartado porque selecionou somente uma pequena região escura e omitiu grande parte da lesão visível. Nenhum refinamento sem validação foi integrado.

## Inferência auditada

A imagem HAM10000 foi aceita pela triagem com escore de qualidade 0,386 e escore OOD 0,781, abaixo do limiar 196,230. O Ensemble retornou classe binária `malignant`, confiança 85,82%, entropia preditiva 0,7329 e variância TTA 0,001667. O Ensemble não recomendou abstenção com os limiares operacionais usados.

A CNN individual ultrapassou o limiar de entropia e recomendou abstenção. ViT e Hybrid não recomendaram abstenção. Com `ML_ENSEMBLE_ABSTAIN_VOTES=2`, uma única recomendação individual não bloqueia o resultado agregado. Esse comportamento deve ser explicado como **regra operacional configurável**, não como certeza clínica.

## Dados e métricas científicas

O manifesto registra 10.015 imagens HAM10000, 7.470 grupos de lesão e divisão por grupos com seed 42. O conjunto de teste contém 1.527 imagens. As contagens do manifesto, as matrizes de confusão e o arquivo de métricas são consistentes. Os pesos do Ensemble somam 1 e foram selecionados na validação: CNN 0,10, ViT 0,55 e Hybrid 0,35. O HAM10000 está documentado no projeto sob licença CC BY-NC 4.0 para uso acadêmico não comercial.[1]

| Modelo | Acurácia binária | Sensibilidade | Especificidade | AUROC | AUPRC | ECE |
|---|---:|---:|---:|---:|---:|---:|
| CNN | 0,7302 | 0,7333 | 0,7294 | 0,8293 | 0,5332 | 0,0544 |
| ViT | 0,7256 | 0,8533 | 0,6944 | 0,8500 | 0,5565 | 0,0456 |
| Hybrid | 0,7439 | 0,7967 | 0,7311 | 0,8370 | 0,4833 | 0,2269 |
| Ensemble | **0,7498** | **0,8233** | **0,7319** | **0,8600** | **0,5709** | **0,0706** |

O ECE do Hybrid, 0,2269, indica calibração pior do que a dos demais componentes. Na apresentação, priorize as métricas do Ensemble e não descreva o Hybrid isolado como bem calibrado.

## Triagem fora do domínio

Uma imagem real não dermatológica do sistema operacional foi recusada com os motivos `outside_dermoscopy_domain`, `quality_score_below_minimum` e `resolution_below_minimum`. O escore OOD foi 2.004,42, acima do limiar 196,23. Esse teste confirma o funcionamento da barreira, mas não demonstra que todo carro, régua, rosto ou outro objeto será rejeitado. Uma afirmação universal exigiria um conjunto OOD amplo, rotulado e independente.

## Rotas e modo local

A auditoria executou a mesma rota usada pela interface. O upload retornou uma URL local; a classificação retornou quatro URLs de heatmap; o histórico recuperou o diagnóstico; e a aba de métricas carregou CNN, ViT, Hybrid e Ensemble com 1.527 amostras.

Com o banco desligado, imagem, diagnóstico e histórico usam fallback local em memória. Os avisos de banco indisponível são esperados nesse modo. O histórico é perdido ao reiniciar o servidor. Para a apresentação, isso é suficiente se a demonstração ocorrer em uma única sessão.

## Configuração recomendada para a apresentação

Use `ML_LESION_GATE_MODE=balanced`, entropia 0,75, variância TTA 0,03 e dois votos para abstenção. Reinicie o servidor depois de alterar variáveis e atualize o navegador com `Ctrl + F5`. Uma execução real auditada levou aproximadamente 25 segundos: 13 segundos para classificação e 12 segundos para os mapas. A barra da interface é estimada; ela não representa telemetria enviada pelo backend.

Não use `permissive` por padrão na apresentação. Esse modo inclui mais contexto e pode aumentar a área da máscara. Use-o somente para imagens com pelos ou iluminação irregular e explique a alteração.

## Correções publicadas

O commit `cb03a0e` foi enviado para `feat/scientific-ml-backend`. Ele aplica transparência proporcional à saliência, zera estritamente o mapa fora do gate, elimina resíduos de quantização, adiciona testes de invariância visual e inclui scripts reproduzíveis de auditoria. Os arquivos XAI da pasta do VS Code têm o mesmo hash SHA-256 dos arquivos publicados.

## Limitações que devem ser declaradas

O protótipo foi treinado e testado no domínio dermatoscópico do HAM10000. As métricas são de avaliação interna congelada e não representam validação clínica prospectiva. O gate ISIC reduz ativações de fundo, mas não garante segmentação perfeita. Os mapas não provam causalidade. A triagem OOD funcional não equivale a cobertura universal de objetos externos. O sistema deve ser apresentado como ferramenta acadêmica de apoio e pesquisa.

## Referências

[1]: https://doi.org/10.7910/DVN/DBW86T "HAM10000 Dataset, Harvard Dataverse"
[2]: https://challenge.isic-archive.com/data/ "ISIC Challenge Datasets"
