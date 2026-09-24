# Guia único de correções da dissertação

**Projeto:** SkinCancerCADDermoIA
**Data:** 24 de setembro de 2026
**Finalidade:** reunir, em um único documento, todos os pontos que precisam ser corrigidos na versão da dissertação, com indicação do local e textos prontos para inserção.

## Como utilizar este documento

A sequência abaixo deve ser seguida no arquivo-fonte da dissertação. Os trechos apresentados em **negrito** são textos prontos para serem inseridos ou utilizados como substituição. Depois das alterações, o documento deve ser recompilado e revisado no PDF, especialmente quanto à numeração de figuras, referências cruzadas, citações e quebras de página.

Não é suficiente corrigir apenas o arquivo PDF. O PDF deve ser gerado novamente a partir do arquivo-fonte editável, porque a inserção de parágrafos pode alterar a numeração das figuras, das tabelas e das páginas.

## 1. Correção do resumo

### Local

Substituir o resumo atual, que ainda apresenta o trabalho como proposta e menciona uma interface em Python/Django.

### Texto pronto

**O diagnóstico precoce do câncer de pele, especialmente do melanoma, é relevante para a condução clínica e para a definição de estratégias de acompanhamento. Embora a dermatoscopia seja uma ferramenta de referência para a avaliação de lesões pigmentadas, sua interpretação depende da experiência do examinador e pode apresentar variabilidade entre observadores. Neste contexto, este trabalho apresenta o desenvolvimento e a avaliação interna de um sistema de Diagnóstico Auxiliado por Computador baseado em aprendizado profundo para análise de imagens dermatoscópicas. A solução integra uma rede convolucional baseada em ResNet-50, um Vision Transformer e uma arquitetura híbrida CNN–Transformer, cujas saídas são preservadas individualmente e também combinadas por um agregador calibrado. O pipeline inclui triagem de qualidade e domínio, inferência com aumento em tempo de teste, estimativas operacionais de incerteza, recomendação de abstenção e mapas de explicabilidade. A aplicação foi implementada com módulos científicos em Python e uma interface web baseada em React, TypeScript, Vite, Express e tRPC. O treinamento e o teste interno foram realizados com partições congeladas do HAM10000, enquanto um avaliador externo estratificado foi preparado para comparar o comportamento dos checkpoints em bases com metadados clínicos e de fototipo, como PAD-UFES-20, DDI e Fitzpatrick17k. Os resultados apresentados neste trabalho são internos e funcionais; não constituem validação clínica nem permitem concluir que o sistema tenha desempenho equivalente entre diferentes tons de pele ou populações.**

**Palavras-chave:** Câncer de pele; aprendizado profundo; redes neurais convolucionais; Vision Transformer; diagnóstico auxiliado por computador; explicabilidade; validação externa; diversidade demográfica.

## 2. Correção do abstract

### Local

Substituir o abstract atual, principalmente a expressão “This qualification paper”, a descrição em Python/Django e a ideia de que o sistema ainda será desenvolvido.

### Texto pronto

**This dissertation presents the development and internal evaluation of a deep-learning-based Computer-Aided Diagnosis system for dermoscopic skin-lesion analysis. The implemented pipeline combines a ResNet-50-based convolutional model, a Vision Transformer, and a hybrid CNN–Transformer architecture. Individual predictions are preserved and combined by a calibrated aggregator. The system also includes image-quality and domain screening, test-time augmentation, operational uncertainty estimates, abstention recommendations, and explainability maps. The scientific modules were implemented in Python, whereas the executable web application uses React, TypeScript, Vite, Express, and tRPC. Training and internal testing were conducted on frozen HAM10000 partitions. In response to the demographic-representation limitation, an external stratified evaluator was implemented to assess the trained checkpoints on authorized datasets containing clinical, skin-tone, and anatomical-location metadata, including PAD-UFES-20, DDI, and Fitzpatrick17k. The reported results are internal and functional; they do not constitute clinical validation and do not support claims of equivalent performance across skin tones, populations, or acral presentations.**

## 3. Correção dos objetivos

### Local

Substituir o objetivo geral, que ainda está formulado como se a contribuição fosse apenas comparar dois sistemas.

### Objetivo geral pronto

**Desenvolver e avaliar internamente um sistema de Diagnóstico Auxiliado por Computador para classificação binária de lesões dermatoscópicas, integrando uma CNN baseada em ResNet-50, um Vision Transformer, uma arquitetura híbrida CNN–Transformer e um agregador calibrado, com mecanismos de triagem, incerteza, explicabilidade e auditoria de validade externa.**

### Objetivo específico adicional

Adicionar aos objetivos específicos:

**Implementar um avaliador externo estratificado por fototipo, localização anatômica e demais metadados disponíveis, sem inferir rótulos clínicos a partir da cor dos pixels e sem utilizar dados externos no treinamento antes da avaliação inicial de mudança de domínio.**

Se existir o objetivo específico intitulado “Interface de Demonstração”, substituí-lo por:

**Implementar uma aplicação web executável e auditável para upload, triagem, classificação, visualização dos resultados, consulta das métricas, registro do histórico da sessão e apresentação dos mapas de explicabilidade.**

## 4. Correção da estrutura da dissertação

### Problema encontrado

A versão ajustada afirma que a dissertação possui cinco capítulos, embora o sumário apresente seis. Além disso, o Capítulo 4 e o Capítulo 5 ainda são descritos como proposta e plano de continuidade, apesar de a implementação já existir.

### Texto pronto para a seção “Estrutura da dissertação”

**A dissertação está organizada em seis capítulos. O Capítulo 1 apresenta a introdução, a motivação, o problema de pesquisa, os objetivos e a organização do trabalho. O Capítulo 2 estabelece a fundamentação teórica sobre câncer e lesões de pele, imagens dermatoscópicas, conjuntos de dados, redes convolucionais, Vision Transformers, arquiteturas híbridas, agregação de modelos e explicabilidade. O Capítulo 3 descreve a revisão sistemática da literatura, incluindo o protocolo de busca, os critérios de seleção, a análise dos estudos e as lacunas identificadas. O Capítulo 4 apresenta a concepção e a arquitetura do sistema. O Capítulo 5 descreve o desenvolvimento e a implementação da aplicação, os modelos treinados, o pipeline de inferência, os mecanismos de triagem, a explicabilidade, os testes funcionais, a auditoria, as limitações e o avaliador externo. O Capítulo 6 apresenta os trabalhos futuros, concentrados na validação externa, na análise por subgrupos, na avaliação com especialistas e no aperfeiçoamento metodológico do sistema.**

## 5. Correção da seção de datasets

### Local exato na versão atual da defesa

Inserir o texto na seção **2.2 – Datasets para Câncer de Pele**, depois do parágrafo que termina com:

> “Além desses, outros datasets como o ‘Melanoma Skin Cancer dataset’ são empregados para o desenvolvimento de modelos de diagnóstico precoce (HASAN et al., 2025).”

Esse parágrafo aparece na página 19 do PDF `Defesa_ajustada.pdf`, imediatamente antes do parágrafo que começa com:

> “É importante notar que muitos desses datasets podem apresentar desafios, como o desequilíbrio de classes...”

Portanto, o texto novo deve entrar **entre esses dois parágrafos**, antes da discussão sobre desequilíbrio de classes, pré-processamento, aumento de dados e modelos de difusão.

### Atenção: não deixar o texto duplicado

A versão atual da defesa já possui uma discussão demográfica posterior, iniciada pelo parágrafo **“Embora HAM10000 e ISIC sejam referências consolidadas...”**, nas páginas 20–22. Para evitar repetição, faça uma destas duas opções:

1. **Opção recomendada:** substitua o bloco posterior, desde “Embora HAM10000 e ISIC sejam referências consolidadas...” até o parágrafo que termina com “modalidade de aquisição”, pelo texto novo abaixo, mantendo a discussão demográfica somente no ponto indicado acima; ou
2. Mova o bloco posterior para o ponto indicado acima e ajuste suas citações para o padrão `\cite{ref_...}`.

Não mantenha os dois blocos completos, porque a seção ficará repetitiva e a mesma limitação será discutida duas vezes.

### Texto pronto

**Apesar de sua relevância para o desenvolvimento de métodos de análise de imagens dermatoscópicas, HAM10000 e ISIC não devem ser tratados como representações completas da diversidade clínica e demográfica da população brasileira. O HAM10000 reúne 10.015 imagens dermatoscópicas provenientes de diferentes fontes e modalidades de aquisição, com mais de metade das lesões confirmadas por patologia, mas não foi construído como um estudo de prevalência populacional nem como uma base estratificada por fototipo de Fitzpatrick \cite{ref_44}. Consequentemente, uma métrica elevada nesse conjunto caracteriza o comportamento do modelo em uma distribuição específica de imagens e não garante desempenho equivalente em outros tons de pele, modalidades de aquisição ou localizações anatômicas.**

**Essa limitação é relevante porque a ausência de metadados confiáveis de tipo de pele dificulta a avaliação de equidade. Revisões recentes mostram que muitos conjuntos de dados dermatológicos não informam de maneira verificável a distribuição dos tipos de pele e que a sub-representação de grupos pode produzir diferenças de desempenho entre fototipos. Além disso, etnia, nacionalidade e tipo de pele não são variáveis equivalentes; por isso, a avaliação deve utilizar os metadados efetivamente disponíveis e descrever como foram obtidos \cite{ref_42}.**

**Para aproximar a avaliação do contexto brasileiro, o PAD-UFES-20 é uma fonte externa pertinente por reunir imagens clínicas obtidas por smartphones no Espírito Santo, dados de pacientes e informações clínicas que incluem o tipo de pele de Fitzpatrick. O conjunto contém 2.298 imagens, 1.641 lesões e 1.373 pacientes, com confirmação por biópsia para os casos de câncer descritos na base. Entretanto, suas imagens clínicas não possuem a mesma distribuição das imagens dermatoscópicas do HAM10000. Assim, o PAD-UFES-20 deve ser utilizado inicialmente como conjunto externo de mudança de domínio, mantendo o teste interno do HAM10000 congelado e evitando a mistura direta das bases antes da avaliação independente \cite{ref_39}.**

**A avaliação deve ser complementada por bases com diversidade de tons de pele e, quando possível, confirmação patológica. O DDI foi construído para permitir a comparação de imagens de diferentes grupos de fototipo e evidenciou limitações de algoritmos de dermatologia em tons de pele mais escuros e em doenças incomuns. O Fitzpatrick17k, por sua vez, fornece anotações de fototipo em imagens clínicas e mostra a importância de verificar se os tipos de pele presentes no teste são semelhantes aos observados no treinamento \cite{ref_40, ref_41}. Esses estudos não fornecem uma métrica automaticamente transferível para o sistema desenvolvido, mas fundamentam a necessidade de uma avaliação externa estratificada.**

## 6. Correção da discussão sobre população brasileira e lesões acrais

### Local

Inserir na seção de limitações ou na seção de validade externa do Capítulo 5, depois da apresentação das métricas internas do HAM10000.

### Texto pronto

**A observação da banca sobre a representatividade demográfica constitui uma limitação central do experimento, e não apenas uma possibilidade de melhoria de desempenho. O fato de HAM10000 e ISIC serem referências importantes para a computação em imagens dermatológicas não significa que seus resultados possam ser generalizados automaticamente para todas as populações, modalidades de aquisição ou apresentações clínicas. Em particular, a ausência de metadados validados de tom de pele no experimento principal impede uma auditoria direta por fototipo e impede concluir que a acurácia medida no teste HAM10000 seja equivalente entre diferentes grupos populacionais \cite{ref_44, ref_42}.**

**A questão das lesões acrais também precisa ser formulada com cautela. O protocolo atual não foi desenhado para medir especificamente o desempenho em lesões de palmas, plantas ou unidade ungueal em uma população brasileira. Portanto, não se deve afirmar que o sistema reconhece adequadamente essas apresentações nem que a distribuição do HAM10000 seja suficiente para representá-las. A resposta experimental exige um subconjunto externo com localização anatômica registrada, diagnóstico confiável e quantidade suficiente de casos acrais, além da apresentação de métricas separadas para esse grupo.**

**Essa lacuna possui relevância clínica no contexto nacional. Uma coorte brasileira de melanoma acral descreveu 48 casos e destacou a escassez de dados brasileiros sobre as características epidemiológicas, clínicas, dermoscópicas e histopatológicas dessa apresentação. O estudo não permite inferir o desempenho do sistema desenvolvido, mas justifica a inclusão de localização anatômica e diagnóstico confirmado no protocolo de validação externa \cite{ref_43}.**

## 7. Descrição correta da implementação externa

### Local

Inserir no Capítulo 5, na subseção de implementação, depois da descrição da triagem e antes das limitações finais.

### Texto pronto

**Para responder à limitação de representatividade identificada na qualificação, foi implementado um avaliador externo estratificado, separado do módulo de treinamento. O avaliador recebe um manifesto autorizado contendo o caminho da imagem, o diagnóstico, o identificador do paciente, o identificador da lesão, o fototipo ou outra anotação de tom de pele e a localização anatômica. A implementação não infere fototipo a partir dos pixels, pois uma estimativa automática de cor não equivale a um rótulo clínico validado. O protocolo preserva o teste interno do HAM10000 e registra a modalidade de aquisição e a disponibilidade dos metadados \cite{ref_39, ref_40, ref_41, ref_42, ref_44}.**

**A avaliação externa é executada antes de qualquer ajuste fino. Para cada base e subgrupo, o sistema registra suporte, acurácia, acurácia balanceada, precisão, sensibilidade, especificidade, F1-score, AUROC, AUPRC, erro esperado de calibração e taxa de abstenção. Também são preservados os resultados por imagem, a matriz de confusão e as verificações de duplicidade por paciente e por lesão. Quando um subgrupo possui poucos casos ou apenas uma classe, o resultado é marcado como exploratório e as métricas indefinidas não são substituídas por valores artificiais.**

**A existência do avaliador no código-fonte não significa que a classificação já esteja validada para todos os fototipos ou para a população brasileira. Os resultados demográficos somente devem ser incorporados à dissertação depois da execução com os arquivos autorizados das bases externas, da conferência dos metadados e da análise do suporte de cada subgrupo. Para lesões acrais, a análise exige localização anatômica registrada, diagnóstico confiável e quantidade suficiente de casos para produzir métricas independentes \cite{ref_43}.**

## 8. Substituições pontuais no texto atual

Realizar as seguintes substituições:

1. Trocar **“Este trabalho de qualificação”** por **“Esta dissertação”**.

1. Trocar **“protótipo funcional, com interface em Python/Django”** por **“sistema funcional, com módulos científicos em Python/PyTorch e aplicação web em React, TypeScript, Vite, Express e tRPC”**.

1. Trocar **“utilizando o dataset ISIC-2019”**, quando estiver descrevendo o sistema já executado, por **“utilizando o HAM10000 para o treinamento e teste interno, além do ISIC 2016 para o treinamento do localizador auxiliar”**.

1. Corrigir `ISIC0 027419...` para: **“A primeira execução foi realizada com a imagem `ISIC_0027419.jpg`, utilizada como exemplo dermatoscópico.”**

1. Corrigir o trecho corrompido do teste OOD para: **“Como teste de controle, foi utilizada uma imagem não dermatológica. A triagem retornou o motivo `outside_dermoscopy_domain` e impediu que a imagem fosse encaminhada aos modelos.”**

1. Corrigir **“classificação.O uso”** para **“classificação. O uso”**.

1. Corrigir **“Por fim a leitura completa dos artigos elecionados”** para **“Por fim, realizou-se a leitura completa dos artigos selecionados.”**

1. Corrigir a apresentação do dataset para **“HAM10000 (Human Against Machine with 10,000 training images)”**.

1. Remover qualquer linha exposta no PDF que contenha comandos de compilação, como `article [utf8]inputenc [brazil]babel...`.

1. Conferir a Figura 5.7 após a recompilação. Ela deve mostrar a tabela e o gráfico comparativo.

1. Corrigir referências internas que ainda apontam para a Figura 9, quando a numeração final do Capítulo 5 utilizar Figuras 5.7, 5.8, 5.9 e seguintes.

## 9. Capítulo 6 pronto: Trabalhos futuros

### Orientação

Substituir integralmente o capítulo atual de plano de continuidade pelo texto abaixo. O capítulo deve apresentar uma agenda de pesquisa futura, sem afirmar que essas atividades já foram realizadas e sem associá-las a qualquer etapa acadêmica específica.

# 6 Trabalhos futuros

**O sistema desenvolvido constitui um protótipo acadêmico funcional para classificação de lesões dermatoscópicas. A avaliação realizada até o momento demonstra a integração entre modelos, triagem, inferência, explicabilidade e interface, mas ainda não é suficiente para sustentar conclusões gerais sobre desempenho clínico, equidade entre tons de pele ou comportamento em diferentes populações. Os trabalhos futuros devem, portanto, ampliar a validade externa, aprofundar a análise metodológica e aproximar a avaliação das condições encontradas na prática dermatológica.**

## 6.1 Validação externa e mudança de domínio

**A primeira frente de investigação consiste em executar o avaliador externo com bases autorizadas que apresentem características diferentes das imagens utilizadas no desenvolvimento. O PAD-UFES-20 deverá ser utilizado para avaliar a mudança entre imagens dermatoscópicas e imagens clínicas obtidas por smartphones. O DDI e o Fitzpatrick17k poderão complementar essa análise por apresentarem informações relacionadas à diversidade de tons de pele e às condições dermatológicas observadas. O conjunto de teste interno do HAM10000 deverá permanecer congelado, funcionando como referência para a comparação entre o desempenho interno e o desempenho externo \cite{ref_39, ref_40, ref_41, ref_44}.**

**A análise deverá registrar a modalidade de aquisição, a distribuição das classes, o número de pacientes, o número de lesões e a quantidade de imagens por grupo. A utilização de identificadores de paciente e de lesão será necessária para reduzir o risco de vazamento de informação entre treinamento, validação e teste.**

## 6.2 Avaliação por fototipo e diversidade demográfica

**Uma segunda frente consiste em avaliar o desempenho segundo os metadados demográficos disponíveis. As métricas deverão ser calculadas separadamente para cada grupo de fototipo com suporte suficiente, incluindo acurácia, acurácia balanceada, sensibilidade, especificidade, F1-score, AUROC, AUPRC, calibração e taxa de abstenção. Os intervalos de confiança deverão ser apresentados sempre que o tamanho amostral permitir \cite{ref_40, ref_41, ref_42}.**

**A análise não deverá transformar diferenças observadas em conclusões causais. Um resultado discrepante pode estar relacionado à quantidade de casos, à distribuição dos diagnósticos, à modalidade de imagem, à qualidade da aquisição ou à própria anotação do fototipo. Por essa razão, a origem do metadado, o método de anotação e o suporte de cada grupo deverão acompanhar as métricas. Quando houver poucos casos, o resultado deverá ser descrito como exploratório.**

## 6.3 Avaliação específica de lesões acrais

**Outra linha de investigação consiste em construir ou obter um subconjunto com localização anatômica registrada para palmas, plantas e unidade ungueal. Esse subconjunto deverá conter diagnóstico confiável e, sempre que possível, confirmação histopatológica. O desempenho em lesões acrais deverá ser apresentado separadamente do desempenho global, pois a distribuição visual, a ausência de pelos e os padrões dermoscópicos dessas regiões podem diferir daqueles observados em outras áreas do corpo \cite{ref_43}.**

**A análise deverá incluir o número de casos benignos e malignos, a distribuição dos fototipos, a modalidade de aquisição, os padrões clínicos ou dermoscópicos disponíveis e a proporção de casos rejeitados pela triagem de qualidade. Não se deverá concluir que o sistema é adequado para lesões acrais apenas com base nos resultados do HAM10000.**

## 6.4 Aperfeiçoamento dos modelos e da calibração

**A arquitetura atual poderá ser aperfeiçoada mediante experimentos controlados de balanceamento, calibração e seleção de hiperparâmetros. Cada alteração deverá ser comparada com o baseline congelado, utilizando o mesmo particionamento de teste e evitando que o conjunto externo seja utilizado para selecionar decisões de treinamento.**

**Também poderão ser avaliadas estratégias de reamostragem, funções de perda sensíveis ao custo, calibração por temperatura, combinação de modelos com pesos estimados em validação independente e técnicas de aumento de dados compatíveis com a morfologia das lesões. Essas estratégias deverão ser comparadas não apenas pela acurácia, mas também pela sensibilidade, especificidade, AUPRC, calibração, taxa de abstenção e estabilidade entre grupos.**

## 6.5 Avaliação da explicabilidade

**Os mapas de explicabilidade deverão ser avaliados além da inspeção visual. A análise futura deverá investigar estabilidade diante de pequenas transformações da imagem, fidelidade em relação à saída do modelo, sensibilidade à região da lesão e concordância com avaliações de especialistas. Grad-CAM, atribuição de tokens, gradiente da entrada e mapas agregados deverão ser comparados sob um protocolo comum, considerando que esses métodos são explicações aproximadas e não máscaras clínicas \cite{ref_33}.**

**Os resultados deverão manter a distinção entre uma visualização de atribuição e uma máscara clínica. Um mapa colorido pode indicar regiões que influenciaram a saída numérica do modelo, mas não prova que a região seja biologicamente causal ou clinicamente suficiente para justificar a decisão.**

## 6.6 Avaliação com especialistas e utilidade do sistema

**Uma etapa posterior deverá avaliar a utilidade da aplicação com dermatologistas ou profissionais habilitados. Essa avaliação poderá comparar a interpretação de imagens com e sem os mapas, verificar se as informações apresentadas são compreensíveis e identificar situações em que a interface favorece uma confiança indevida. O estudo deverá separar a avaliação da usabilidade da avaliação de desempenho diagnóstico.**

**Também será importante investigar se a recomendação de abstenção é compreendida corretamente. A abstenção deve ser apresentada como um sinal de que o sistema não atingiu um critério operacional de confiança ou de domínio, e não como uma confirmação de benignidade ou malignidade.**

## 6.7 Robustez, privacidade e reprodutibilidade

**A robustez do sistema poderá ser investigada com imagens submetidas a variações de iluminação, compressão, foco, resolução, pelos, artefatos e dispositivos de aquisição. O objetivo será verificar se a triagem rejeita entradas inadequadas sem transformar variações aceitáveis em rejeições excessivas.**

**A expansão do sistema também deverá considerar privacidade e segurança. Imagens clínicas e metadados de pacientes deverão ser armazenados apenas quando houver autorização, controle de acesso e justificativa metodológica. Os manifestos utilizados na avaliação deverão evitar informações diretamente identificáveis.**

**Para favorecer a reprodutibilidade, cada experimento deverá registrar a versão do código, a configuração, os checkpoints, a seed, os critérios de inclusão, a origem dos dados, as licenças e os scripts de avaliação. As bases externas não deverão ser baixadas ou redistribuídas automaticamente quando suas condições de acesso não permitirem esse procedimento.**

## 6.8 Síntese dos trabalhos futuros

**A continuidade da pesquisa deverá priorizar a validação externa e a caracterização das limitações antes de qualquer tentativa de apresentar o sistema como ferramenta de uso clínico. O resultado mais importante das próximas etapas não será apenas aumentar uma métrica global, mas verificar se o comportamento do modelo permanece aceitável quando mudam o fototipo, a modalidade de aquisição, a localização anatômica, o diagnóstico e as condições de imagem. Essa agenda permitirá avaliar a generalização do sistema de forma mais rigorosa e produzir conclusões compatíveis com a diversidade da prática dermatológica.**

## 10. Referências que devem ser acrescentadas à bibliografia principal

Adicionar as referências abaixo à bibliografia principal da dissertação. No texto final, **não utilizar citações autor-data** nos trechos deste guia. Utilizar exclusivamente o padrão do artigo: `\cite{ref_39}`, `\cite{ref_40}`, `\cite{ref_41}`, `\cite{ref_42}`, `\cite{ref_43}` e `\cite{ref_44}`. As chaves devem permanecer exatamente iguais às chaves do arquivo BibTeX.

**PACHECO, Andre G. C. et al. PAD-UFES-20: A skin lesion dataset composed of patient data and clinical images collected from smartphones. Data in Brief, v. 32, art. 106221, 2020. DOI: 10.1016/j.dib.2020.106221.**

**DANESHJOU, Roxana et al. Disparities in dermatology AI performance on a diverse, curated clinical image set. Science Advances, v. 8, n. 31, eabq6147, 2022. DOI: 10.1126/sciadv.abq6147.**

**GROH, Matthew et al. Evaluating Deep Neural Networks Trained on Clinical Images in Dermatology with the Fitzpatrick 17k Dataset. In: 2021 IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops. 2021. p. 1820–1828. DOI: 10.1109/CVPRW53098.2021.00201.**

**ALIPOUR, Neda; BURKE, Ted; COURTNEY, Jane. Skin Type Diversity in Skin Lesion Datasets: A Review. Current Dermatology Reports, v. 13, n. 3, p. 198–210, 2024. DOI: 10.1007/s13671-024-00440-0.**

**GARCIA, Lucas Campos; GONTIJO, João Renato Vianna; BITTENCOURT, Flávia Vasques. Plantar acral melanoma: epidemiological, clinical, dermoscopic and histopathological features. A Brazilian cohort. Anais Brasileiros de Dermatologia, v. 100, n. 1, p. 45–53, 2025. DOI: 10.1016/j.abd.2024.03.006.**

**TSCHANDL, Philipp; ROSENDAHL, Cliff; KITTLER, Harald. The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions. Scientific Data, v. 5, art. 180161, 2018. DOI: 10.1038/sdata.2018.161.**

## 11. Conferência final antes da entrega

- [ ] O resumo foi substituído pelo texto atualizado.

- [ ] O abstract não utiliza mais “qualification paper”.

- [ ] O texto não descreve a interface final como Python/Django.

- [ ] A estrutura informa seis capítulos.

- [ ] O Capítulo 2 contém a discussão sobre HAM10000, ISIC, fototipos e população brasileira.

- [ ] PAD-UFES-20, DDI, Fitzpatrick17k, Alipour et al., Garcia et al. e HAM10000 foram acrescentados à bibliografia.

- [ ] O Capítulo 5 informa que o avaliador externo foi implementado, sem afirmar que os resultados externos já foram concluídos.

- [ ] A discussão de lesões acrais está apresentada como limitação e proposta de avaliação específica.

- [ ] O Capítulo 6 foi substituído pelo texto de trabalhos futuros acima.

- [ ] As referências às figuras foram atualizadas automaticamente após a recompilação.

- [ ] A Figura 5.7 mostra a comparação gráfica das métricas.

- [ ] Os trechos corrompidos do PDF foram corrigidos no arquivo-fonte.

- [ ] As linhas de comandos de compilação foram removidas do texto final.

- [ ] A conclusão não apresenta o sistema como ferramenta clinicamente validada.

- [ ] O PDF final foi lido integralmente depois da recompilação.

## Referências deste guia

[1]: https://doi.org/10.1038/sdata.2018.161 "The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions"

[2]: https://doi.org/10.1016/j.dib.2020.106221 "PAD-UFES-20: A skin lesion dataset composed of patient data and clinical images collected from smartphones"

[3]: https://doi.org/10.1126/sciadv.abq6147 "Disparities in dermatology AI performance on a diverse, curated clinical image set"

[4]: https://doi.org/10.1109/CVPRW53098.2021.00201 "Evaluating Deep Neural Networks Trained on Clinical Images in Dermatology with the Fitzpatrick 17k Dataset"

[5]: https://doi.org/10.1007/s13671-024-00440-0 "Skin Type Diversity in Skin Lesion Datasets: A Review"

[6]: https://doi.org/10.1016/j.abd.2024.03.006 "Plantar acral melanoma: epidemiological, clinical, dermoscopic and histopathological features. A Brazilian cohort"
