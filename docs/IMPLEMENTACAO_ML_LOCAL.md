# Implementação local do detector SkinCancerCADDermoIA

## Escopo da rodada

Esta rodada conectou o backend TypeScript aos modelos reais de aprendizado de máquina, preservando os componentes da interface existentes. O fluxo agora valida a elegibilidade da imagem, executa inferência Python com os checkpoints CNN, ViT e híbrido, combina os resultados com pesos escolhidos na validação e pode gerar explicações aproximadas por Grad-CAM e atribuição de tokens.

> O sistema é uma ferramenta de apoio à pesquisa e triagem computacional. Ele não realiza diagnóstico autônomo, não substitui avaliação dermatológica e não deve ser usado para decisões clínicas sem validação externa e supervisão profissional.

## Dados utilizados

O HAM10000 foi baixado da versão 4.0 do Harvard Dataverse, identificada pelo DOI `10.7910/DVN/DBW86T`. A fonte informa 10.015 imagens dermatoscópicas, sete categorias diagnósticas e agrupamento por `lesion_id`; as duas partes ZIP foram verificadas pelos MD5 oficiais: `4639bfa73ab251610530a97c898e6e46` e `da43d6cc50f6613013be07e8986b384b`. O metadata oficial contém 10.015 observações e foi mantido fora do Git, assim como os arquivos de imagem brutos [1].

O uso desta rodada é acadêmico e não comercial, sob os termos exibidos pelo Dataverse como **Creative Commons Attribution-NonCommercial 4.0 International**. O código não redistribui os ZIPs nem os checkpoints no repositório. A atribuição da fonte deve acompanhar qualquer dissertação, relatório ou material derivado que compartilhe resultados ou material adaptado [1].

O DDI não foi baixado nem misturado ao treinamento. Sua fonte institucional exige registro individual e Research Use Agreement, restringe o uso a pesquisa pessoal não comercial, proíbe redistribuição e declara uso não clínico. Ele permanece como opção de validação externa local, condicionada ao registro e aceite do pesquisador no portal Stanford AIMI [2].

## Preparação e divisão

A preparação usa `seed=42`, remove imagens ausentes e descarta rótulos fora das sete classes previstas. A divisão é agrupada por `lesion_id`, com 15% para validação e 15% para teste, evitando que imagens da mesma lesão atravessem as partições. O resultado possui 10.015 imagens, 7.470 grupos únicos e 1.527 imagens no teste congelado. A leitura foi corrigida para aceitar tanto CSV quanto o formato tabular `.tab` publicado oficialmente.

A referência de qualidade foi construída com as imagens do HAM10000. O gate de entrada verifica decodificação, qualidade visual e distância robusta em relação ao domínio dermatoscópico de referência. Entradas OOD são retornadas como `IMAGE_NOT_ELIGIBLE` e não são encaminhadas aos classificadores.

## Treinamento executado

A rodada foi executada em CPU, sem GPU, usando pesos pré-treinados disponibilizados pelo ecossistema open source, resolução de 160×160, batch de 8, duas épocas, backbone congelado e amostragem balanceada somente no treino. Os artefatos ficam em `ml_artifacts/ham10000/`, que é explicitamente ignorado pelo Git.

| Modelo | Dispositivo | Melhor época | AUROC binária na validação | Pesos pré-treinados |
|---|---|---:|---:|---|
| CNN ResNet-50 | CPU | 2 | 0,8428 | Sim |
| ViT pequeno | CPU | 2 | 0,8576 | Sim |
| Híbrido CNN–ViT | CPU | 1 | 0,8532 | Sim |

Os pesos do ensemble desta rodada foram selecionados na validação: CNN 35%, ViT 35% e híbrido 30%. O teste não foi usado para escolher hiperparâmetros ou pesos.

## Resultado no teste congelado

Os valores abaixo são métricas da rodada experimental, não desempenho clínico geral. O conjunto é fortemente desbalanceado e possui limitações de representatividade; por isso, AUROC deve ser lida junto com AUPRC, sensibilidade, especificidade, F1, suporte por classe e intervalos de confiança.

| Modelo | Acurácia | Sensibilidade | Especificidade | F1 binário | AUROC binária | AUPRC binária |
|---|---:|---:|---:|---:|---:|---:|
| CNN ResNet-50 | 70,7% | 76,7% | 69,2% | 50,7% | 81,7% | 46,9% |
| ViT pequeno | 73,5% | 81,3% | 71,6% | 54,7% | 85,1% | 54,0% |
| Híbrido CNN–ViT | 68,0% | 88,7% | 62,9% | 52,1% | 83,0% | 48,7% |
| Ensemble | 71,0% | 85,0% | 67,6% | 53,5% | 85,0% | 55,6% |

No ensemble, o intervalo de confiança bootstrap de 95% para AUROC binária foi 0,8289–0,8709; para sensibilidade, 0,8087–0,8868; para especificidade, 0,6504–0,7028; e para F1 binário, 0,4950–0,5726. Para a classificação multiclasse, o macro-F1 foi aproximadamente 0,4257, com intervalo de 0,3885–0,4628, enquanto a AUROC macro one-vs-rest foi aproximadamente 0,9034, com intervalo de 0,8897–0,9159.

## Integração implementada

O serviço `PythonInferenceService` executa os módulos Python por processo controlado, com timeout, limite de buffer e `PYTHONPATH` definido. `ClassificationModels.ts` agora usa os checkpoints reais e possui fallback para `ml_artifacts/ham10000/{cnn,vit,hybrid}/best.pt` quando as variáveis específicas não são definidas. As rotas já existentes de upload e classificação persistem a imagem, aplicam o gate de elegibilidade, salvam o diagnóstico e tentam persistir os heatmaps sem alteração dos componentes React.

Foi adicionado `scripts/persist_real_metrics.ts`, que lê os JSONs reais da rodada e atualiza `model_metrics` quando `DATABASE_URL` estiver configurada. Em ambiente sem banco, o script registra `SKIP` e não inventa métricas.

## Execução local

```bash
cd /caminho/para/SkinCanceIA
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-ml.txt
pnpm install --frozen-lockfile
```

Para preparar e treinar uma nova rodada:

```bash
pnpm ml:prepare
pnpm ml:quality-reference
PYTHONPATH=ml python3 -m skin_cancer_ml.train \
  --data-dir /caminho/para/HAM10000/images \
  --metadata-csv /caminho/para/HAM10000_metadata.tab \
  --output-dir ml_artifacts/ham10000 \
  --model all --epochs 20 --image-size 224 --batch-size 16 \
  --freeze-backbone --unfreeze-backbone-after 5 --balanced-sampler
```

Para executar a validação e a integração:

```bash
pnpm check
pnpm test
pnpm build
PYTHONPATH=ml python3 ml/ensemble.py \
  --root ml_artifacts/ham10000 \
  --test-csv ml_artifacts/ham10000/test.csv
PYTHONPATH=ml python3 ml/bootstrap_metrics.py \
  --predictions ml_artifacts/ham10000/ensemble/test_predictions.npz \
  --output ml_artifacts/ham10000/ensemble/ENSEMBLE_BOOTSTRAP_CI.json \
  --repeats 1000 --seed 42
pnpm exec tsx scripts/persist_real_metrics.ts
```

Para iniciar o servidor local, copie `.env.example` para `.env`, ajuste os caminhos absolutos e configure um banco MySQL/TiDB se desejar histórico e métricas persistidas. A configuração mínima dos modelos é `ML_PROJECT_ROOT`, `ML_PYTHON_PATH`, `ML_DOMAIN_REFERENCE`, `ML_MODEL_VERSION` e os três caminhos de checkpoint. O armazenamento persistente de produção também exige as variáveis do serviço de storage.

## Verificações realizadas

O smoke test do serviço TypeScript aceitou uma imagem HAM10000 de 600×450 pixels, executou os três modelos e gerou os três heatmaps. Os dois ativos OOD públicos de teste foram rejeitados com `IMAGE_NOT_ELIGIBLE` e motivo `outside_dermoscopy_domain`. A verificação TypeScript passou, a suíte Vitest passou com quatro testes e o build de produção deve ser executado antes de qualquer publicação.

A rodada ainda requer validação externa autorizada, múltiplas sementes, análise por paciente quando disponível, avaliação por subgrupos de tonalidade e calibração clínica independente. O DDI é especialmente relevante para esse objetivo, mas seus termos impedem redistribuição e uso clínico; ausência de DDI ou de rótulos tonais confiáveis não pode ser convertida em alegação de equidade.

## Referências

[1]: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T "Harvard Dataverse — HAM10000, versão 4.0"

[2]: https://ddi-dataset.github.io/index.html "Stanford DDI — Diverse Dermatology Images e Research Use Agreement"
