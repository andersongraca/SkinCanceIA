# Evidência da fonte oficial do dataset

A página oficial consultada foi o Harvard Dataverse/ViDIR Dataverse, com o título **The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions**.

URL permanente: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T

A página foi aberta em 15 de agosto de 2026 para confirmar a origem e as condições de uso antes de qualquer download. O conteúdo textual carregou; a captura visual não foi necessária para a auditoria. Próximo passo: extrair do HTML os metadados de versão, arquivos, licença e termos de uso, e registrar o identificador DOI junto dos artefatos do experimento.

## Termos confirmados

A versão oficial consultada é a **4.0**. O dataset contém 10.015 imagens, sete classes diagnósticas e `lesion_id` para agrupar imagens da mesma lesão. A página lista publicamente os dois ZIPs de imagens, o metadata tabular, as segmentações revisadas por dermatologista e o teste ISIC 2018.

A licença indicada na aba Terms é **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**. O uso acadêmico não comercial é compatível com o objetivo do mestrado, desde que o trabalho cite o dataset conforme a citação oficial, preserve a atribuição e não redistribua os arquivos brutos fora dos termos. O código, os checkpoints derivados e as métricas serão mantidos separados dos arquivos originais; os arquivos brutos não serão versionados no GitHub.

A fonte oficial alerta que o repositório estava com problemas técnicos de API durante a consulta. O download deve ser feito pelo fluxo web/arquivo público do Harvard Dataverse ou por uma cópia institucional autorizada, conferindo a integridade por MD5 quando disponível. A licença não substitui eventual aprovação institucional para uso de dados médicos; o orientador e a instituição devem confirmar que o uso proposto atende às regras locais de pesquisa.

Referências: DOI `10.7910/DVN/DBW86T`; https://doi.org/10.7910/DVN/DBW86T; licença e termos na página oficial do Harvard Dataverse, versão 4.0.

## Acesso ao metadata

A página pública do arquivo `HAM10000_metadata.tab` foi aberta no navegador. O Dataverse exibe o botão **Access File** e mostra os termos **Creative Commons Attribution-NonCommercial 4.0 International Public License**. O metadata é público, tem 8 variáveis e 10.015 observações segundo a página do dataset. A API exibiu aviso de instabilidade; o download deve usar o botão público do arquivo ou o endpoint oficial quando o serviço estabilizar.

## Termos de acesso exibidos no navegador

O arquivo `HAM10000_metadata.tab` está marcado como **Public** no menu Access File. O mesmo menu oferece CSV, Tab-delimited e RData, além de metadados e citação. A licença exibida é CC BY-NC 4.0; o texto acessível informa que a licença permite reproduzir e compartilhar o material e material adaptado somente para fins não comerciais, exige atribuição/citação e não permite sugerir endosso do licenciante.

## Confirmação dos termos no modal

Ao selecionar o formato CSV, o Dataverse exibiu novamente o modal **Dataset Terms** com a licença CC BY-NC 4.0. O download somente prossegue após aceitar os termos; a página também expõe a opção de cancelar. Como o uso é para pesquisa de mestrado não comercial e a licença exige citação, o próximo passo é aceitar os termos apenas para baixar o metadata público e registrar essa decisão no protocolo.

## Download do metadata

O histórico de downloads do Chromium confirmou o arquivo `HAM10000_metadata` proveniente de `https://dataverse.harvard.edu`. O aceite da licença foi realizado após confirmação explícita do usuário. O arquivo deve ser localizado em `/home/ubuntu/Downloads/`; será copiado para o diretório de dados local e validado antes do treinamento.

## Arquivos de imagem

A página oficial confirmou `HAM10000_images_part_1.zip` como arquivo público ZIP do dataset, identificado por DOI de arquivo `10.7910/DVN/DBW86T/XJZSQ6`. O menu oferece a opção **ZIP Archive** para download e repete os termos CC BY-NC 4.0. O arquivo deve ser baixado fora do repositório, validado e extraído somente no diretório local de dados.

## Liberação das imagens parte 1

O Dataverse solicitou e recebeu o aceite dos termos para `HAM10000_images_part_1.zip`. A página voltou ao estado normal após a confirmação; o download deve ser verificado no histórico do navegador antes de iniciar a parte 2.

## Arquivo de imagem parte 2

A página oficial confirmou `HAM10000_images_part_2.zip` como arquivo público ZIP, identificado pelo DOI de arquivo `10.7910/DVN/DBW86T/IZEF3O`. O menu de acesso oferece **ZIP Archive** e repete a licença CC BY-NC 4.0. O aceite dos termos já foi confirmado pelo usuário para uso acadêmico não comercial.

## Liberação das imagens parte 2

O Dataverse solicitou e recebeu o aceite dos termos para `HAM10000_images_part_2.zip`. A página voltou ao estado normal após a confirmação; o download será verificado no diretório local antes da extração.

## Imagens OOD para teste de rejeição

Foram copiadas apenas para testes locais duas imagens públicas retornadas pela busca de imagens: uma fotografia de carro proveniente do PICRYL (`public_car_picryl.jpg`) e uma imagem pública de cabeça/rosto sem identificação proveniente do PICRYL (`public_head_picryl.jpg`). Elas não fazem parte do HAM10000, não serão usadas para treinar o classificador e não serão publicadas como dados clínicos; servem somente para verificar se o gate retorna `outside_dermoscopy_domain`.
