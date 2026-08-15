# Fontes oficiais de imagens dermatológicas para teste

## ISIC Archive

Fonte: https://www.isic-archive.com/

A página oficial descreve o ISIC Archive como um arquivo público de imagens de pele voltado a ensino, pesquisa e desenvolvimento/teste de algoritmos de inteligência artificial. O arquivo oferece galeria pública, coleções, anotações e conjuntos de benchmark. Antes de baixar uma imagem individual, deve-se verificar os termos aplicáveis à coleção e registrar o identificador da imagem e a licença correspondente.

## Diverse Dermatology Images (DDI)

Fonte: https://ddi-dataset.github.io/

O DDI é descrito como um conjunto de imagens de doenças cutâneas confirmadas por biópsia, com representação de tons Fitzpatrick I–VI. O site informa 656 imagens de 570 pacientes, rótulo de tom de pele baseado em avaliação presencial, diagnóstico baseado em laudo de patologia e comparação planejada entre Fitzpatrick I–II e V–VI.

O acordo de uso permite visualização e uso para pesquisa pessoal não comercial, mas proíbe redistribuir ou publicar cópias das imagens sem autorização específica. Portanto, o DDI pode ser usado para validação local após registro e aceite do acordo, mas suas imagens não devem ser anexadas ao repositório público nem enviadas em um pacote de código.

## HAM10000

Fonte: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T

O HAM10000 continua sendo a fonte autorizada já utilizada no projeto, com uso acadêmico não comercial conforme a licença registrada no manifesto do projeto. Ele é adequado para o pipeline dermatoscópico principal, mas o metadata local não contém rótulo validado de tom de pele nem patient_id; portanto, não deve ser usado sozinho para concluir ausência de viés em peles negras.

## Regra de seleção

Para testes reproduzíveis, preferir imagens com identificador estável, diagnóstico ou anotação oficial, licença/termo de uso registrado e origem acadêmica. Imagens encontradas em busca de imagens sem licença identificável não devem ser usadas como evidência científica nem publicadas no repositório. Imagens de carro, cabeça/cabelo e objetos podem ser usadas apenas como casos OOD se a fonte permitir uso e redistribuição, com atribuição apropriada.

## Imagens encontradas na busca associada ao ISIC

Foram verificadas visualmente duas imagens baixadas nos resultados associados ao ISIC Archive: `lFGg1DzDNBwt.jpg` (1024×1024, campo dermatoscópico circular com lesão pigmentada central) e `OnvpVX3cFbgh.jpg` (256×256, campo circular com pelos e pequena área avermelhada). A busca não forneceu identificador individual nem licença específica para cada arquivo; portanto, elas podem ser usadas apenas como referências de inspeção neste momento, não como amostras científicas publicadas ou como dados de treinamento até que o identificador e os termos da coleção sejam confirmados no ISIC.
