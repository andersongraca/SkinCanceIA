# Análise de prontidão do sistema

## Estado atual

O núcleo científico está executável: CNN ResNet-50, ViT, híbrido CNN–ViT, ensemble, triagem OOD, incerteza e heatmaps funcionam com os artefatos locais. A verificação TypeScript passou, os oito testes Python passaram e o teste end-to-end direto do serviço TypeScript executou triagem, os três modelos, ensemble e heatmaps sobre uma imagem HAM10000 real.

Entretanto, o projeto ainda deve ser tratado como um **protótipo científico integrado**, e não como um sistema de produção ou dispositivo clínico pronto. A diferença principal está nos testes de integração HTTP/tRPC, na persistência real, na autenticação visível e em algumas telas que ainda usam dados simulados.

## Pendências críticas para declarar o sistema completo

| Prioridade | Pendência | Estado atual | Trabalho necessário | Critério de conclusão |
|---|---|---|---|---|
| P0 | Banco de dados | `DATABASE_URL` não estava configurada no ambiente de validação; o seed de métricas não foi executado | Aplicar as migrações, executar `scripts/seed_model_metrics.ts` e verificar `metrics.getAllMetrics` com dados reais | As quatro linhas de métricas aparecem na interface e permanecem após reinício |
| P0 | Persistência de imagens | O upload implementado grava no diretório local `runtime/uploads`; isso é adequado para teste local, mas não é armazenamento persistente de produção | Usar o armazenamento persistente configurado, salvar a chave/URL no banco e baixar temporariamente a imagem apenas durante a inferência | Upload, classificação e consulta histórica continuam funcionando depois de reiniciar o processo |
| P0 | Autenticação da interface | As mutations de upload/classificação são protegidas, mas a página de diagnóstico não mostra um fluxo explícito de login quando não há sessão | Adicionar estado de sessão, botão de entrada e mensagem clara para usuário não autenticado | Usuário não autenticado vê orientação de login; usuário autenticado consegue completar o fluxo |
| P0 | Histórico | `HistoryTab.tsx` ainda exibe três registros fictícios e não chama `diagnosis.getHistory` | Substituir `mockHistory` por `trpc.diagnosis.getHistory.useQuery`, ligar detalhes ao registro real e remover botões sem ação | A tela mostra zero registros quando vazia e os diagnósticos reais após uma classificação |
| P0 | Integração tRPC | O teste end-to-end atual chama o serviço TypeScript diretamente, sem passar por autenticação, upload, banco e HTTP | Criar testes com caller tRPC/contexto autenticado e, quando possível, teste HTTP de upload → classificação → histórico | O caminho completo é coberto por teste automatizado, incluindo rejeição OOD |

## Pendências importantes do back-end

| Área | O que falta | Observação científica ou operacional |
|---|---|---|
| Testes TypeScript | Há somente um teste Vitest de logout | Faltam testes de upload, autorização por usuário, rejeição OOD, classificação aceita, métricas e histórico |
| Modelo de dados | A migração não declara chave única para `(model_name, model_version)`, nem índices ou chaves estrangeiras para imagens/diagnósticos | O `upsert` das métricas não é plenamente idempotente sem uma restrição única; isso deve ser corrigido antes de produção |
| Armazenamento de heatmaps | Os heatmaps são gerados no filesystem e expostos por uma rota estática de runtime | Para produção, devem ser enviados ao armazenamento persistente e referenciados por URL/chave |
| Observabilidade | Não há health check específico para Python, checkpoints, referência OOD e pesos do ensemble | Adicionar verificação de inicialização, logs estruturados, latência, timeout e mensagens operacionais sem vazar caminhos sensíveis |
| Limites de entrada | O upload usa base64 dentro de uma mutation tRPC | Funciona para o protótipo, mas multipart ou upload direto ao armazenamento é mais adequado para arquivos grandes |
| Documentação | `ml/README.md` ainda não descreve todas as variáveis novas, como referência OOD e pesos do ensemble | Atualizar o procedimento de instalação e configuração para outro computador ou servidor |

## Pendências científicas antes da versão final da dissertação

O conjunto atual foi treinado com poucas épocas, resolução 160×160 e backbone congelado para permitir execução em CPU. Para uma versão experimental final, é recomendável repetir o treinamento em GPU com 224×224, descongelamento progressivo, mais épocas, múltiplas sementes e intervalos de confiança por bootstrap. Também faltam validação externa, agrupamento por paciente caso o identificador esteja disponível, análise por sexo/idade/localização, estudo de limiar clínico, curva de calibração multiclasses e conjunto OOD externo maior.

Os casos de carro, cabeça/cabelo e imagem uniforme são testes de fumaça úteis, mas não constituem uma validação abrangente do detector de domínio. O sistema deve rejeitar esses exemplos, porém não é cientificamente correto afirmar rejeição perfeita para qualquer fotografia fora do domínio sem um conjunto externo representativo.

## Pendências de interface e acabamento

A tela de resultados já recebe a resposta real e exibe qualidade, OOD, incerteza, abstensão e heatmaps. A tela de métricas já consulta a API real. Ainda é necessário validar visualmente no navegador os estados de carregamento, rejeição, erro de sessão, ausência de métricas, heatmap ausente e histórico vazio.

O HTML de entrada ainda contém placeholders de analytics que produzem avisos no build quando as variáveis não estão definidas. Isso não bloqueia o algoritmo, mas deve ser removido ou configurado antes da publicação. Também é recomendável revisar acessibilidade, textos sem acentuação em telas antigas, foco por teclado e responsividade em telas pequenas.

## Ordem recomendada de fechamento

Primeiro, configurar e migrar o banco, executar o seed de métricas e substituir o histórico simulado. Em seguida, corrigir persistência de imagens e heatmaps, adicionar o estado de login e criar os testes de integração tRPC. Depois, executar os testes no navegador em todos os estados e validar o build com as variáveis de produção. Por fim, registrar os resultados científicos finais, atualizar a documentação e publicar o branch quando a permissão de escrita estiver habilitada.

## Conclusão

O sistema **não está bloqueado no núcleo de aprendizado de máquina**, que já funciona e foi testado. Os bloqueios para considerá-lo totalmente pronto são principalmente de integração e operação: banco configurado e populado, armazenamento persistente, autenticação explícita, histórico real, testes tRPC/HTTP e validação visual da interface. Para a dissertação, ainda existe uma segunda camada de trabalho científico: treinamento mais robusto, validação externa e quantificação de incerteza com intervalos de confiança.
