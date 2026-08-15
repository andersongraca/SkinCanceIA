# Auditoria inicial — SkinCancerCADDermoIA

## Repositório

O repositório público `andersongraca/SkinCancerCADDermoIA` está na branch `master`, com dois commits e estrutura TypeScript/Node.js/Express/tRPC, Drizzle/MySQL e React no cliente. O front-end não será alterado nesta etapa.

## Estado real do back-end

A documentação descreve CNN, ViT, modelo híbrido, ensemble, métricas e heatmaps, mas `server/services/ClassificationModels.ts` contém apenas implementações simuladas: `classify` usa espera artificial e números aleatórios; `generateHeatmap` apenas registra uma mensagem e retorna `true`. O modelo híbrido combina as confianças simuladas com pesos fixos de 0,5/0,5; o ensemble calcula média e votação sobre resultados simulados.

`server/services/ClassificationService.ts` instancia os quatro modelos com métricas fixas e plausivelmente inventadas para demonstração. `classifyImage` executa todos os modelos, mas não há carregamento de pesos, pré-processamento real, inferência, calibração, validação ou avaliação. `generateAllHeatmaps` devolve caminhos esperados sem confirmar a criação dos arquivos.

`server/routers.ts` expõe apenas histórico/consulta de diagnósticos e leitura de métricas. Não há endpoint de upload, classificação, persistência de imagem/diagnóstico após inferência ou geração de heatmap. O bootstrap Express também não configura multipart.

O esquema Drizzle já possui tabelas para imagens dermatoscópicas, diagnósticos e métricas. A tabela `diagnoses` armazena classificação, confiança, resultados CNN/ViT/híbrido, caminho de heatmap e versão do modelo; entretanto, as funções de inserção existentes em `server/db.ts` ainda não estão conectadas às rotas e ao pipeline.

As dependências atuais incluem TensorFlow.js e MobileNet para uso potencial no ecossistema JavaScript, mas não incluem uma stack de treinamento/inferência Python/PyTorch nem bibliotecas de transformers ou processamento de imagens no servidor. A estratégia técnica deverá decidir entre inferência nativa em Node/TensorFlow.js, um serviço Python separado ou uma abordagem híbrida, considerando implantação e disponibilidade de pesos.

## Exigências dos documentos

O parecer de qualificação considera relevante a hibridização CNN–ViT, Ensemble Learning e XAI, mas exige atenção à generalização para tons de pele mais escuros e apresentações acrais, dada a predominância de peles claras nos conjuntos HAM10000/ISIC. Também exige correção das duplicações e revisão textual do documento, que serão tratadas como contexto, não como alteração do front-end.

A dissertação propõe comparar CNNs e ViTs, desenvolver arquitetura híbrida, usar ensemble, balanceamento de dados, estratégias de generalização, métricas clínicas e Grad-CAM/XAI. O sistema deverá evitar alegações de desempenho sem experimentos rastreáveis; as métricas fixas atualmente exibidas não devem ser tratadas como resultados científicos.

## Riscos e decisões pendentes

1. Confirmar quais pesos/modelos e qual conjunto de dados estão disponíveis; não é seguro presumir treinamento ou desempenho sem os arquivos.
2. Definir binário benigno/maligno ou multiclasses HAM10000 e o mapeamento clínico correspondente.
3. Definir estratégia de inferência compatível com o ambiente de implantação.
4. Definir protocolo de divisão por paciente/imagem, balanceamento, calibração, métricas por classe, análise de subgrupos e validação externa.
5. Preservar os contratos usados pelo front-end, alterando somente serviços, rotas e integração de dados no back-end.

## Contratos observados no front-end

`DiagnosisPage.tsx` coordena as abas de upload, resultados, histórico e métricas. `UploadTab.tsx` aceita JPEG/PNG de até 10 MB, mas o botão de análise ainda aguarda dois segundos e apenas dispara callbacks locais; não envia o arquivo ao servidor. `ResultsTab.tsx` exibe objetos mockados com `finalClassification`, `finalConfidence`, resultados CNN/ViT/híbrido/ensemble, tempos de inferência e áreas reservadas para quatro heatmaps. `MetricsTab.tsx` também usa métricas mockadas. Portanto, o back-end pode ser finalizado de forma independente, mas a visualização atual não consumirá automaticamente os resultados reais enquanto não houver uma integração de front-end — que ficará fora do escopo solicitado nesta fase.

A árvore versionada contém os componentes de diagnóstico, e o único branch remoto relevante observado é `master`. A cópia local está limpa e foi usada somente para leitura.
