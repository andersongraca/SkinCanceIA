# Configuração de incerteza e abstensão

## Objetivo

O pipeline calcula a incerteza de cada checkpoint usando entropia preditiva e variância entre as três transformações TTA. A abstensão é um mecanismo de segurança: quando a saída não é suficientemente estável, o sistema informa que a classificação deve ser revisada, em vez de apresentar uma resposta automatizada como definitiva.

## Parâmetros

Os limiares individuais são configuráveis por variáveis de ambiente:

```env
ML_ENTROPY_THRESHOLD=0.75
ML_TTA_VARIANCE_THRESHOLD=0.03
```

Os limiares agregados e o quórum do ensemble são configuráveis separadamente:

```env
ML_ENSEMBLE_ABSTAIN_VOTES=2
ML_ENSEMBLE_ENTROPY_THRESHOLD=0.75
ML_ENSEMBLE_TTA_VARIANCE_THRESHOLD=0.03
```

O valor padrão do quórum é dois votos de abstensão em três modelos. Assim, um único modelo com entropia alta não bloqueia o ensemble quando os outros dois permanecem estáveis. A política ainda recomenda abstensão quando pelo menos dois modelos votam pela abstensão ou quando a entropia/variância média do ensemble ultrapassa os limiares agregados.

## Interpretação

A confiança da classe e a incerteza são medidas diferentes. Uma imagem pode receber classificação provisória com confiança alta e, simultaneamente, ser marcada para revisão se um modelo apresentar comportamento instável. A saída continua sendo experimental e não substitui avaliação dermatológica.

## Calibração para pesquisa

Os valores não devem ser escolhidos apenas para eliminar a abstensão de uma imagem individual. Para uma calibração defensável, mantenha o teste congelado e faça uma varredura dos limiares no conjunto de validação. Para cada combinação, registre cobertura, erro entre imagens aceitas, sensibilidade para casos malignos e especificidade.

Uma grade inicial para investigação é:

- Entropia: 0,60 a 0,85, com passo de 0,05.
- Variância TTA: 0,010 a 0,050, com passo de 0,005.
- Quórum: 1, 2 ou 3 votos.

A configuração escolhida deve ser registrada junto da versão do conjunto de validação e dos indicadores obtidos antes e depois do ajuste. Os parâmetros usados na configuração local atual são experimentais e devem ser reavaliados quando os modelos forem treinados novamente.
