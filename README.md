# SkinCancerCADDermoIA

## Sistema CAD para análise de lesões cutâneas

O SkinCancerCADDermoIA é um sistema de auxílio à pesquisa para análise de imagens dermatoscópicas. O backend científico implementa classificação multiclasses das sete categorias do HAM10000, classificação binária benigno/maligno, calibração de probabilidade, estimativa de incerteza, abstensão, triagem de qualidade e rejeição de imagens fora do domínio dermatoscópico.

A arquitetura experimental reúne três componentes: uma CNN baseada em ResNet-50 para características locais, um Vision Transformer para relações globais e um modelo híbrido CNN–ViT com projeção em tokens, blocos de atenção e gate de fusão. Um ensemble combina as probabilidades calibradas dos três componentes com pesos selecionados exclusivamente na validação.

> O sistema é uma ferramenta de apoio à pesquisa e triagem computacional. Não realiza diagnóstico autônomo, não substitui avaliação dermatológica e não deve ser usado para decisões clínicas sem validação externa e supervisão profissional.

## Funcionalidades científicas

O pipeline Python contém preparação determinística do HAM10000, divisão agrupada por `lesion_id`, perdas focais, amostragem balanceada opcional, métricas multiclasses e binárias, calibração por temperatura, intervalos de confiança por bootstrap, avaliação por subgrupos externos e auditoria de classes raras.

A entrada é submetida a uma barreira de elegibilidade antes da inferência. O backend verifica decodificação, resolução, proporção, exposição, uniformidade, detalhe visual e distância robusta em relação à referência de domínio calibrada com HAM10000. Imagens de carro, cabeça/cabelo, rosto ou outros objetos devem ser rejeitadas com `IMAGE_NOT_ELIGIBLE` quando estiverem fora da distribuição de referência.

A explicabilidade é produzida sem alterar o modelo: Grad-CAM para a CNN, atribuição de tokens para o ViT e Grad-CAM, atribuição de tokens, rollout de atenção e mapa combinado para o híbrido. Os mapas são explicações aproximadas e não devem ser interpretados como máscaras anatômicas ou prova de causalidade.

## Resultado da rodada executada

Os três checkpoints desta rodada foram treinados em CPU com resolução 160×160, backbone congelado, amostragem balanceada no treino e duas épocas por modelo. O teste congelado contém 1.527 imagens.

| Modelo | Macro-F1 multiclasses | AUROC multiclasses | AUROC binária | Sensibilidade | Especificidade |
|---|---:|---:|---:|---:|---:|
| CNN ResNet-50 | 0,3725 | 0,8748 | 0,8167 | 0,7667 | 0,6903 |
| ViT | 0,4311 | 0,8922 | 0,8487 | 0,7167 | 0,7938 |
| Híbrido CNN–ViT | 0,3957 | 0,8853 | 0,8465 | 0,6533 | 0,8289 |
| Ensemble | **0,4748** | **0,9096** | **0,8607** | **0,7167** | **0,8052** |

O ensemble atual usa pesos de validação CNN 10%, ViT 50% e híbrido 40%. As métricas completas estão em [`docs/experiments/EXPERIMENT_REPORT.md`](docs/experiments/EXPERIMENT_REPORT.md), incluindo suporte das classes `df` e `vasc`, intervalos de confiança e limitações de representatividade.

## Dataset e limites de interpretação

O HAM10000 foi obtido do [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T), versão 4.0, sob licença CC BY-NC 4.0 para uso acadêmico não comercial. As imagens brutas, os arquivos de download e os checkpoints são mantidos fora do controle de versão.

O metadata utilizado não contém `patient_id` nem rótulo validado de tom de pele/Fitzpatrick. Portanto, o projeto não afirma equidade para peles negras com base apenas no HAM10000, não infere tonalidade pelos pixels e não apresenta desempenho clínico geral. A versão final da dissertação deve incluir validação externa autorizada com rótulos tonais confiáveis, análise por paciente quando possível, múltiplas sementes e suporte explícito para classes raras.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-ml.txt
pnpm install
```

A aplicação web exige Node.js 18 ou superior, pnpm e um banco MySQL/TiDB quando o histórico e as métricas persistidas forem habilitados. O arquivo [`.env.example`](.env.example) lista as variáveis necessárias sem conter credenciais reais; copie-o para um arquivo local e preencha somente os valores do seu ambiente.

## Preparação e treinamento

```bash
pnpm ml:prepare
pnpm ml:quality-reference

PYTHONPATH=ml python3 -m skin_cancer_ml.train \
  --data-dir data/raw/images \
  --metadata-csv data/metadata/HAM10000_metadata.csv \
  --output-dir ml_artifacts/ham10000 \
  --model all \
  --epochs 20 \
  --image-size 224 \
  --batch-size 16 \
  --balanced-sampler
```

O comando de treinamento acima é uma configuração recomendada para GPU. A rodada versionada no relatório foi uma execução curta em CPU destinada à validação do pipeline completo.

Após o treinamento, execute a avaliação congelada e o ensemble:

```bash
PYTHONPATH=ml python3 ml/evaluate_test.py \
  --checkpoint ml_artifacts/ham10000/cnn/best.pt \
  --test-csv ml_artifacts/ham10000/test.csv

PYTHONPATH=ml python3 ml/ensemble.py \
  --root ml_artifacts/ham10000 \
  --test-csv ml_artifacts/ham10000/test.csv

PYTHONPATH=ml python3 ml/bootstrap_metrics.py \
  --predictions ml_artifacts/ham10000/ensemble/test_predictions.npz \
  --output docs/experiments/ENSEMBLE_BOOTSTRAP_CI.json \
  --repeats 1000 --seed 42
```

## Configuração do backend

As seguintes variáveis devem ser configuradas fora do repositório:

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

Para o servidor completo, configure também `DATABASE_URL` e as variáveis do armazenamento persistente. Não versionar arquivos `.env`, tokens, chaves ou credenciais.

## Testes e validação

```bash
PYTHONPATH=ml python3 -m pytest -q
pnpm check
pnpm test
pnpm build
```

A suíte validada nesta rodada contém nove testes Python, quatro testes TypeScript em dois arquivos e build de produção aprovado. O teste do serviço TypeScript pode ser executado com os checkpoints configurados:

```bash
pnpm exec tsx scripts/test_ml_service.ts data/ood_examples/in_domain_ham10000.jpg
pnpm exec tsx scripts/test_ml_rejection.ts test_assets/ood/public_car_picryl.jpg
pnpm exec tsx scripts/test_ml_rejection.ts test_assets/ood/public_head_picryl.jpg
```

Os ativos locais em `test_assets/ood/` são exemplos de smoke test documentados como domínio público. Imagens sem licença individual confirmada não devem ser incluídas no repositório nem usadas como evidência clínica.

## Estrutura relevante

| Diretório | Responsabilidade |
|---|---|
| `ml/skin_cancer_ml/` | Configuração, dados, modelos, inferência, qualidade e explicabilidade |
| `ml/ensemble.py` | Seleção de pesos na validação e avaliação do ensemble |
| `ml/bootstrap_metrics.py` | Intervalos de confiança no teste congelado |
| `server/services/` | Integração TypeScript–Python e orquestração dos modelos |
| `server/routers.ts` | Procedimentos tipados de upload, classificação, histórico e métricas |
| `client/src/components/diagnosis/` | Interface de upload, resultados, métricas e histórico |
| `docs/experiments/` | Relatórios, auditoria, métricas e limitações científicas |
| `tests/` | Testes Python do backend científico |

## Licença do código

O código da aplicação permanece sob a licença definida pelo projeto. O HAM10000 possui termos próprios de uso e não é redistribuído neste repositório. Consulte a documentação do dataset e preserve a atribuição exigida.

## Contato do projeto

Projeto de mestrado de Anderson Graça Araújo — PROCC/UFS.
