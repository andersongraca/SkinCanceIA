# Protocolo de validação externa e representatividade demográfica

## Objetivo

O projeto passou a conter um avaliador externo estratificado em `ml/evaluate_external.py`. O módulo foi criado para avaliar os checkpoints já treinados em manifestos autorizados de bases externas, preservando o teste interno do HAM10000 como referência congelada. O avaliador não infere fototipo pela cor dos pixels e não executa fine-tuning automaticamente.

A implementação atende à necessidade apontada no parecer da banca: medir a mudança de domínio e observar o comportamento do sistema quando os dados possuem metadados de fototipo, diagnóstico, localização anatômica ou modalidade de aquisição. O PAD-UFES-20 é relevante por representar imagens clínicas brasileiras obtidas por smartphones [1]. O DDI permite avaliar imagens clinicamente selecionadas, com confirmação patológica e grupos de fototipo [2]. O Fitzpatrick17k fornece anotações de fototipo para imagens clínicas em escala maior, embora suas fontes e rótulos devam ser interpretados conforme as limitações do próprio conjunto [3]. A necessidade de conferir diversidade e verificabilidade dos metadados é discutida por Alipour, Burke e Courtney [4]. A análise de lesões acrais deve ser mantida separada, considerando a escassez de coortes brasileiras específicas [5].

## Manifesto esperado

O avaliador aceita um CSV com os caminhos das imagens e os rótulos. Os nomes das colunas abaixo são recomendados:

```text
image_path,dx,patient_id,lesion_id,fitzpatrick,localization,split
img-001.jpg,mel,p-001,l-001,VI,plantar,test
img-002.jpg,nv,p-002,l-002,II,back,test
```

Os campos `fitzpatrick`, `skin_tone` e `skin_type` devem ser provenientes de metadados autorizados do dataset. O módulo não cria esses rótulos a partir da imagem. Se a base não possuir `patient_id` ou `lesion_id`, essa ausência é registrada no JSON como limitação metodológica.

## Execução

A avaliação pode ser executada com os três checkpoints do experimento:

```bash
PYTHONPATH=ml python3 ml/evaluate_external.py \
  --manifest data/external/PAD_UFES20_manifest.csv \
  --image-dir data/external/PAD_UFES20/images \
  --label-column dx \
  --checkpoint ml_artifacts/ham10000/cnn/best.pt \
  --checkpoint ml_artifacts/ham10000/vit/best.pt \
  --checkpoint ml_artifacts/ham10000/hybrid/best.pt \
  --weights 0.10 0.55 0.35 \
  --output ml_artifacts/external/pad_ufes20_baseline.json
```

O mesmo comando pode ser utilizado para DDI ou Fitzpatrick17k, desde que o pesquisador prepare um manifesto com os caminhos, os rótulos e os metadados fornecidos pela fonte autorizada. O código não baixa os dados automaticamente porque cada base possui condições próprias de acesso, distribuição e uso.

## Saídas registradas

O JSON de saída inclui o protocolo utilizado, os checkpoints, os pesos, o número de imagens, as previsões por imagem, a matriz de confusão, acurácia, acurácia balanceada, precisão, sensibilidade, especificidade, F1-score, AUROC, AUPRC, ECE e taxa de abstenção. As mesmas métricas são calculadas por valor de cada coluna demográfica ou clínica disponível.

Quando um subgrupo possui somente uma classe, AUROC e AUPRC são registrados como indefinidos, e o suporte do grupo é preservado. Essa escolha evita transformar ausência de casos positivos ou negativos em desempenho artificialmente igual a zero. O arquivo também registra duplicidades de pacientes e lesões quando os identificadores estão disponíveis.

## Texto para o artigo

**Para responder à limitação de representatividade identificada na qualificação, foi implementado um avaliador externo estratificado, separado do módulo de treinamento. O avaliador recebe um manifesto autorizado contendo o caminho da imagem, o diagnóstico, o identificador do paciente, o identificador da lesão, o fototipo ou outra anotação de tom de pele e a localização anatômica. A implementação não infere fototipo a partir dos pixels, pois uma estimativa automática de cor não equivale a um rótulo clínico validado. O protocolo foi preparado para comparar os checkpoints treinados no HAM10000 com dados externos, preservando o teste interno e registrando explicitamente a modalidade de aquisição e a disponibilidade dos metadados \cite{ref_39, ref_40, ref_41, ref_42, ref_44}.**

**A avaliação externa é executada antes de qualquer ajuste fino. Para cada base e subgrupo, o sistema registra suporte, acurácia, acurácia balanceada, precisão, sensibilidade, especificidade, F1-score, AUROC, AUPRC, erro esperado de calibração e taxa de abstenção. Também são preservados os resultados por imagem, a matriz de confusão e as verificações de duplicidade por paciente e por lesão. Quando não há casos suficientes ou quando o subgrupo contém apenas uma classe, o resultado é marcado como exploratório e as métricas indefinidas não são substituídas por valores artificiais.**

**O avaliador foi implementado como uma etapa de auditoria e não como um mecanismo automático de re-treinamento. Portanto, a sua existência no código-fonte não significa que a classificação já esteja validada para todos os fototipos ou para a população brasileira. Os resultados demográficos somente devem ser incorporados à dissertação depois da execução com os arquivos autorizados das bases externas e da revisão dos respectivos metadados. Para lesões acrais, o protocolo exige localização anatômica registrada, diagnóstico confiável e suporte suficiente para uma análise independente \cite{ref_43}.**

## Limites de interpretação

A disponibilidade de uma coluna chamada `fitzpatrick` não garante, sozinha, que a anotação seja clínica, completa ou comparável entre bases. A origem, o método de anotação, a quantidade de casos por grupo e a modalidade de aquisição devem ser descritos no artigo. As métricas externas devem ser apresentadas como evidência de generalização ou de mudança de domínio, e não como prova de equidade quando o número de casos for reduzido.

O módulo conserva o teste do HAM10000 sem alterar pesos. Qualquer fine-tuning posterior deve ser executado em uma etapa separada, com controle por paciente e lesão, documentação da licença, comparação com o baseline e novo conjunto de teste externo. Essa separação reduz o risco de contaminar a avaliação externa com decisões de treinamento.

## Referências

[1]: https://doi.org/10.1016/j.dib.2020.106221 "PAD-UFES-20: A skin lesion dataset composed of patient data and clinical images collected from smartphones"
[2]: https://doi.org/10.1126/sciadv.abq6147 "Disparities in dermatology AI performance on a diverse, curated clinical image set"
[3]: https://doi.org/10.1109/CVPRW53098.2021.00201 "Evaluating Deep Neural Networks Trained on Clinical Images in Dermatology with the Fitzpatrick 17k Dataset"
[4]: https://doi.org/10.1007/s13671-024-00440-0 "Skin Type Diversity in Skin Lesion Datasets: A Review"
[5]: https://doi.org/10.1016/j.abd.2024.03.006 "Plantar acral melanoma: epidemiological, clinical, dermoscopic and histopathological features. A Brazilian cohort"
[6]: https://doi.org/10.1038/sdata.2018.161 "The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions"
