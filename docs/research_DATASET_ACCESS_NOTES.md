# Notas de acesso e elegibilidade de datasets

## HAM10000 — Harvard Dataverse

A página oficial é `https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T`. Nesta sessão, a página não entregou texto navegável nem captura visual confiável; portanto, os detalhes de versão, arquivos e termos devem ser confirmados por extração textual ou pela documentação já existente no repositório antes do download. O projeto já registra a versão 4.0, 10.015 imagens, sete classes e licença CC BY-NC 4.0, mas essa informação será tratada como pendente de nova confirmação direta nesta rodada.

## DDI — Stanford AIMI

A fonte institucional consultada foi `https://aimi.stanford.edu/datasets/ddi-diverse-dermatology-images`, com URL canônica `https://ddi-dataset.github.io/index.html` e DOI de citação `https://doi.org/10.71718/kqee-3z39`.

A página descreve o DDI como conjunto público, profundamente curado e confirmado patologicamente, com diversidade de tons de pele. Após filtragem de baixa qualidade, restaram 656 imagens de 570 pacientes únicos. A distribuição informada é: FST I–II, 208 imagens (159 benignas, 49 malignas); FST III–IV, 241 (167 benignas, 74 malignas); FST V–VI, 207 (159 benignas, 48 malignas). O conjunto é retrospectivo e de conveniência, sendo adequado principalmente para validação externa e análise de subgrupos, não para ser misturado automaticamente ao treino do HAM10000. O acesso e os termos do botão de download ainda precisam ser verificados antes de qualquer cópia local.

## Confirmação textual adicional — 20 de agosto de 2026

A extração textual da página oficial do Harvard Dataverse confirmou o HAM10000 na versão 4.0, com 10.015 imagens, sete categorias (`akiec`, `bcc`, `bkl`, `df`, `mel`, `nv`, `vasc`), agrupamento por `lesion_id`, duas partes de imagens com 5.000 e 5.015 JPEGs, metadata com 8 variáveis e 10.015 observações. A página também disponibiliza publicamente o teste ISIC 2018 Task 3 (1.511 imagens e ground truth publicado em 2023), além de segmentações e arquivos de apoio. Os MD5 observados foram `4639bfa73ab251610530a97c898e6e46` para a parte 1, `da43d6cc50f6613013be07e8986b384b` para a parte 2 e `0488b6f65849e310857d9207daa55a21` para o ZIP de teste ISIC. A página aponta para termos customizados do dataset; a licença precisa ser lida diretamente antes do download automatizado.

A página canônica do DDI confirma que as imagens são de 656 casos e 570 pacientes únicos, com rótulos baseados em revisão de patologia e tons Fitzpatrick I–VI, e explica que o conjunto foi desenhado para comparação entre Fitzpatrick I–II e V–VI. O Research Use Agreement permite somente pesquisa pessoal não comercial, exige registro individual, proíbe distribuir ou publicar cópias, proíbe compartilhar o link de download, proíbe reidentificação e declara uso exclusivamente não clínico. Por isso, o DDI será tratado como validação local opcional, fora do Git e fora do treinamento, condicionado ao aceite individual do usuário no portal Stanford AIMI.

## Confirmação direta no Dataverse

A página do HAM10000 na versão 4.0 confirma que o contrato exibido é **Custom Dataset Terms**, não uma licença Creative Commons genérica visível na página. Os arquivos públicos listados são as duas partes de imagens, metadata tabular, segmentações, ground truth e imagens do teste ISIC 2018. Os tamanhos e hashes MD5 completos confirmados na extração foram: parte 1, 1,3 GB, `4639bfa73ab251610530a97c898e6e46`; parte 2, 1,3 GB, `da43d6cc50f6613013be07e8986b384b`; ISIC 2018 Task 3 test images, 401,5 MB, `0488b6f65849e310857d9207daa55a21`; segmentações, 10,3 MB, `6e8d252e09cfdb0189199f15985a5b84`. A página mostra os itens como públicos e indica o botão de acesso/aceite por arquivo. Antes de baixar os ZIPs, é necessário abrir os termos e confirmar o aceite correspondente; o repositório não deve redistribuir as imagens brutas.
