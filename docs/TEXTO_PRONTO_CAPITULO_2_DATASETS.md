# Texto pronto para inserir no artigo

## Local exato de inserção

Inserir o conteúdo abaixo na seção do artigo que apresenta os datasets para câncer de pele, normalmente intitulada `2.2 Datasets para câncer de pele`. O texto deve ser colocado depois da descrição do HAM10000 e do ISIC, antes da seção sobre CNNs, Vision Transformers ou métodos de classificação.

Não criar no artigo o título `4.1 Inserção sugerida na seção de datasets`. Esse título pertence apenas ao relatório de revisão e não deve ser copiado para a dissertação.

## Texto para copiar

**Embora HAM10000 e ISIC sejam referências consolidadas para o desenvolvimento e a comparação de métodos computacionais em imagens dermatológicas, a sua utilização não autoriza presumir representatividade demográfica ou validade clínica universal. O HAM10000 reúne 10.015 imagens dermatoscópicas provenientes de diferentes fontes e modalidades de aquisição, mas os metadados utilizados neste trabalho não contêm, de forma validada e completa, o fototipo de Fitzpatrick de cada imagem. Consequentemente, não é possível inferir a distribuição de tons de pele da amostra nem afirmar que as métricas obtidas no teste interno sejam equivalentes entre diferentes grupos populacionais. A base deve ser tratada como um benchmark de classificação dermatoscópica, e não como uma amostra representativa da população brasileira \cite{ref_44, ref_42}.**

**Essa distinção é particularmente importante porque o desempenho de um modelo pode refletir a distribuição dos dados de treinamento, além das características da doença. O estudo que apresentou o conjunto DDI avaliou imagens clinicamente selecionadas e confirmadas por patologia em diferentes grupos de fototipo e observou limitações relevantes dos modelos previamente treinados, sobretudo em imagens de pele escura e em doenças menos frequentes. O mesmo estudo mostrou que o ajuste fino com dados mais diversificados pode reduzir a diferença de desempenho, mas não elimina a necessidade de uma avaliação independente. O Fitzpatrick17k também demonstrou a utilidade de registrar o fototipo e de avaliar se o desempenho é maior em tipos de pele semelhantes àqueles presentes no treinamento \cite{ref_40, ref_41, ref_42}.**

**No contexto brasileiro, o PAD-UFES-20 oferece uma oportunidade de validação externa porque foi coletado no Espírito Santo com imagens clínicas de smartphones, metadados dos pacientes e informações de fototipo. A base reúne 2.298 imagens, 1.641 lesões e 1.373 pacientes, incluindo diagnósticos de câncer confirmados por biópsia. Entretanto, suas imagens clínicas não são equivalentes às imagens dermatoscópicas do HAM10000. Por essa razão, o PAD-UFES-20 deve ser utilizado inicialmente para medir mudança de domínio e validade externa, e não incorporado diretamente ao treinamento sem um protocolo específico de harmonização, particionamento por paciente e controle de possíveis duplicidades \cite{ref_39, ref_44}.**

**A utilização de bases externas deve considerar também a localização anatômica das lesões. Lesões presentes em palmas, plantas e unidade ungueal podem apresentar características clínicas e dermoscópicas específicas. No contexto brasileiro, uma coorte de melanoma acral destacou a relevância de investigar conjuntamente aspectos epidemiológicos, clínicos, dermoscópicos e histopatológicos, além da escassez de dados nacionais para esse grupo. Assim, a análise de lesões acrais deve ser realizada separadamente quando houver localização anatômica registrada, diagnóstico confiável e número suficiente de casos \cite{ref_43}.**

**Dessa forma, os resultados obtidos no HAM10000 devem ser interpretados como uma avaliação interna no domínio dermatoscópico utilizado no treinamento. Eles não devem ser apresentados como evidência suficiente de equidade entre fototipos nem como validação clínica para a população brasileira. A generalização do sistema deverá ser examinada por meio de validação externa, com métricas estratificadas por fototipo, diagnóstico, localização anatômica e modalidade de aquisição \cite{ref_39, ref_40, ref_41, ref_42, ref_43, ref_44}.**

## Frase de transição para a seção seguinte

**Após essa discussão, a seção seguinte pode iniciar a apresentação das arquiteturas de aprendizado profundo utilizadas na literatura, deixando explícito que a escolha do modelo não elimina a necessidade de controlar a representatividade dos dados e a validade externa.**

## Referências necessárias

As chaves utilizadas no texto são:

```latex
\cite{ref_39}  % PAD-UFES-20
\cite{ref_40}  % DDI
\cite{ref_41}  % Fitzpatrick17k
\cite{ref_42}  % Revisão sobre diversidade de fototipos
\cite{ref_43}  % Coorte brasileira de melanoma acral
\cite{ref_44}  % HAM10000
```

O bloco BibTeX pronto está em `docs/REFERENCIAS_DEMOGRAFIA.bib`. Antes de compilar, conferir se essas chaves ainda não existem no arquivo `.bib` principal da dissertação. Caso já existam, manter as chaves originais e apenas substituir as chaves usadas nos parágrafos.

## Observação metodológica

O texto acima descreve corretamente a limitação e o protocolo de validação. Ele não afirma que o sistema já alcançou uma determinada acurácia por fototipo. Essa afirmação somente poderá ser acrescentada depois da execução real do avaliador externo com os manifestos autorizados dos datasets.
