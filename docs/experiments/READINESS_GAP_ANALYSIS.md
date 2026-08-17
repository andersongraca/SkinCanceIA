# Análise de prontidão e lacunas

## Diagnóstico executivo

O projeto está **funcional como protótipo científico integrado**. O núcleo de aprendizado de máquina, a triagem OOD, a explicabilidade e a integração TypeScript–Python foram implementados. Os checkpoints locais CNN, ViT e híbrido existem, o ensemble foi recalculado e os testes automatizados continuam aprovados.

O projeto ainda não deve ser descrito como produto clínico pronto. Os bloqueios restantes são de ambiente de produção, validação científica final e publicação. Nesta sessão também foi corrigido um problema de execução: o servidor de desenvolvimento não resolvia `@shared/const` porque faltava um `tsconfig.json` raiz; o arquivo foi adicionado e o servidor passou a iniciar na porta 3000.

## Estado por área

| Área | Estado atual | Classificação |
|---|---|---|
| CNN ResNet-50 | Checkpoint treinado e avaliado no HAM10000 | Concluída para protótipo |
| ViT | Checkpoint treinado e avaliado no HAM10000 | Concluída para protótipo |
| Híbrido CNN–ViT | Checkpoint treinado e avaliado no HAM10000 | Concluída para protótipo |
| Ensemble | Pesos calibrados na validação e métricas de teste salvas | Concluída para protótipo |
| Calibração e incerteza | Temperatura, TTA, entropia e abstensão implementadas | Concluída para protótipo |
| Heatmaps | Grad-CAM, tokens, atenção e mapa híbrido produzidos | Concluída para protótipo |
| Gate OOD | HAM10000 aceito; carro e cabeça/cabelo rejeitados | Smoke test concluído |
| TypeScript e tRPC | Rotas, serviço Python, autorização e build funcionando | Concluída localmente |
| Servidor de desenvolvimento | Inicia após correção do `tsconfig.json` raiz | Concluída localmente |
| Banco | Schema e migrações verificadas, mas sem `DATABASE_URL` | Pendente de ambiente |
| Armazenamento persistente | Código preparado, credenciais ausentes | Pendente de ambiente |
| Teste visual autenticado | Browser da sessão indisponível | Pendente de execução visual |
| GitHub | Commit local `412a3f4` pronto, conector desabilitado | Bloqueado por permissão |

## Pendências críticas operacionais

### Banco de dados

`DATABASE_URL` não está configurada nesta sessão. É necessário provisionar MySQL/TiDB, aplicar as migrações e executar `scripts/seed_model_metrics.ts`. O critério de conclusão é conseguir carregar as quatro linhas de métricas pela rota real, persistir um diagnóstico e recuperar seu histórico após reiniciar o servidor.

### Armazenamento persistente

As imagens e heatmaps usam filesystem local somente no modo de desenvolvimento. Em produção, o código exige armazenamento persistente configurado e falha explicitamente quando ele não existe. É necessário configurar o serviço de armazenamento, testar upload, materialização temporária para inferência, remoção do temporário e persistência das URLs dos heatmaps.

### Autenticação e validação no navegador

As rotas protegidas respondem `401 UNAUTHORIZED` sem sessão, e a interface contém o fluxo explícito de autenticação. Ainda falta executar o teste visual em um navegador com sessão válida, verificando upload, estado de carregamento, resultado aceito, rejeição OOD, erro, ausência de métricas, histórico vazio e histórico preenchido.

### Publicação

O projeto está na branch local `feat/scientific-ml-backend`, commit `412a3f4`, com árvore de trabalho limpa. O GitHub permanece desabilitado na sessão; por isso, o push não foi concluído. É necessário habilitar o conector GitHub e executar `git push -u origin feat/scientific-ml-backend`, ou baixar o pacote-fonte seguro e executar esse comando em um ambiente com credencial de escrita.

## Pendências científicas

A rodada disponível foi executada em CPU com duas épocas, resolução 160×160 e backbone congelado. Para a versão final da dissertação, recomenda-se retreinar com GPU, 224×224, mais épocas, descongelamento progressivo, ajuste de hiperparâmetros e múltiplas sementes. O ensemble e os intervalos de confiança devem ser recalculados após o retreinamento.

O HAM10000 possui desbalanceamento severo, suporte de teste baixo para `df` e `vasc`, ausência de `patient_id` no metadata utilizado e ausência de rótulo validado de tom de pele/Fitzpatrick. Não é permitido afirmar equidade para peles negras ou desempenho clínico geral somente com essa base. É necessária validação externa autorizada com anotação tonal confiável, análise por subgrupo e relato de suporte e intervalos.

Os exemplos de carro, cabeça/cabelo e imagem uniforme comprovam apenas um smoke test do gate de domínio. Uma avaliação científica deverá incluir um conjunto OOD externo documentado, com objetos, rostos, cabelos, fotografias clínicas não dermatoscópicas, desfoque, iluminação extrema e imagens de outras modalidades.

Os heatmaps são explicações aproximadas. Sem máscaras clínicas ou anotação de localização, não devem ser apresentados como prova de causalidade, delimitação anatômica ou garantia de que o modelo ignorou artefatos.

## Ordem recomendada de fechamento

A ordem prática é configurar banco e armazenamento persistente; executar seed e fluxo completo de upload, classificação e histórico; validar a interface com sessão autenticada; treinar a versão científica final na GPU; executar validação externa e análise de subgrupos; recalcular ensemble, calibração e bootstrap; atualizar a dissertação; habilitar o conector GitHub; e publicar a branch segura.

Até que essas etapas sejam concluídas, a formulação correta é: **backend científico integrado e testado localmente, pronto para a etapa de implantação e validação científica final**.
