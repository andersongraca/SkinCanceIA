# Revisão da dissertação para a defesa do mestrado

**Projeto:** SkinCancerCADDermoIA
**Documento auditado:** `Defesa.pdf`
**Parecer considerado:** Parecer de Avaliação do Exame de Qualificação, emitido pelo Prof. Dr. Charles Godoy
**Data da revisão:** 24 de setembro de 2026

> **Nota de uso.** Este documento não substitui o arquivo-fonte da dissertação. Ele registra as correções necessárias e fornece trechos prontos para serem incorporados ao `.tex` ou ao editor utilizado na redação final. As passagens novas estão em **negrito** somente para facilitar a identificação durante a revisão; o negrito deve ser removido na versão definitiva, salvo quando exigido pelo padrão do programa.

## 1. Diagnóstico geral

A versão `Defesa.pdf` apresenta mérito científico e já contém uma descrição substancial do sistema implementado. Entretanto, o texto ainda mistura três momentos distintos da pesquisa: a proposta originalmente planejada, o protótipo efetivamente desenvolvido e o plano de continuidade. Essa mistura gera afirmações no futuro do presente sobre atividades que já foram executadas, além de manter referências à interface Django e ao dataset ISIC-2019, embora a implementação descrita no Capítulo 5 utilize React, TypeScript, Express, tRPC e o experimento principal no HAM10000.

O parecer da banca é procedente em dois pontos. Primeiro, há uma necessidade real de revisão estrutural do Capítulo 2 e do protocolo da revisão sistemática. A auditoria textual da versão da defesa confirmou a existência de conteúdo tematicamente repetido, uma numeração duplicada no protocolo e termos que precisam ser corrigidos. A comparação automática entre as seções não identificou cópias literais extensas na versão atualmente extraída; portanto, a redação mais precisa para a defesa é que existem **sobreposições e organização inadequada**, e não que todo o conteúdo esteja necessariamente duplicado palavra por palavra.

Segundo, a preocupação clínica sobre representatividade demográfica deve ser incorporada como limitação central. HAM10000 e ISIC são bases importantes para o desenvolvimento computacional, mas não fornecem, no protocolo atual, evidência suficiente para afirmar desempenho uniforme entre fototipos, populações miscigenadas, modalidades de aquisição e apresentações acrais. A dissertação deve responder à pergunta da banca com uma combinação de discussão científica, declaração explícita de limitação e plano de validação externa. Não é adequado afirmar que o sistema já foi validado para a população brasileira se essa validação ainda não foi realizada.

## 2. Correções obrigatórias identificadas no PDF da defesa

| Local | Problema | Correção recomendada | Prioridade |
|---|---|---|---|
| Capítulo 2 | Sobreposição entre datasets, CNNs, Transformers e Machine Learning | Reorganizar as seções por função: bases de dados, CNNs, ViTs, aplicações em câncer de pele, híbridos, desafios e métricas. Remover repetições conceituais. | Obrigatória |
| Seção 2.8.1 | O parecer registra “promissula” | Procurar o termo no arquivo-fonte e substituir por “promissora”. Na versão extraída do PDF, o termo não foi encontrado; a checagem ainda deve ser feita no `.tex`. | Obrigatória |
| Agradecimentos | O parecer registra “padastro” | Substituir por “padrasto”, caso o termo ainda esteja presente no arquivo-fonte. | Obrigatória |
| Seção 3.2.1 | “selecionandos”, “citerios”, “exlusão” e “elecionados” | Substituir por “selecionados”, “critérios”, “exclusão” e “selecionados”. | Obrigatória |
| Seções 2.2 e 2.5 | “A pré-processamento” | Substituir por “O pré-processamento”. | Obrigatória |
| Capítulo 3 | Há dois títulos `3.1.2 Critérios de Inclusão e Exclusão` e `3.1.3 Critérios de Inclusão e Exclusão` | Manter `3.1.2 Critérios de Inclusão e Exclusão` para a tabela de critérios e renomear `3.1.3` para `Questões de Pesquisa`. | Obrigatória |
| Seção 3.4 | Uso isolado de `[49]` | Adotar o mesmo padrão bibliográfico do restante do texto. Se o padrão for autor-data, substituir por `(ALI et al., 2025c)` ou pela referência efetivamente correspondente. Se o padrão for BibTeX numérico, usar a chave LaTeX correspondente, sem misturar os estilos. | Obrigatória |
| Capítulo 2 | “100000 Training Images” | Corrigir para “10.000 Training Images” na expansão do acrônimo HAM10000. O conjunto publicado contém 10.015 imagens, não 100.000. | Obrigatória |
| Capítulo 5 | Resíduos de compilação, como `float` e fórmulas fragmentadas | Remover o texto residual, recompilar o documento e revisar as fórmulas no PDF gerado. | Obrigatória |
| Capítulo 4 | Django e ISIC-2019 aparecem como se fossem a implementação final | Diferenciar claramente proposta e implementação. A interface efetiva é React/TypeScript com backend Express/tRPC; o experimento principal implementado utiliza HAM10000. | Obrigatória |
| Capítulo 6 | O plano ainda descreve como futuro o treinamento e a interface já implementados | Reescrever o plano para priorizar validação externa, auditoria demográfica, revisão clínica, documentação e redação final. | Obrigatória |

## 3. Reorganização recomendada para o Capítulo 2

A banca identificou repetição entre as subseções 2.2–2.7. Para eliminar a ambiguidade, recomenda-se manter a seguinte lógica:

1. **2.1 Câncer e lesões de pele:** contexto clínico, principais categorias e necessidade de rastreio.
2. **2.2 Datasets para câncer de pele:** HAM10000, ISIC, limitações de modalidade, anotação, diversidade e validade externa. A discussão de fototipos deve ser iniciada aqui.
3. **2.3 Redes neurais convolucionais:** fundamentos de convolução, campos receptivos, extração local e ResNet como arquitetura de referência.
4. **2.4 Transformers e Vision Transformers:** tokens, autoatenção, dependências globais e requisitos de dados.
5. **2.5 Machine Learning aplicado ao câncer de pele:** síntese de como CNNs, ViTs e técnicas de transferência são utilizadas na literatura. Esta seção não deve repetir a explicação matemática das seções 2.3 e 2.4.
6. **2.5.1 Arquiteturas híbridas:** integração entre características locais e contexto global.
7. **2.6 Desafios de dados e estratégias de generalização:** desequilíbrio, ruído de rótulo, mudança de domínio, fototipos sub-representados e validação externa.
8. **2.7 Desempenho e estado da arte:** comparação crítica dos trabalhos, sem transformar resultados de bases diferentes em uma classificação direta de superioridade.
9. **2.8 Métricas de avaliação:** acurácia, sensibilidade, especificidade, precisão, F1, AUROC, AUPRC, calibração e intervalos de confiança.

A tabela comparativa do Capítulo 2 deve informar, sempre que possível, a base utilizada, a modalidade da imagem, o número de classes, a divisão dos pacientes ou lesões, a métrica reportada e a existência de validação externa. Resultados de bases diferentes não devem ser ordenados como se fossem diretamente comparáveis.

## 4. Texto pronto para responder à observação clínica da banca

### 4.1 Inserção sugerida na seção de datasets

**Embora HAM10000 e ISIC sejam referências consolidadas para o desenvolvimento e a comparação de métodos computacionais em imagens dermatológicas, a sua utilização não autoriza presumir representatividade demográfica ou validade clínica universal. O HAM10000 reúne 10.015 imagens dermatoscópicas provenientes de diferentes fontes e modalidades de aquisição, mas o metadata utilizado neste trabalho não contém, de forma validada e completa, o fototipo de Fitzpatrick de cada imagem. Consequentemente, não é possível inferir a distribuição de tons de pele da amostra nem afirmar que as métricas obtidas no teste interno sejam equivalentes entre diferentes grupos populacionais. A base deve ser tratada como um benchmark de classificação dermatoscópica, e não como uma amostra representativa da população brasileira \cite{ref_44, ref_42}.**

**Essa distinção é particularmente importante porque a performance de um modelo pode refletir a distribuição dos dados de treinamento, além das características da doença. O estudo que apresentou o conjunto DDI avaliou imagens clinicamente selecionadas e confirmadas por patologia em diferentes grupos de fototipo e observou limitações relevantes dos modelos previamente treinados, sobretudo em imagens de pele escura e em doenças menos frequentes. O mesmo estudo mostrou que o ajuste fino com dados mais diversificados pode reduzir a diferença de desempenho, mas não elimina a necessidade de uma avaliação independente. O Fitzpatrick17k também demonstrou a utilidade de registrar o fototipo e de avaliar se o desempenho é maior em tipos de pele semelhantes àqueles presentes no treinamento \cite{ref_40, ref_41, ref_42}.**

**No contexto brasileiro, o PAD-UFES-20 oferece uma oportunidade de validação externa porque foi coletado no Espírito Santo com imagens clínicas de smartphones, metadados do paciente e informações de fototipo. A base reúne 2.298 imagens, 1.641 lesões e 1.373 pacientes, incluindo diagnósticos de câncer confirmados por biópsia. Entretanto, suas imagens clínicas não são equivalentes às imagens dermatoscópicas do HAM10000. Por essa razão, o PAD-UFES-20 deve ser utilizado inicialmente para medir mudança de domínio e validade externa, e não incorporado diretamente ao treinamento sem um protocolo específico de harmonização, particionamento por paciente e controle de possíveis duplicidades \cite{ref_39, ref_44}.**

### 4.2 Inserção sugerida na seção de limitações

**A principal limitação demográfica do experimento é a ausência de uma auditoria estratificada por fototipo no conjunto principal. A classificação de uma imagem como pertencente a uma determinada fonte ou dataset não equivale à identificação do tom de pele do paciente. Além disso, a escala de Fitzpatrick é útil para organizar a análise, mas não representa sozinha toda a diversidade fenotípica da população. Assim, os resultados apresentados neste trabalho devem ser interpretados como evidência de funcionamento e desempenho interno no domínio experimental escolhido, e não como prova de equidade ou de generalização para a população brasileira.**

**Também não foi realizada uma avaliação específica de lesões acrais em palmas, plantas ou unidade ungueal. Essa lacuna é clinicamente relevante porque estudos brasileiros descrevem características epidemiológicas, dermoscópicas e histopatológicas particulares no melanoma acral, uma condição para a qual ainda há escassez de dados nacionais. Portanto, a dissertação não deve afirmar que o sistema reconhece adequadamente apresentações acrais; deve registrar essa avaliação como uma tarefa futura que exige um subconjunto externo com localização anatômica, diagnóstico confiável e número suficiente de casos \cite{ref_43}.**

### 4.3 Inserção sugerida na seção de auditoria do sistema

**A auditoria de representatividade deve ser realizada em duas etapas. Na primeira, o teste HAM10000 permanece congelado e é utilizado somente para a avaliação interna previamente definida. Na segunda, o sistema é avaliado em bases externas, preferencialmente PAD-UFES-20, DDI e Fitzpatrick17k, sem alterar os pesos antes do registro dos resultados de baseline. Para cada base, devem ser informados a modalidade da imagem, a origem, o número de pacientes e lesões, a distribuição diagnóstica, a disponibilidade de fototipo, a sensibilidade, a especificidade, a AUROC, a AUPRC, o F1-score, a calibração, a taxa de abstenção e os intervalos de confiança. Quando um subgrupo tiver poucos exemplos, o resultado deve ser apresentado como exploratório, sem afirmação de equivalência ou de ausência de viés \cite{ref_39, ref_40, ref_41}.**

## 5. Correção conceitual do Capítulo 4

A seção de proposta deve permanecer como registro histórico do que foi planejado, mas precisa ser seguida por uma frase de transição para evitar que o leitor confunda planejamento com resultado. Recomenda-se acrescentar ao final do Capítulo 4:

**A proposta descrita neste capítulo foi posteriormente materializada em um protótipo acadêmico, mas algumas decisões de implementação diferiram do planejamento inicial. A interface final foi desenvolvida com React e TypeScript, o backend utiliza Express e tRPC, o experimento principal de classificação foi conduzido com o HAM10000 e o ISIC 2016 foi empregado em um módulo auxiliar de localização para os mapas de explicabilidade. A descrição da implementação efetiva, dos testes e das limitações é apresentada no Capítulo 5.**

No Capítulo 4, as expressões “serão implementados”, “será desenvolvida” e “será realizada” podem permanecer quando o objetivo for descrever a proposta original. Porém, depois da apresentação dos resultados, não se deve utilizar o Capítulo 4 para declarar que essas atividades ainda não ocorreram. O Capítulo 5 deve ser a fonte autoritativa para o que foi realmente executado.

## 6. Correção do Capítulo 5

O Capítulo 5 já contém uma descrição mais consistente do protótipo. Para a versão da defesa, devem ser aplicadas as seguintes correções:

- manter a distinção entre classificação e explicabilidade;
- declarar que o gate auxiliar restringe os mapas e não altera a classe prevista;
- substituir qualquer menção residual a Django por React/TypeScript quando o texto estiver descrevendo a implementação efetiva;
- substituir qualquer menção residual a ISIC-2019 como base principal por HAM10000, deixando ISIC-2016 apenas na função de segmentação auxiliar quando essa for a descrição correta;
- remover `float`, fórmulas quebradas e palavras coladas produzidas pela conversão para PDF;
- corrigir a frase “A pré-processamento” para “O pré-processamento”;
- manter as métricas do sistema identificadas como avaliação interna, sem apresentá-las como desempenho clínico;
- manter a afirmação de que os mapas são explicações aproximadas e não máscaras clínicas ou prova de causalidade;
- manter a limitação de que o gate de localização foi treinado em uma base diferente daquela utilizada na classificação.

A versão editável atual do projeto já contém uma discussão de representatividade demográfica e validade externa. Essa discussão deve ser incorporada ao arquivo-fonte da dissertação, e não deixada somente na documentação do software.

## 7. Reescrita do plano de continuidade do mestrado

O plano de continuidade da versão da defesa está desatualizado porque descreve como futuras a implementação dos modelos, a interface Django e os testes que já foram realizados. Recomenda-se substituir o texto por uma agenda de fechamento do mestrado:

**Após a implementação do protótipo, as etapas remanescentes concentram-se na validação externa, na auditoria de representatividade, na revisão clínica e na consolidação da dissertação. Inicialmente, o conjunto de teste interno do HAM10000 será mantido congelado. Em seguida, serão organizadas avaliações independentes em bases com características distintas, incluindo imagens clínicas brasileiras e bases com metadados de fototipo. Essa etapa permitirá medir mudança de domínio e verificar se as métricas internas se mantêm quando variam a população, o equipamento, a iluminação e a modalidade da imagem.**

**A análise não deverá limitar-se à acurácia. Serão reportadas sensibilidade, especificidade, precisão, F1-score, AUROC, AUPRC, calibração, intervalos de confiança e taxa de abstenção. Quando houver metadados suficientes, os resultados serão estratificados por fototipo, diagnóstico, localização anatômica e modalidade de aquisição. Os casos acrais serão tratados como uma análise específica, sem extrapolar resultados de outras localizações.**

**Depois do registro dos resultados de baseline, poderá ser avaliado o ajuste fino com dados diversificados. Qualquer alteração dos pesos deverá ser acompanhada por novo particionamento por paciente, controle de duplicidades, documentação de licenças e comparação com o baseline congelado. O objetivo não será maximizar uma única métrica, mas avaliar o equilíbrio entre desempenho, calibração, segurança operacional, transparência e aplicabilidade ao contexto brasileiro.**

**Por fim, serão concluídas a revisão ortográfica e estrutural, a conferência das referências, a organização das figuras, a descrição das limitações, a revisão por especialista em dermatologia e a redação da conclusão. O sistema continuará sendo apresentado como protótipo de apoio à pesquisa, e não como dispositivo diagnóstico autônomo.**

## 8. Referências adicionais a incorporar

As referências abaixo devem ser adicionadas à bibliografia da dissertação caso ainda não estejam presentes. No arquivo BibTeX do projeto, podem ser associadas às chaves `ref_39` a `ref_44`, preservando a numeração já utilizada no Capítulo 5.

**ref_39 — PAD-UFES-20**

PACHECO, A. G. C. et al. PAD-UFES-20: a skin lesion dataset composed of patient data and clinical images collected from smartphones. *Data in Brief*, v. 32, p. 106221, 2020. DOI: 10.1016/j.dib.2020.106221.

**ref_40 — DDI**

DANESHJOU, R. et al. Disparities in dermatology AI performance on a diverse, curated clinical image set. *Science Advances*, v. 8, n. 31, eabq6147, 2022. DOI: 10.1126/sciadv.abq6147.

**ref_41 — Fitzpatrick17k**

GROH, M. et al. Evaluating deep neural networks trained on clinical images in dermatology with the Fitzpatrick 17k dataset. In: *2021 IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops*. [S.l.]: IEEE, 2021. p. 1820–1828. DOI: 10.1109/CVPRW53098.2021.00201.

**ref_42 — revisão sobre diversidade de fototipos**

ALIPOUR, N.; BURKE, T.; COURTNEY, J. Skin type diversity in skin lesion datasets: a review. *Current Dermatology Reports*, v. 13, n. 3, p. 198–210, 2024. DOI: 10.1007/s13671-024-00440-0.

**ref_43 — melanoma acral em coorte brasileira**

GARCIA, L. C.; GONTIJO, J. R. V.; BITTENCOURT, F. V. Plantar acral melanoma: epidemiological, clinical, dermoscopic and histopathological features. A Brazilian cohort. *Anais Brasileiros de Dermatologia*, v. 100, n. 1, p. 45–53, 2025. DOI: 10.1016/j.abd.2024.03.006.

**ref_44 — HAM10000**

TSCHANDL, P. et al. The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions. *Scientific Data*, v. 5, p. 180161, 2018. DOI: 10.1038/sdata.2018.161.

No texto em formato autor-data, as chamadas correspondentes podem ser redigidas como `(PACHECO et al., 2020)`, `(DANESHJOU et al., 2022)`, `(GROH et al., 2021)`, `(ALIPOUR; BURKE; COURTNEY, 2024)`, `(GARCIA; GONTIJO; BITTENCOURT, 2025)` e `(TSCHANDL et al., 2018)`. No Capítulo 5 em formato LaTeX numerado, manter as chamadas `\cite{ref_39}`, `\cite{ref_40}`, `\cite{ref_41}`, `\cite{ref_42}`, `\cite{ref_43}` e `\cite{ref_44}` de acordo com o arquivo `.bib` efetivamente utilizado.

## 9. Texto final sobre a implementação do avaliador externo

**Para responder à limitação de representatividade identificada na qualificação, foi implementado no código-fonte um avaliador externo estratificado, separado do módulo de treinamento. O avaliador recebe um manifesto autorizado contendo o caminho da imagem, o diagnóstico, o identificador do paciente, o identificador da lesão, o fototipo ou outra anotação de tom de pele e a localização anatômica. A implementação não infere fototipo a partir dos pixels, pois uma estimativa automática de cor não equivale a um rótulo clínico validado. O protocolo foi estruturado para avaliar os checkpoints treinados no HAM10000 em dados externos, preservando o teste interno e registrando a modalidade de aquisição e a disponibilidade dos metadados \cite{ref_39, ref_40, ref_41, ref_42, ref_44}.**

**O avaliador calcula métricas globais e estratificadas por fototipo, tom de pele, diagnóstico, localização anatômica e demais metadados disponíveis. São registradas acurácia, acurácia balanceada, precisão, sensibilidade, especificidade, F1-score, AUROC, AUPRC, erro esperado de calibração, taxa de abstenção, matriz de confusão e suporte de cada subgrupo. O módulo também verifica duplicidades por paciente e por lesão, preserva as previsões por imagem e marca como exploratórios os subgrupos com suporte reduzido ou apenas uma classe.**

**A implementação do avaliador não deve ser confundida com a conclusão da validação demográfica. O código está preparado para receber os manifestos autorizados de PAD-UFES-20, DDI e Fitzpatrick17k, mas os resultados por fototipo somente devem ser apresentados após a execução com os arquivos originais e a conferência dos respectivos metadados. Para lesões acrais, a análise exige localização anatômica, diagnóstico confiável e suporte suficiente, em razão da escassez de coortes brasileiras específicas \cite{ref_39, ref_40, ref_41, ref_43}.**

O arquivo `ml/evaluate_external.py` contém a implementação e o protocolo de execução está documentado em `docs/EXTERNAL_VALIDATION_PROTOCOL.md`. O bloco BibTeX correspondente está em `docs/REFERENCIAS_DEMOGRAFIA.bib`.

## 10. O que deverá ser implementado no software depois da correção textual

A correção documental deve preceder a alteração dos pesos e do treinamento. A implementação posterior deve seguir este protocolo:

1. **Adicionar um avaliador externo separado do treino**, capaz de ler PAD-UFES-20, DDI e Fitzpatrick17k conforme as licenças e os formatos de cada base.
2. **Preservar o teste HAM10000 congelado** e salvar os resultados de baseline antes de qualquer fine-tuning.
3. **Controlar a unidade paciente–lesão–imagem**, evitando que imagens do mesmo paciente ou da mesma lesão apareçam em treino e teste.
4. **Registrar metadados demográficos e clínicos disponíveis**, sem tentar inferir fototipo automaticamente como se fosse rótulo clínico validado.
5. **Produzir métricas por subgrupo**, incluindo fototipo quando disponível, modalidade de imagem, diagnóstico e localização anatômica.
6. **Incluir uma análise específica de lesões acrais** somente quando existir quantidade e anotação suficientes; caso contrário, registrar a ausência de poder estatístico.
7. **Comparar baseline e fine-tuning**, apresentando intervalos de confiança e diferenças absolutas de desempenho, e não somente a melhor acurácia.
8. **Adicionar calibração e análise de abstenção por subgrupo**, verificando se o mecanismo de incerteza rejeita desproporcionalmente determinados grupos.
9. **Auditar os mapas de explicabilidade separadamente da classificação**, pois o gate auxiliar pode melhorar a visualização sem corrigir viés demográfico ou provar fidelidade clínica.
10. **Submeter o fluxo e os resultados à revisão de um especialista**, deixando claro que a ferramenta é um protótipo de apoio à pesquisa e não um diagnóstico médico autônomo.

## 11. Checklist de entrega para a defesa

- [ ] Remover duplicações e sobreposições desnecessárias do Capítulo 2.
- [ ] Corrigir a numeração duplicada de `3.1.2` e `3.1.3`.
- [ ] Corrigir ortografia, concordância e palavras coladas.
- [ ] Corrigir `100000` para `10000` na descrição do HAM10000.
- [ ] Eliminar `[49]` isolado e padronizar as citações.
- [ ] Recompilar o PDF e conferir fórmulas, acentos e caracteres especiais.
- [ ] Separar claramente proposta, implementação e plano de continuidade.
- [ ] Inserir a discussão sobre fototipos, miscigenação, mudança de domínio e lesões acrais.
- [ ] Adicionar PAD-UFES-20, DDI, Fitzpatrick17k, revisão de diversidade e coorte brasileira de melanoma acral à bibliografia.
- [ ] Não afirmar validação brasileira ou equidade antes de executar a avaliação externa.
- [ ] Reordenar as figuras somente após a versão textual e a compilação final estabilizarem.
- [ ] Realizar a implementação externa no software em uma etapa separada, preservando o baseline.

## Conclusão

A correção mais importante não é apenas trocar palavras ou inserir mais uma base de imagens. É alinhar a narrativa da dissertação ao estágio real do trabalho. O protótipo já foi implementado e testado internamente; a defesa deve apresentar esse resultado com clareza, mas também deve declarar que a generalização para a população brasileira, a análise por fototipo e a avaliação de lesões acrais ainda dependem de validação externa. Essa formulação atende à observação do avaliador médico sem transformar uma hipótese de trabalho em uma conclusão clínica não demonstrada.

A sequência recomendada é: **corrigir o texto e a bibliografia; recompilar e revisar o PDF; depois implementar o avaliador externo no software; somente então avaliar eventual fine-tuning com dados mais diversos.**

## Fontes consultadas

- [HAM10000, Scientific Data, 2018](https://doi.org/10.1038/sdata.2018.161)
- [PAD-UFES-20, Data in Brief, 2020](https://doi.org/10.1016/j.dib.2020.106221)
- [DDI, Science Advances, 2022](https://doi.org/10.1126/sciadv.abq6147)
- [Fitzpatrick17k, CVPR Workshops, 2021](https://doi.org/10.1109/CVPRW53098.2021.00201)
- [Skin Type Diversity in Skin Lesion Datasets: A Review, 2024](https://doi.org/10.1007/s13671-024-00440-0)
- [Plantar acral melanoma: A Brazilian cohort, 2025](https://doi.org/10.1016/j.abd.2024.03.006)
