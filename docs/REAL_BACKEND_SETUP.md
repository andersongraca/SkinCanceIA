# SkinCanceIA — backend real e autenticação

## Estado atual

O projeto foi configurado para executar uma análise de imagem real, sem usar o resultado simulado do modo de demonstração por padrão. O ambiente Python reconhece a NVIDIA GeForce GTX 1650 com 4 GB de VRAM, PyTorch 2.6.0 com CUDA 12.4 e `cuda_available=true`.

O conjunto HAM10000 foi baixado da fonte oficial do Harvard Dataverse, preparado com divisão agrupada por lesão e validado com 10.015 imagens e zero imagens ausentes. Os artefatos ficam fora do Git por causa do tamanho e dos termos de uso do dataset.

| Artefato | Caminho |
|---|---|
| CNN | `ml_artifacts/ham10000/cnn/best.pt` |
| ViT | `ml_artifacts/ham10000/vit/best.pt` |
| Híbrido | `ml_artifacts/ham10000/hybrid/best.pt` |
| Referência de qualidade/OOD | `ml_artifacts/ham10000/quality_reference.json` |
| Pesos do ensemble | `ml_artifacts/ham10000/ensemble/weights.json` |
| Métricas do teste | `ml_artifacts/ham10000/ensemble/test_metrics.json` |

Os checkpoints atuais são uma rodada inicial de uma época, com backbone congelado, imagem de 160 px e batch 4. Eles comprovam o pipeline e não devem ser tratados como um modelo clínico validado. No teste congelado, o ensemble obteve AUROC binário de aproximadamente 0,860, sensibilidade de aproximadamente 0,823 e especificidade de aproximadamente 0,732. Essas métricas são experimentais e não substituem avaliação clínica externa, validação prospectiva ou decisão médica.

## Banco local

O MariaDB foi instalado no computador e inicializado sem exigir privilégios administrativos. A instância roda em modo usuário na porta `3307`, com dados em `runtime/mariadb-data`. O banco `skincancer` e as tabelas `users`, `dermatological_images`, `diagnoses` e `model_metrics` foram criados pelas migrações Drizzle.

Para iniciar o MariaDB após reiniciar o computador, abra um terminal na pasta do projeto e execute:

```powershell
& "C:\Program Files\MariaDB 12.3\bin\mariadbd.exe" `
  --datadir="C:\Users\Gabriel\Documents\SkinCancerTensorFlow\runtime\mariadb-data" `
  --port=3307 --bind-address=127.0.0.1 --console
```

Mantenha esse terminal aberto. O `.env` já contém a `DATABASE_URL` local e um `JWT_SECRET` gerado automaticamente; não copie esse arquivo para o Git nem o envie por mensagem.

## Iniciar a aplicação no Windows

Em um segundo terminal, execute:

```powershell
cd "C:\Users\Gabriel\Documents\SkinCancerTensorFlow"
$env:Path = "C:\Program Files\nodejs;" + $env:Path
$env:NODE_ENV = "development"
pnpm exec tsx watch server/_core/index.ts
```

A aplicação ficará disponível em `http://localhost:3000`. O script `pnpm dev` original usa a sintaxe de variável de ambiente do Unix e pode falhar no PowerShell do Windows; o comando acima é a forma compatível com este computador.

## OAuth real ainda pendente

O bypass de demonstração foi removido como comportamento padrão. O arquivo `.env` mantém `VITE_LOCAL_DEMO_MODE=false`, e a aplicação agora falha de forma explícita quando OAuth não está configurado. O callback OAuth também valida o state e o nonce em cookie antes de trocar o código, evitando aceitar um callback forjado.

Para habilitar o login real, preencha somente no `.env` local os valores oficiais fornecidos pela configuração do projeto Manus:

```dotenv
VITE_APP_ID=...
OAUTH_SERVER_URL=...
VITE_OAUTH_PORTAL_URL=...
OWNER_OPEN_ID=...
OWNER_NAME=...
```

Depois reinicie o servidor e o Vite. Não use valores inventados, não coloque segredos no código e não envie tokens ou senhas por chat. Sem esses três valores OAuth, o sistema pode executar os componentes científicos localmente, mas não pode criar uma sessão de usuário real.

## Validações concluídas

A compilação TypeScript passou, o build de produção passou, os testes Vitest passaram com quatro testes, o callback OAuth com state inválido retornou HTTP 403 e o smoke test TypeScript–Python executou triagem, classificação dos três componentes e geração dos três heatmaps. A referência de qualidade também foi calculada a partir dos grupos de treinamento e validação.

> A aplicação é um protótipo de pesquisa. Uma classificação “malignant” ou “benign” não é diagnóstico médico e não deve orientar tratamento, alta ou atraso na consulta de um dermatologista.

## Referências

[1]: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T "Harvard Dataverse — HAM10000, DOI 10.7910/DVN/DBW86T"
