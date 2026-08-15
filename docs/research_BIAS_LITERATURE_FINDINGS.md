# Trilha de pesquisa sobre viés dermatológico

## Consultas e fontes

A busca inicial identificou literatura recente sobre sub-representação de tons de pele escuros, menor desempenho de sistemas dermatológicos em peles negras e necessidade de validação externa. Foram abertas duas fontes acadêmicas para leitura direta:

1. Revisão em PubMed Central: https://pmc.ncbi.nlm.nih.gov/articles/PMC12624499/
2. Protocolo metodológico no Journal of Medical Internet Research: https://ai.jmir.org/2024/1/e58275/

Na sessão atual, a primeira página apresentou uma barreira reCAPTCHA e a segunda não carregou conteúdo textual no navegador. Portanto, nenhuma afirmação detalhada dessas páginas deve ser tratada como extraída integralmente até uma nova tentativa por extração textual ou acesso direto ao artigo.

## Achados preliminares da busca

Os resultados acadêmicos identificaram como temas recorrentes: desempenho inferior em tons de pele mais escuros, sub-representação de peles negras em materiais e bases dermatológicas, necessidade de medir a composição demográfica/tonal do conjunto, validação externa e relato de desempenho por subgrupo. Para a implementação, esses temas serão convertidos em análise de distribuição, métricas por classe, auditoria de subgrupos e limitações explícitas, sem inventar rótulos de tom de pele ausentes no HAM10000.

## Regra metodológica adotada

O projeto não deve inferir cor da pele de forma silenciosa nem atribuir grupos raciais a imagens sem anotação validada. Caso o HAM10000 não possua rótulo confiável de tom de pele, a dissertação deve declarar a ausência dessa variável e usar um conjunto externo com anotação apropriada para avaliar equidade, ou limitar a conclusão à população representada na base disponível.

## Fontes lidas diretamente

### Daneshjou et al., Science Advances / PubMed

A página do PubMed para o estudo de 2022 informa que modelos de IA dermatológica apresentaram limitações substanciais no conjunto DDI, especialmente em tons de pele escuros e doenças incomuns. O resumo também informa que o fine-tuning com imagens DDI reduziu a diferença de desempenho entre tons claros e escuros. Fonte: https://pubmed.ncbi.nlm.nih.gov/35960806/ ; DOI: https://doi.org/10.1126/sciadv.abq6147.

### Diverse Dermatology Images (DDI)

A página oficial do DDI informa que o conjunto é composto por uma amostra retrospectiva de conveniência com imagens Fitzpatrick I–VI, desenhada para permitir comparação entre Fitzpatrick I–II e V–VI com pareamento por categoria diagnóstica, idade aproximada, gênero e período da fotografia. A página também informa 656 imagens representando 570 pacientes; o tom de pele foi anotado por avaliação presencial na clínica e as imagens possuem confirmação por biópsia/avaliação patológica conforme descrito no conjunto. Fonte: https://ddi-dataset.github.io/.

## Implicação para este projeto

O HAM10000 continua adequado para desenvolvimento inicial de classificação dermatoscópica, mas não deve ser tratado como evidência suficiente de equidade por tom de pele. A avaliação final deve separar desenvolvimento interno de validação externa: manter o teste HAM10000 congelado e, se a licença/acesso acadêmico permitirem, usar DDI ou Fitzpatrick17k como conjunto externo, reportando desempenho por grupo tonal e por diagnóstico comum/incomum. Não se deve atribuir rótulos Fitzpatrick às imagens HAM10000 sem anotação validada.
