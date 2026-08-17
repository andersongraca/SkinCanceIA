# Pipeline de aprendizado de máquina

Este diretório contém o pipeline de treinamento, inferência e explicabilidade do sistema de classificação de lesões dermatoscópicas. A implementação foi isolada do `client/`, portanto a interface existente não é alterada.

## Preparação

Instale as dependências Python com `pip install -r requirements-ml.txt`. O pipeline espera um diretório de imagens e um CSV de metadados com, no mínimo, as colunas `image_id` e `dx`. O rótulo `dx` deve usar as sete categorias `akiec`, `bcc`, `bkl`, `df`, `mel`, `nv` e `vasc`. Quando disponíveis, `patient_id` ou `lesion_id` serão usados para manter imagens correlacionadas no mesmo grupo durante a divisão.

O pipeline não baixa datasets automaticamente nem assume licença para dados privados. Para o HAM10000, use os arquivos obtidos de uma fonte autorizada e confira a licença e os metadados antes de treinar. Os caminhos permanecem locais e são passados por argumentos ou variáveis de ambiente.

## Treinamento

O comando abaixo treina os três modelos individuais e salva checkpoints, configurações, divisão agrupada, histórico e calibração em `ml_artifacts/`:

```bash
python3 -m ml.skin_cancer_ml.train \
  --data-dir /caminho/para/imagens \
  --metadata-csv /caminho/para/HAM10000_metadata.csv \
  --output-dir ml_artifacts \
  --model all \
  --epochs 20 \
  --batch-size 16 \
  --freeze-backbone \
  --unfreeze-backbone-after 5 \
  --balanced-sampler
```

A configuração usa transferência de aprendizado quando os pesos podem ser obtidos, focal loss com pesos por número efetivo de amostras, supervisão multitarefa, divisão por grupo, AdamW, clipping de gradiente, scheduler cosseno e calibração de temperatura no conjunto de validação. A opção `--balanced-sampler` ativa, somente no treino, amostragem com raiz inversa da frequência e reposição; validação e teste permanecem com a distribuição original. Com `--freeze-backbone --unfreeze-backbone-after 5`, as cinco primeiras épocas treinam as cabeças e as épocas seguintes descongelam o backbone com taxa de aprendizagem dez vezes menor, reduzindo o risco de destruir as representações pré-treinadas. O valor padrão `0` mantém o backbone congelado durante toda a execução. Se pesos externos não estiverem disponíveis, o treinador registra a inicialização sem pré-treinamento; isso não deve ser confundido com resultado final.

## Inferência

```bash
python3 -m ml.skin_cancer_ml.infer \
  --checkpoint ml_artifacts/hybrid/best.pt \
  --image /caminho/para/imagem.jpg
```

A resposta JSON contém a decisão binária, as probabilidades binárias e multiclasses, a classe fina predominante, a versão do modelo, a quantidade de amostras de TTA e indicadores de incerteza. A decisão não deve ser interpretada como diagnóstico médico; trata-se de suporte computacional para avaliação por profissional habilitado.

## Explicabilidade

```bash
python3 -m ml.skin_cancer_ml.explain \
  --checkpoint ml_artifacts/hybrid/best.pt \
  --image /caminho/para/imagem.jpg \
  --output /tmp/heatmap.png
```

Para CNN, o pipeline gera Grad-CAM. Para ViT, gera atribuição dos tokens por gradiente. Para o híbrido, gera Grad-CAM do ramo convolucional, atribuição dos tokens, rollout de atenção e mapa combinado ponderado pelo gate aprendido. Os mapas devem ser avaliados por fidelidade e inspeção especializada; não são segmentações clínicas nem prova de causalidade.

## Integração com o servidor

O servidor TypeScript chama os módulos Python por processo controlado, sem `shell` intermediário e com timeout. Configure `ML_PROJECT_ROOT`, `ML_PYTHON_PATH`, `ML_CNN_CHECKPOINT`, `ML_VIT_CHECKPOINT`, `ML_HYBRID_CHECKPOINT`, `ML_DOMAIN_REFERENCE`, `ML_ENSEMBLE_WEIGHTS_PATH`, `ML_MODEL_VERSION` e `ML_INFERENCE_TIMEOUT_MS` no ambiente de execução. Para produção, configure também `DATABASE_URL`, `BUILT_IN_FORGE_API_URL` e `BUILT_IN_FORGE_API_KEY` para banco e armazenamento persistente. Não commite essas variáveis em arquivos `.env` ou no repositório.

A mutação protegida `diagnosis.classifyStoredImage` recebe o identificador de uma imagem já persistida, valida a propriedade pelo usuário autenticado, executa a inferência e grava o diagnóstico. A rota não aceita caminho arbitrário informado por usuário não autenticado.

## Auditoria de classes e representatividade

Execute a auditoria antes de qualquer treinamento final:

```bash
python3 ml/audit_ham10000.py \
  --metadata data/metadata/HAM10000_metadata.csv \
  --split-dir ml_artifacts/ham10000 \
  --output docs/experiments/HAM10000_BIAS_AUDIT.json
```

O HAM10000 possui forte concentração em `nv` e classes raras como `df` e `vasc`. O relatório deve apresentar suporte, precisão, recall, F1, AUROC one-vs-rest e AUPRC one-vs-rest por classe. O metadata disponível contém idade, sexo e localização, mas não contém rótulo validado de tom de pele/Fitzpatrick nem `patient_id`; portanto, não se deve inferir tom de pele dos pixels nem declarar equidade por pele negra usando apenas essa base.

A avaliação final deve preservar o teste HAM10000 congelado e, quando houver acesso autorizado, incluir validação externa com imagens clínicas que tenham anotação confiável de diversidade tonal, como DDI ou Fitzpatrick17k. Os resultados devem ser separados por subgrupo tonal, diagnóstico comum/incomum e classe rara, sempre reportando suporte e intervalos de confiança. A ausência de um subgrupo não deve ser convertida em desempenho zero sem explicação metodológica.

## Reprodutibilidade e validade

Os artefatos salvos incluem a configuração, o resumo das divisões, as tabelas de treino/validação/teste, o histórico e a temperatura de calibração. O conjunto de teste deve permanecer congelado e não pode ser usado para escolher hiperparâmetros. Resultados científicos devem ser reportados com AUROC, AUPRC, sensibilidade, especificidade, macro-F1, MCC, Brier score, ECE, matriz de confusão, métricas por classe e análise por subgrupo quando os metadados permitirem. Nenhuma saída do sistema deve ser descrita como diagnóstico clínico autônomo.
