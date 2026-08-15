# Handoff operacional — backend científico

## Estado final desta sessão

O núcleo científico está implementado e validado localmente: CNN ResNet-50, Vision Transformer, híbrido CNN–ViT, ensemble calibrado, triagem de qualidade/OOD, incerteza, abstensão, heatmaps, upload protegido, classificação real, métricas, autenticação explícita e histórico persistido. Nesta sessão foram treinados os três checkpoints reais em HAM10000 com resolução 160×160, backbone congelado, amostragem balanceada no treino e duas épocas por modelo.

Os checkpoints estão em `ml_artifacts/ham10000/cnn/best.pt`, `ml_artifacts/ham10000/vit/best.pt` e `ml_artifacts/ham10000/hybrid/best.pt`. A referência de domínio está em `ml_artifacts/ham10000/quality_reference.json`, com limiar OOD `196,2295`. Os pesos selecionados na validação estão em `ml_artifacts/ham10000/ensemble/weights.json`: CNN 10%, ViT 50% e híbrido 40%.

O dataset HAM10000 foi obtido da versão 4.0 do Harvard Dataverse, sob licença CC BY-NC 4.0 e uso acadêmico não comercial confirmado. As imagens brutas e os checkpoints não devem ser publicados no repositório; devem permanecer no ambiente local ou em armazenamento privado autorizado.

## Protocolo científico fechado

A divisão foi determinística com `seed=42`, aproximadamente 70%/15%/15%, estratificada e agrupada por `lesion_id`. O teste possui 1.527 imagens e permaneceu congelado para a avaliação final. A calibração de temperatura e a seleção dos pesos do ensemble usam somente a validação. O bootstrap usa as previsões congeladas do ensemble, 1.000 reamostragens e `seed=42`.

O metadata possui idade, sexo e localização, mas não possui rótulo validado de tom de pele/Fitzpatrick nem `patient_id`. Não se deve inferir tom de pele pelos pixels nem afirmar equidade para peles negras com HAM10000 isoladamente. A validação externa com um conjunto autorizado e anotação tonal confiável continua necessária.

## Métricas finais do teste

| Modelo | Macro-F1 multiclasses | AUROC multiclasses | AUROC binária | Sensibilidade | Especificidade | MCC binário | ECE binário |
|---|---:|---:|---:|---:|---:|---:|---:|
| CNN ResNet-50 | 0,3725 | 0,8748 | 0,8167 | 0,7667 | 0,6903 | 0,3707 | 0,2693 |
| ViT | 0,4311 | 0,8922 | 0,8487 | 0,7167 | 0,7938 | 0,4399 | 0,1985 |
| Híbrido CNN–ViT | 0,3957 | 0,8853 | 0,8465 | 0,6533 | 0,8289 | 0,4336 | 0,0370 |
| Ensemble | **0,4748** | **0,9096** | **0,8607** | **0,7167** | **0,8052** | **0,4537** | **0,0795** |

O ensemble apresentou acurácia multiclasses de 0,6398, balanced accuracy de 0,6009, AUPRC multiclasses de 0,5543 e Brier score de 0,4865. Na tarefa binária, apresentou acurácia de 0,7878, balanced accuracy de 0,7609, precisão de 0,4736, F1 de 0,5703 e AUPRC de 0,5946.

Os intervalos de confiança de 95% estão em `docs/experiments/ENSEMBLE_BOOTSTRAP_CI.json`: AUROC binária 0,8398–0,8814, sensibilidade 0,6610–0,7693, especificidade 0,7831–0,8273 e F1 binário 0,5261–0,6131. O relatório completo está em `docs/experiments/EXPERIMENT_REPORT.md`.

## Comandos de instalação e preparação

```bash
pip install -r requirements-ml.txt
pnpm install

pnpm ml:prepare
python3 ml/audit_ham10000.py \
  --metadata data/metadata/HAM10000_metadata.csv \
  --split-dir ml_artifacts/ham10000 \
  --output docs/experiments/HAM10000_BIAS_AUDIT.json

pnpm ml:quality-reference
```

## Treinamento recomendado na máquina com GPU

A rodada atual é um smoke test científico executável em CPU. Para a versão experimental final, recomenda-se treinar com GPU, 224×224 px, mais épocas, descongelamento progressivo e múltiplas sementes:

```bash
PYTHONPATH=ml python3 -m skin_cancer_ml.train \
  --data-dir /caminho/para/imagens \
  --metadata-csv /caminho/para/HAM10000_metadata.csv \
  --output-dir ml_artifacts/ham10000 \
  --model all \
  --epochs 20 \
  --image-size 224 \
  --batch-size 16 \
  --balanced-sampler
```

Após os três checkpoints, a avaliação e o ensemble são recalculados sem usar o teste para ajuste:

```bash
PYTHONPATH=ml python3 ml/evaluate_test.py \
  --checkpoint ml_artifacts/ham10000/cnn/best.pt \
  --test-csv ml_artifacts/ham10000/test.csv \
  --batch-size 32

PYTHONPATH=ml python3 ml/ensemble.py \
  --root ml_artifacts/ham10000 \
  --test-csv ml_artifacts/ham10000/test.csv \
  --batch-size 32

PYTHONPATH=ml python3 ml/bootstrap_metrics.py \
  --predictions ml_artifacts/ham10000/ensemble/test_predictions.npz \
  --output docs/experiments/ENSEMBLE_BOOTSTRAP_CI.json \
  --repeats 1000 --seed 42
```

## Configuração do servidor TypeScript

Configure fora do repositório as variáveis `DATABASE_URL`, `BUILT_IN_FORGE_API_URL`, `BUILT_IN_FORGE_API_KEY`, `ML_PROJECT_ROOT`, `ML_PYTHON_PATH`, `ML_CNN_CHECKPOINT`, `ML_VIT_CHECKPOINT`, `ML_HYBRID_CHECKPOINT`, `ML_MODEL_VERSION`, `ML_DOMAIN_REFERENCE`, `ML_ENSEMBLE_WEIGHTS_PATH` e `ML_INFERENCE_TIMEOUT_MS`.

Um exemplo local, sem gravar segredos em arquivo versionado, é:

```bash
export ML_PROJECT_ROOT=/caminho/para/SkinCancerCADDermoIA
export ML_PYTHON_PATH=/usr/bin/python3
export ML_CNN_CHECKPOINT=$ML_PROJECT_ROOT/ml_artifacts/ham10000/cnn/best.pt
export ML_VIT_CHECKPOINT=$ML_PROJECT_ROOT/ml_artifacts/ham10000/vit/best.pt
export ML_HYBRID_CHECKPOINT=$ML_PROJECT_ROOT/ml_artifacts/ham10000/hybrid/best.pt
export ML_DOMAIN_REFERENCE=$ML_PROJECT_ROOT/ml_artifacts/ham10000/quality_reference.json
export ML_ENSEMBLE_WEIGHTS_PATH=$ML_PROJECT_ROOT/ml_artifacts/ham10000/ensemble/weights.json
export ML_MODEL_VERSION=ham10000-160px-epoch2
export ML_INFERENCE_TIMEOUT_MS=600000
```

O servidor materializa temporariamente imagens persistidas durante a inferência e remove os arquivos temporários ao final. Em produção, a ausência de armazenamento persistente deve causar falha explícita no upload, e não gravação silenciosa em diretório efêmero. Heatmaps devem ser persistidos somente quando o armazenamento configurado estiver disponível.

## Banco de dados

A migração `drizzle/0002_harden_diagnosis_relations.sql` adiciona chaves estrangeiras, índices e unicidade por `(model_name, model_version)`. Aplique as migrações no ambiente que possuir `DATABASE_URL` e depois execute:

```bash
pnpm exec tsx scripts/seed_model_metrics.ts
```

A carga real no banco não foi executada nesta sessão porque `DATABASE_URL` não está configurada. O seed deve ser executado somente no ambiente de implantação, após verificar as migrações e as credenciais fora do repositório.

## Validação executada

| Verificação | Resultado |
|---|---|
| Testes Python | 9 testes aprovados |
| TypeScript | `pnpm check` aprovado |
| Testes TypeScript | 2 arquivos e 4 testes aprovados |
| Build de produção | Aprovado; apenas aviso de chunk front-end grande |
| Avaliação de teste | CNN, ViT e híbrido avaliados em 1.527 imagens |
| Ensemble | Pesos recalculados na validação; métricas e previsões salvas |
| Bootstrap | 1.000 reamostragens, `seed=42`, IC 95% salvo |
| Gate OOD | HAM10000 válido aceito; carro e cabeça/cabelo rejeitados |
| Serviço end-to-end | Classificação aceita, ensemble TypeScript e três heatmaps gerados |
| Heatmaps | Grad-CAM CNN, atribuição ViT, rollout e mapa híbrido gerados |

O teste end-to-end aceitou a imagem HAM10000 com `ood_score=0,809506`, retornou classificação final `benign`, confiança 97,9253% e `abstain=false`. O carro foi rejeitado com `ood_score=469,303577`; a imagem de cabeça/cabelo foi rejeitada com `ood_score=503,887232`. Ambos retornaram `IMAGE_NOT_ELIGIBLE` antes da classificação.

## Artefatos principais

`docs/experiments/EXPERIMENT_REPORT.md` contém o protocolo e os resultados. `docs/experiments/HAM10000_BIAS_AUDIT.json` contém a auditoria de distribuição. `docs/experiments/ENSEMBLE_BOOTSTRAP_CI.json` contém os intervalos de confiança. `ml_artifacts/ham10000/ensemble/test_metrics.json` contém as métricas por componente e do ensemble. `ml_artifacts/ham10000/ensemble/test_predictions.npz` contém as previsões congeladas. `ml_artifacts/ham10000/xai/demo/` contém os heatmaps de demonstração e `visual_validation_notes.md` registra a inspeção visual. `ml_artifacts/ham10000/ood_gate_validation.md` registra a validação do gate.

## Limitações que devem permanecer na dissertação

Os checkpoints atuais são uma rodada curta de validação do pipeline, com duas épocas, backbone congelado e 160×160 px em CPU. Eles não devem ser apresentados como a versão final de desempenho clínico. A base possui desbalanceamento, baixo suporte para classes raras, ausência de tom de pele validado e ausência de `patient_id`. Não é permitido afirmar ausência de viés contra peles negras, diagnóstico clínico ou generalização fora do domínio.

O sistema é uma ferramenta de apoio à pesquisa e triagem computacional. A saída não substitui avaliação dermatológica, e os heatmaps são explicações aproximadas, não máscaras clínicas nem prova de causalidade.
