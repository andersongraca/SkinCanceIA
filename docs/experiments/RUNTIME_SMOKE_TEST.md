# Smoke test operacional local

## Ambiente

O servidor foi iniciado em modo de desenvolvimento na porta 3000 com os três checkpoints HAM10000, a referência OOD e os pesos do ensemble configurados por variáveis de ambiente. O ambiente não possui `DATABASE_URL`, GPU NVIDIA, `OAUTH_SERVER_URL` nem armazenamento persistente; por isso, os testes abaixo cobrem o comportamento local sem sessão autenticada e sem persistência de produção.

| Verificação | Resultado observado |
|---|---|
| `GET /` | HTTP 200, `text/html`, página de entrada retornada |
| `GET /api/trpc/auth.me` | HTTP 200, sessão anônima retornada |
| `GET /api/trpc/metrics.getAllMetrics` | HTTP 200, lista vazia por ausência de banco |
| `GET /api/trpc/diagnosis.getHistory` sem sessão | HTTP 401, código `UNAUTHORIZED` |
| Servidor de desenvolvimento | Iniciou após adicionar `tsconfig.json` raiz com aliases herdados |

A primeira tentativa de iniciar o watcher falhou porque o projeto não possuía `tsconfig.json` raiz e o alias `@shared/const` não era resolvido pelo `tsx`. A correção adicionou um `tsconfig.json` que estende `tsconfig.backend.json`, preservando os aliases `@shared/*`, `server/*` e `@/*`. O `pnpm check`, os testes Vitest e o build de produção permaneceram aprovados após a alteração.

A validação visual no navegador não foi executada porque o navegador da sessão não estava disponível. A resposta HTTP confirma que o servidor e as rotas públicas estão vivos, mas não substitui a revisão visual autenticada no navegador.
