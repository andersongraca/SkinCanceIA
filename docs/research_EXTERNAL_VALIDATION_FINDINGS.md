# Evidências para validação externa e representatividade

## DDI — Diverse Dermatology Images

A página oficial do DDI informa que o conjunto possui 656 imagens de 570 pacientes únicos, com diagnósticos confirmados por patologia e tons de pele Fitzpatrick I–VI. A anotação de tom foi realizada por avaliação presencial na consulta, cruzamento com fotografias demográficas e revisão por dois dermatologistas certificados. O desenho permite comparar FST I–II com FST V–VI por categoria diagnóstica, idade, gênero e data da fotografia.

A página também estabelece que o DDI é destinado a pesquisa não comercial e não pode ser redistribuído ou usado para diagnóstico ou cuidado de pacientes. Portanto, qualquer validação deve ocorrer após registro individual no portal e sem incluir imagens no repositório público.

Fonte oficial: https://ddi-dataset.github.io/

Fonte institucional: https://aimi.stanford.edu/datasets/ddi-diverse-dermatology-images

## Fitzpatrick17k

A publicação do MIT Media Lab descreve 16.577 imagens clínicas anotadas com tipos de pele Fitzpatrick, provenientes de dois atlas dermatológicos e cobrindo 114 condições. O trabalho relata maior representação de tons claros e queda de desempenho quando o tipo de pele se distancia dos dados de treinamento. O conjunto é clínico, não dermatoscópico; portanto, sua utilização deve ser tratada como validação de domínio externo, e não como substituto direto do teste HAM10000.

Fonte: https://www.media.mit.edu/publications/evaluating-deep-neural-networks-trained-on-clinical-images-in-dermatology-with-the-fitzpatrick-17k-dataset/

## HAM10000

O artigo original descreve 10.015 imagens dermatoscópicas de múltiplas fontes, com mais de 50% das lesões confirmadas por patologia e os demais casos apoiados por acompanhamento, consenso especializado ou microscopia confocal. O dataset é adequado para benchmark dermatoscópico, mas a validação externa deve considerar diferenças de modalidade, população, equipamento e origem das imagens.

Fonte: https://www.nature.com/articles/sdata2018161

## Implicação metodológica

O experimento final deve manter o teste HAM10000 congelado e adicionar uma avaliação externa separada. Para cada subgrupo tonal, devem ser reportados suporte, sensibilidade, especificidade, AUROC, AUPRC, F1, calibração e intervalos de confiança. As imagens clínicas do DDI ou Fitzpatrick17k não devem ser misturadas ao treino dermatoscópico sem um protocolo explícito, pois isso confundiria domínio de aquisição com efeito de tom de pele.
