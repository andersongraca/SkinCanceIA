# GitHub Pages

O workflow `.github/workflows/deploy-pages.yml` publica a interface React como um artefato estático no GitHub Pages quando há push na branch `feat/scientific-ml-backend` ou quando o workflow é acionado manualmente.

A URL esperada é:

```text
https://andersongraca.github.io/SkinCanceIA/
```

## Limitação arquitetural

O GitHub Pages serve apenas arquivos estáticos. Ele não executa o servidor Express/tRPC, o Python de inferência, o banco MySQL, o armazenamento persistente nem os checkpoints. Por isso, a página publicada é uma demonstração da interface e não executa a classificação real enquanto não houver um backend HTTPS separado.

O cliente aceita a variável `VITE_TRPC_API_URL`. Para uma implantação integrada, o workflow ou o ambiente de build deve fornecer uma URL HTTPS de um backend que exponha o endpoint tRPC compatível:

```text
VITE_TRPC_API_URL=https://seu-backend.example.com/api/trpc
```

Não coloque tokens, `DATABASE_URL`, chaves de armazenamento ou caminhos de checkpoints em variáveis expostas ao frontend. Segredos devem permanecer no backend.

## Ativação no repositório

Depois do push do workflow, abra **Settings → Pages** no repositório e selecione **GitHub Actions** como fonte, caso o GitHub ainda não tenha habilitado Pages automaticamente. O workflow precisa das permissões `pages: write` e `id-token: write`, já declaradas no arquivo.

A publicação do Pages não substitui a implantação do backend científico. Ela fornece a camada visual pública; a classificação real continua dependendo de um servidor seguro separado.
