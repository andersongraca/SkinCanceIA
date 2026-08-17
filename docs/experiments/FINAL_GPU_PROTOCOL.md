# Protocolo da rodada final em GPU

Este protocolo deve ser executado na máquina com GPU depois que o dataset autorizado estiver disponível. A rodada atual em CPU permanece como validação de funcionamento e não deve ser sobrescrita sem preservar seus artefatos.

## Treinamento

```bash
cd /caminho/para/SkinCancerCADDermoIA
export PYTHONPATH=ml

python3 -m skin_cancer_ml.train \
  --data-dir data/raw/images \
  --metadata-csv data/metadata/HAM10000_metadata.csv \
  --output-dir ml_artifacts/ham10000_final \
  --model all \
  --epochs 20 \
  --image-size 224 \
  --batch-size 16 \
  --freeze-backbone \
  --unfreeze-backbone-after 5 \
  --balanced-sampler
```

A opção `--unfreeze-backbone-after 5` treina inicialmente as cabeças e os blocos de fusão, descongela o backbone na sexta época e recria o otimizador com taxa de aprendizagem dez vezes menor. Se a memória da GTX 1050 Ti for insuficiente, reduza o batch para 8 ou 4, sem alterar validação e teste.

## Avaliação congelada

```bash
for model in cnn vit hybrid; do
  python3 ml/evaluate_test.py \
    --checkpoint ml_artifacts/ham10000_final/$model/best.pt \
    --test-csv ml_artifacts/ham10000_final/test.csv \
    --batch-size 16
done

python3 ml/ensemble.py \
  --root ml_artifacts/ham10000_final \
  --test-csv ml_artifacts/ham10000_final/test.csv \
  --batch-size 16

python3 ml/bootstrap_metrics.py \
  --predictions ml_artifacts/ham10000_final/ensemble/test_predictions.npz \
  --output docs/experiments/ENSEMBLE_BOOTSTRAP_CI_FINAL.json \
  --repeats 2000 \
  --seed 42
```

Os pesos devem ser selecionados apenas na validação. O teste não deve ser usado para escolher épocas, hiperparâmetros, limiares ou pesos.

## Validação externa

A avaliação DDI ou Fitzpatrick17k deve permanecer em um diretório separado, sem copiar as imagens para o repositório. O metadata externo precisa fornecer o rótulo diagnóstico compatível com a tarefa e a anotação tonal validada. Execute `ml/evaluate_subgroups.py` somente depois de confirmar a licença e o alinhamento de ordem entre metadata e predições.

Os resultados devem ser apresentados por subgrupo com suporte, AUROC, AUPRC, sensibilidade, especificidade, F1, ECE e intervalos de confiança. Não se deve misturar imagens clínicas externas ao treino dermatoscópico nesta etapa, pois isso mudaria a pergunta científica e confundiria efeito de domínio com efeito de tom de pele.

## Critérios de aceitação

A rodada final só deve substituir os resultados da dissertação se todos os modelos produzirem checkpoints válidos, o teste congelado for avaliado uma única vez, o ensemble for escolhido na validação, os intervalos forem gerados, o relatório por classe incluir `df` e `vasc`, e a validação externa preservar os rótulos tonais sem inferência automática pelos pixels.
