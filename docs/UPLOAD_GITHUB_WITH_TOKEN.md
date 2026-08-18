# Publicar no GitHub usando token fine-grained

Este guia publica a branch `feat/scientific-ml-backend` no repositório `https://github.com/andersongraca/SkinCanceIA` sem colocar o token na URL, no histórico do shell ou em arquivos do projeto.

## Token recomendado

Crie um token fine-grained em https://github.com/settings/personal-access-tokens/new com validade de 7 dias, acesso somente ao repositório `SkinCanceIA` e permissão `Contents: Read and write`. A permissão `Metadata: Read-only` é normalmente automática. Não habilite permissões administrativas ou de workflow sem necessidade.

## Caso você já tenha a pasta do projeto

Abra Git Bash, PowerShell ou Terminal na pasta que contém o diretório `.git` e execute:

```bash
git remote set-url origin https://github.com/andersongraca/SkinCanceIA.git
git checkout feat/scientific-ml-backend
git status
git push -u origin feat/scientific-ml-backend
```

Quando aparecerem os prompts, informe:

```text
Username: andersongraca
Password: cole o token fine-grained quando solicitado
```

O token não aparecerá enquanto for digitado ou colado no campo de senha. Não use `git remote set-url origin https://TOKEN@github.com/...` e não execute `git config credential.helper store`, porque essas formas podem deixar a credencial exposta.

Se a branch ainda não existir localmente, use:

```bash
git checkout -B feat/scientific-ml-backend
git push -u origin feat/scientific-ml-backend
```

## Caso você tenha baixado o ZIP atualizado

Extraia `SkinCancerCADDermoIA_current_3478255.zip`, abra o terminal dentro da pasta extraída e execute:

```bash
git init
git checkout -B feat/scientific-ml-backend
git remote add origin https://github.com/andersongraca/SkinCanceIA.git
git add .
git commit -m "feat: publish scientific skin cancer backend"
git push -u origin feat/scientific-ml-backend
```

Use o mesmo usuário e token nos prompts do Git. O pacote não contém dataset bruto, checkpoints, `node_modules`, arquivos `.env` ou credenciais.

## Verificação

Depois do push, confirme a branch com:

```bash
git ls-remote --heads origin feat/scientific-ml-backend
```

O resultado deve mostrar um hash seguido de `refs/heads/feat/scientific-ml-backend`. A branch também pode ser aberta em https://github.com/andersongraca/SkinCanceIA/tree/feat/scientific-ml-backend.

## Erros comuns

`403` normalmente significa que o token não tem `Contents: Read and write`, não está limitado ao repositório correto, pertence a outro proprietário ou foi revogado. `Authentication failed` geralmente significa que o token foi digitado no campo de usuário em vez do campo de senha, ou expirou. Não envie o token para diagnóstico; envie apenas a mensagem de erro sem valores secretos.

Após confirmar o push, revogue o token de 7 dias em https://github.com/settings/personal-access-tokens para encerrar o acesso temporário.
