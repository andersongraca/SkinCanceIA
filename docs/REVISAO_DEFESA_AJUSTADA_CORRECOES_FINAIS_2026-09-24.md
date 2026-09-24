# Revisão final da Defesa_ajustada.pdf

**Projeto:** SkinCancerCADDermoIA
**Data da auditoria:** 24 de setembro de 2026
**Objetivo:** conferir se as observações do parecer sobre representatividade demográfica, tons de pele, população brasileira e lesões acrais foram incorporadas corretamente, além de identificar o que ainda precisa ser corrigido antes da defesa.

## 1. Parecer geral

A versão ajustada avançou em relação à proposta inicial porque já apresenta um Capítulo 5 intitulado **Desenvolvimento e implementação do sistema**, descreve a execução da ferramenta, registra métricas internas do HAM10000, apresenta testes funcionais, documenta o gate auxiliar de localização e reconhece que o resultado não constitui validação clínica.

Entretanto, a revisão da banca **ainda não está plenamente incorporada na versão da defesa em PDF**. O texto demográfico aparece parcialmente, mas algumas citações utilizadas no corpo não correspondem às fontes adequadas ou não aparecem na bibliografia final. Além disso, a versão em PDF continua contendo trechos da qualificação, como “este trabalho de qualificação”, “protótipo em Python/Django” e “plano de continuidade para a finalização da dissertação”, embora o sistema atualmente implementado utilize Python/PyTorch no módulo científico e React/TypeScript/Express/tRPC na aplicação web.

Há também uma divergência importante entre o arquivo editável atual do Capítulo 5 e o PDF da defesa: o arquivo editável já contém as seções de limitações, representatividade demográfica, avaliador externo e comparação metodológica, mas essas seções não aparecem na versão PDF analisada. Portanto, não basta corrigir o arquivo Markdown ou o código-fonte; é necessário **recompilar a dissertação a partir do fonte LaTeX atualizado e conferir o PDF página a página**.

## 2. O que já foi atendido

| Exigência do parecer | Situação atual | Observação |
| --- | --- | --- |
| Discutir o viés demográfico de HAM10000 e ISIC | Parcialmente atendida | A discussão existe no arquivo editável do Capítulo 5, mas precisa chegar ao PDF final e receber a citação primária do HAM10000. |
| Explicar que desempenho interno não equivale a generalização brasileira | Atendida no texto editável | A formulação está adequada, desde que permaneça como limitação e não como conclusão clínica. |
| Incluir uma base brasileira | Atendida como protocolo | O PAD-UFES-20 foi incorporado como base de avaliação externa planejada, sem misturá-lo automaticamente ao treinamento. |
| Considerar fototipo de Fitzpatrick | Parcialmente atendida | O avaliador externo aceita metadados de fototipo, mas ainda é necessário executar a avaliação com os arquivos autorizados e apresentar os resultados. |
| Considerar doenças e lesões acrais | Parcialmente atendida | A limitação e a necessidade de uma coorte específica estão descritas; ainda não há resultado experimental específico para lesões acrais. |
| Implementar auditoria por subgrupos | Atendida em nível de código | O módulo `ml/evaluate_external.py`, o protocolo e os testes unitários foram adicionados. Isso demonstra prontidão metodológica, não validação externa concluída. |
| Evitar inferir fototipo pela cor dos pixels | Atendida | O avaliador recebe o fototipo a partir de metadados autorizados e não produz um rótulo clínico artificial. |

## 3. Correções obrigatórias na versão da defesa

### 3.1 Resumo

O resumo ainda apresenta o trabalho como uma proposta e afirma que o resultado principal é um protótipo em Python/Django. Para a defesa, o texto deve refletir a implementação realizada. **Substituir o resumo atual pelo texto abaixo:**

**O diagnóstico precoce do câncer de pele, especialmente do melanoma, é relevante para a condução clínica e para a definição de estratégias de acompanhamento. Embora a dermatoscopia seja uma ferramenta de referência para a avaliação de lesões pigmentadas, sua interpretação depende da experiência do examinador e pode apresentar variabilidade entre observadores. Neste contexto, este trabalho apresenta o desenvolvimento e a avaliação interna de um sistema de Diagnóstico Auxiliado por Computador baseado em aprendizado profundo para análise de imagens dermatoscópicas. A solução integra uma rede convolucional baseada em ResNet-50, um Vision Transformer e uma arquitetura híbrida CNN–Transformer, cujas saídas são preservadas individualmente e também combinadas por um agregador calibrado. O pipeline inclui triagem de qualidade e domínio, inferência com aumento em tempo de teste, estimativas operacionais de incerteza, recomendação de abstenção e mapas de explicabilidade. A aplicação foi implementada com módulos científicos em Python e uma interface web baseada em React, TypeScript, Vite, Express e tRPC. O treinamento e o teste interno foram realizados com partições congeladas do HAM10000, enquanto um avaliador externo estratificado foi preparado para comparar o comportamento dos checkpoints em bases com metadados clínicos e de fototipo, como PAD-UFES-20, DDI e Fitzpatrick17k. Os resultados apresentados neste trabalho são internos e funcionais; não constituem validação clínica nem permitem concluir que o sistema tenha desempenho equivalente entre diferentes tons de pele ou populações.**

**Palavras-chave:** Câncer de pele; aprendizado profundo; redes neurais convolucionais; Vision Transformer; diagnóstico auxiliado por computador; explicabilidade; validação externa; diversidade demográfica.

### 3.2 Abstract

O abstract deve ser atualizado de forma equivalente. É necessário remover a expressão **“This qualification paper”**, retirar a descrição de uma interface em Python/Django e declarar que o sistema foi desenvolvido, mas que a validação externa por fototipo ainda depende da execução dos manifestos autorizados.

**This dissertation presents the development and internal evaluation of a deep-learning-based Computer-Aided Diagnosis system for dermoscopic skin-lesion analysis. The implemented pipeline combines a ResNet-50-based convolutional model, a Vision Transformer, and a hybrid CNN–Transformer architecture. Individual predictions are preserved and combined by a calibrated aggregator. The system also includes image-quality and domain screening, test-time augmentation, operational uncertainty estimates, abstention recommendations, and explainability maps. The scientific modules were implemented in Python, whereas the executable web application uses React, TypeScript, Vite, Express, and tRPC. Training and internal testing were conducted on frozen HAM10000 partitions. In response to the demographic-representation limitation, an external stratified evaluator was implemented to assess the trained checkpoints on authorized datasets containing clinical, skin-tone, and anatomical-location metadata, including PAD-UFES-20, DDI, and Fitzpatrick17k. The reported results are internal and functional; they do not constitute clinical validation and do not support claims of equivalent performance across skin tones, populations, or acral presentations.**

### 3.3 Objetivos

O objetivo geral ainda está escrito como se a pesquisa fosse apenas comparar dois sistemas. Como o sistema final possui três componentes e um agregador, recomenda-se substituir o objetivo geral por:

**Desenvolver e avaliar internamente um sistema de Diagnóstico Auxiliado por Computador para classificação binária de lesões dermatoscópicas, integrando uma CNN baseada em ResNet-50, um Vision Transformer, uma arquitetura híbrida CNN–Transformer e um agregador calibrado, com mecanismos de triagem, incerteza, explicabilidade e auditoria de validade externa.**

Nos objetivos específicos, substituir **“Interface de Demonstração”** por **“Aplicação web executável e auditável”** e acrescentar:

**Implementar um avaliador externo estratificado por fototipo, localização anatômica e demais metadados disponíveis, sem inferir rótulos clínicos a partir da cor dos pixels e sem utilizar dados externos no treinamento antes da avaliação inicial de mudança de domínio.**

### 3.4 Estrutura da dissertação

A defesa ajustada afirma que o trabalho possui cinco capítulos, mas o sumário mostra seis capítulos. Também descreve o Capítulo 4 e o Capítulo 5 como proposta e plano de continuidade, respectivamente, apesar de o sistema já ter sido implementado. Substituir toda a seção de estrutura por:

**A dissertação está organizada em seis capítulos. O Capítulo 1 apresenta a introdução, a motivação, o problema de pesquisa, os objetivos e a organização do trabalho. O Capítulo 2 estabelece a fundamentação teórica sobre câncer e lesões de pele, imagens dermatoscópicas, conjuntos de dados, redes convolucionais, Vision Transformers, arquiteturas híbridas, agregação de modelos e explicabilidade. O Capítulo 3 descreve a revisão sistemática da literatura, incluindo o protocolo de busca, os critérios de seleção, a análise dos estudos e as lacunas identificadas. O Capítulo 4 apresenta a concepção e a arquitetura do sistema. O Capítulo 5 descreve o desenvolvimento e a implementação da aplicação, os modelos treinados, o pipeline de inferência, os mecanismos de triagem, a explicabilidade, os testes funcionais, a auditoria, as limitações e o avaliador externo. O Capítulo 6 apresenta o plano de continuidade do mestrado, concentrado na validação externa, na análise por subgrupos, na avaliação com especialistas e na consolidação da redação final.**

## 4. Correção da discussão sobre datasets e população brasileira

### 4.1 Onde inserir

Inserir o texto seguinte no Capítulo 2, imediatamente depois da apresentação do HAM10000 e do ISIC, antes da subseção que inicia a discussão sobre pré-processamento ou arquiteturas. O texto deve ser acompanhado das referências indicadas na Seção 7 deste documento.

**Apesar de sua relevância para o desenvolvimento de métodos de análise de imagens dermatoscópicas, HAM10000 e ISIC não devem ser tratados como representações completas da diversidade clínica e demográfica da população brasileira. O HAM10000 reúne 10.015 imagens dermatoscópicas provenientes de diferentes fontes e modalidades de aquisição, com mais de metade das lesões confirmadas por patologia, mas não foi construído como um estudo de prevalência populacional nem como uma base estratificada por fototipo de Fitzpatrick. Consequentemente, uma métrica elevada nesse conjunto caracteriza o comportamento do modelo em uma distribuição específica de imagens e não garante desempenho equivalente em outros tons de pele, modalidades de aquisição ou localizações anatômicas.**

**Essa limitação é relevante porque a ausência de metadados confiáveis de tipo de pele dificulta a avaliação de equidade. Revisões recentes mostram que muitos conjuntos de dados dermatológicos não informam de maneira verificável a distribuição dos tipos de pele e que a sub-representação de grupos pode produzir diferenças de desempenho entre fototipos. Além disso, etnia, nacionalidade e tipo de pele não são variáveis equivalentes; por isso, a avaliação deve utilizar os metadados efetivamente disponíveis e descrever como foram obtidos.**

**Para aproximar a avaliação do contexto brasileiro, o PAD-UFES-20 é uma fonte externa pertinente por reunir imagens clínicas obtidas por smartphones no Espírito Santo, dados de pacientes e informações clínicas que incluem o tipo de pele de Fitzpatrick. O conjunto contém 2.298 imagens, 1.641 lesões e 1.373 pacientes, com confirmação por biópsia para os casos de câncer descritos na base. Entretanto, suas imagens clínicas não possuem a mesma distribuição das imagens dermatoscópicas do HAM10000. Assim, o PAD-UFES-20 deve ser utilizado inicialmente como conjunto externo de mudança de domínio, mantendo o teste interno do HAM10000 congelado e evitando a mistura direta das bases antes da avaliação independente.**

**A avaliação deve ser complementada por bases com diversidade de tons de pele e, quando possível, confirmação patológica. O DDI foi construído para permitir a comparação de imagens de diferentes grupos de fototipo e evidenciou limitações de algoritmos de dermatologia em tons de pele mais escuros e em doenças incomuns. O Fitzpatrick17k, por sua vez, fornece anotações de fototipo em imagens clínicas e mostra a importância de verificar se os tipos de pele presentes no teste são semelhantes aos observados no treinamento. Esses estudos não fornecem uma métrica automaticamente transferível para o sistema desenvolvido, mas fundamentam a necessidade de uma avaliação externa estratificada.**

## 5. Correção da implementação descrita no Capítulo 5

A parte demográfica do Capítulo 5 está conceitualmente correta no arquivo editável, mas precisa ser incorporada ao PDF da defesa. Manter o texto em tom de implementação, sem afirmar que os resultados externos já foram obtidos.

**Para responder à limitação de representatividade identificada na qualificação, foi implementado um avaliador externo estratificado, separado do módulo de treinamento. O avaliador recebe um manifesto autorizado contendo o caminho da imagem, o diagnóstico, o identificador do paciente, o identificador da lesão, o fototipo ou outra anotação de tom de pele e a localização anatômica. A implementação não infere fototipo a partir dos pixels, pois uma estimativa automática de cor não equivale a um rótulo clínico validado. O protocolo preserva o teste interno do HAM10000 e registra a modalidade de aquisição e a disponibilidade dos metadados.**

**A avaliação externa é executada antes de qualquer ajuste fino. Para cada base e subgrupo, o sistema registra suporte, acurácia, acurácia balanceada, precisão, sensibilidade, especificidade, F1-score, AUROC, AUPRC, erro esperado de calibração e taxa de abstenção. Também são preservados os resultados por imagem, a matriz de confusão e as verificações de duplicidade por paciente e por lesão. Quando um subgrupo possui poucos casos ou apenas uma classe, o resultado é marcado como exploratório e as métricas indefinidas não são substituídas por valores artificiais.**

**A existência do avaliador no código-fonte não significa que a classificação já esteja validada para todos os fototipos ou para a população brasileira. Os resultados demográficos somente devem ser incorporados à dissertação depois da execução com os arquivos autorizados das bases externas, da conferência dos metadados e da análise do suporte de cada subgrupo. Para lesões acrais, a análise exige localização anatômica registrada, diagnóstico confiável e quantidade suficiente de casos para produzir métricas independentes.**

### 5.1 O que já existe no código

A implementação está organizada nos seguintes arquivos:

- `ml/evaluate_external.py`: leitura de manifestos autorizados, inferência com os checkpoints, combinação das probabilidades, métricas globais e métricas por subgrupo;
- `docs/EXTERNAL_VALIDATION_PROTOCOL.md`: protocolo, esquema do manifesto, comando de execução e limites de interpretação;
- `tests/test_external_evaluation.py`: testes de matriz de confusão, calibração, abstenção e tratamento de subgrupo com uma única classe;
- `docs/REFERENCIAS_DEMOGRAFIA.bib`: referências BibTeX numeradas de `ref_39` a `ref_44`.

O código também registra que não infere fototipo a partir dos pixels, não altera os checkpoints e não executa fine-tuning silencioso. Essa decisão deve ser explicada como uma medida de validade metodológica.

### 5.2 O que ainda não pode ser afirmado

Não afirmar que o modelo já foi treinado com PAD-UFES-20, DDI ou Fitzpatrick17k se os arquivos dessas bases não foram efetivamente autorizados, organizados e processados. A formulação correta é que **o avaliador externo foi implementado e está pronto para a execução reprodutível**, enquanto os resultados por fototipo e população brasileira ainda dependem da execução do protocolo.

Também não afirmar que o sistema reconhece lesões acrais com desempenho comprovado. O texto deve dizer que a coorte brasileira de melanoma acral justifica a inclusão de localização anatômica e a criação de um subconjunto específico de avaliação.

## 6. Correções pontuais identificadas no PDF

1. Substituir **“Este trabalho de qualificação”** por **“Esta dissertação”** em resumo, abstract e estrutura.
2. Substituir **“protótipo funcional, com interface em Python/Django”** por uma descrição coerente com a aplicação efetiva: **módulos científicos em Python/PyTorch e aplicação web em React/TypeScript/Vite/Express/tRPC**.
3. Substituir **“utilizando o dataset ISIC-2019”** no plano de continuidade, caso o texto esteja descrevendo o experimento já executado. O treinamento documentado do sistema apresentado utiliza o HAM10000; ISIC 2016 foi utilizado no localizador auxiliar/gate. ISIC-2019 pode permanecer apenas como possibilidade de avaliação ou expansão futura, desde que isso seja explicitado.
4. Corrigir a frase da página 69 que aparece como `ISIC0 027419. j...`. O texto correto é: **“A primeira execução foi realizada com a imagem `ISIC_0027419.jpg`, utilizada como exemplo dermatoscópico.”**
5. Corrigir a frase da imagem fora do domínio que aparece corrompida como `outside...`. O texto correto é: **“Como teste de controle, foi utilizada uma imagem não dermatológica. A triagem retornou o motivo `outside_dermoscopy_domain` e impediu que a imagem fosse encaminhada aos modelos.”**
6. Corrigir a ausência de espaço em **“classificação.O uso”** para **“classificação. O uso”**.
7. Corrigir **“Por fim a leitura completa dos artigos elecionados”** para **“Por fim, realizou-se a leitura completa dos artigos selecionados.”**
8. Corrigir a apresentação do HAM10000 para **“HAM10000 (Human Against Machine with 10,000 training images)”**, com a referência de Tschandl, Rosendahl e Kittler (2018).
9. Conferir a Figura 5.7 no PDF recompilado. A figura deve mostrar a tabela e o gráfico comparativo, e não apenas os eixos ou a legenda.
10. Conferir a numeração das figuras. No PDF, a seção 5.7 cita a Figura 9, enquanto a numeração do próprio capítulo apresenta as figuras como 14, 15, 16 e 17. Após recompilar, substituir todas as referências internas pela numeração automática do documento.
11. Remover da versão final do PDF qualquer linha que exponha comandos de compilação, como `article [utf8]inputenc [brazil]babel...`.
12. Atualizar o Capítulo 6. As etapas de treinamento, XAI, interface e testes aparecem como futuras, embora já existam no Capítulo 5. O plano de continuidade deve concentrar-se na validação externa, na análise por fototipo, na avaliação de lesões acrais, na participação de dermatologistas, nos testes de fidelidade dos mapas e na redação final.

## 7. Referências novas que precisam estar na bibliografia final

As seis referências abaixo são necessárias para sustentar a correção demográfica. Elas devem ser incorporadas à bibliografia principal da dissertação, e não deixadas somente em um arquivo auxiliar do projeto.

**[39] PACHECO, Andre G. C. et al. PAD-UFES-20: A skin lesion dataset composed of patient data and clinical images collected from smartphones. Data in Brief, v. 32, art. 106221, 2020. DOI: 10.1016/j.dib.2020.106221.**

**[40] DANESHJOU, Roxana et al. Disparities in dermatology AI performance on a diverse, curated clinical image set. Science Advances, v. 8, n. 31, eabq6147, 2022. DOI: 10.1126/sciadv.abq6147.**

**[41] GROH, Matthew et al. Evaluating Deep Neural Networks Trained on Clinical Images in Dermatology with the Fitzpatrick 17k Dataset. In: 2021 IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops. 2021. p. 1820–1828. DOI: 10.1109/CVPRW53098.2021.00201.**

**[42] ALIPOUR, Neda; BURKE, Ted; COURTNEY, Jane. Skin Type Diversity in Skin Lesion Datasets: A Review. Current Dermatology Reports, v. 13, n. 3, p. 198–210, 2024. DOI: 10.1007/s13671-024-00440-0.**

**[43] GARCIA, Lucas Campos; GONTIJO, João Renato Vianna; BITTENCOURT, Flávia Vasques. Plantar acral melanoma: epidemiological, clinical, dermoscopic and histopathological features. A Brazilian cohort. Anais Brasileiros de Dermatologia, v. 100, n. 1, p. 45–53, 2025. DOI: 10.1016/j.abd.2024.03.006.**

**[44] TSCHANDL, Philipp; ROSENDAHL, Cliff; KITTLER, Harald. The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions. Scientific Data, v. 5, art. 180161, 2018. DOI: 10.1038/sdata.2018.161.**

No texto visível da defesa, manter o padrão autor-data já utilizado, por exemplo: `(PACHECO et al., 2020)`, `(DANESHJOU et al., 2022)` e `(TSCHANDL; ROSENDAHL; KITTLER, 2018)`. Não misturar, no mesmo arquivo final, referências numéricas `ref_39` com citações autor-data, a menos que o template LaTeX esteja configurado para converter as chaves automaticamente.

## 8. Texto recomendado para o Capítulo 6 – Plano de continuidade

Substituir a abertura e as etapas antigas por:

**O sistema apresentado no Capítulo 5 já possui uma implementação funcional, modelos treinados, interface web, mecanismos de triagem, geração de mapas e avaliação interna no HAM10000. Portanto, a continuidade do mestrado não consiste em iniciar a implementação, mas em ampliar a validade científica do protótipo e consolidar a análise dos seus limites. As etapas remanescentes concentram-se na execução da validação externa estratificada, na análise por fototipo e localização anatômica, na avaliação específica de lesões acrais, na verificação da estabilidade e fidelidade das explicações, na revisão por especialistas e na redação final da dissertação.**

**a) Validação externa e mudança de domínio:** executar o avaliador com manifestos autorizados do PAD-UFES-20, DDI e Fitzpatrick17k, preservando o teste interno do HAM10000 como referência congelada.

**b) Auditoria demográfica:** apresentar suporte, distribuição de diagnósticos e métricas por fototipo ou grupo disponível, sem produzir conclusões de equidade quando o número de casos for insuficiente.

**c) Avaliação de lesões acrais:** organizar, quando houver autorização e suporte amostral, um subconjunto com localização plantar, palmar ou ungueal e diagnóstico confiável, reportando os resultados separadamente.

**d) Avaliação da explicabilidade:** medir estabilidade, fidelidade e sensibilidade dos mapas, complementando a inspeção visual com avaliação de especialistas e deixando claro que os overlays não são máscaras clínicas.

**e) Consolidação científica:** atualizar tabelas, figuras, referências, limitações e discussão; disponibilizar os manifestos, versões dos checkpoints, configurações e scripts de avaliação compatíveis com as licenças das bases.

**f) Redação e defesa:** revisar a coerência entre objetivos, métodos, resultados e conclusões, recompilar o documento completo e realizar uma conferência final de figuras, legendas, citações e referências.**

## 9. Checklist antes de entregar a versão final

- [ ] Resumo e abstract não usam mais “qualification paper”, “proposed system” ou “Python/Django” como descrição da aplicação final.
- [ ] A estrutura informa seis capítulos e descreve o Capítulo 5 como implementação.
- [ ] O texto demográfico aparece no PDF final, não apenas no arquivo Markdown.
- [ ] PAD-UFES-20, DDI, Fitzpatrick17k, Alipour et al., Garcia et al. e HAM10000 estão na bibliografia principal.
- [ ] O texto não afirma que a validação brasileira já foi concluída se os manifestos externos ainda não foram executados.
- [ ] O avaliador externo é apresentado como implementado e pronto para uso, não como resultado demográfico já obtido.
- [ ] A discussão de melanoma acral é apresentada como justificativa clínica e lacuna de validação, não como evidência de desempenho do sistema.
- [ ] As referências às Figuras 5.7, 5.8, 5.9, 5.10, 5.11 e 5.12 estão consistentes após a recompilação.
- [ ] Os trechos corrompidos da página 69 e do teste fora do domínio foram substituídos.
- [ ] O texto residual do plano antigo foi removido ou transformado em plano de continuidade realista.
- [ ] A dissertação deixa claro que o sistema é um protótipo acadêmico e não uma ferramenta de diagnóstico autônomo.

## 10. Conclusão da auditoria

A correção solicitada pelo avaliador deve ser apresentada como uma combinação de **revisão da fundamentação teórica, implementação de um protocolo de validação externa e declaração explícita dos limites atuais**. O código necessário para estruturar essa avaliação já foi incorporado ao projeto. O que ainda falta para uma conclusão demográfica é executar o protocolo com bases autorizadas, verificar os metadados, produzir métricas por subgrupo e discutir os intervalos de incerteza. Até essa etapa, a formulação cientificamente correta é: **o sistema foi preparado para avaliar a generalização por fototipo e população, mas essa generalização ainda não foi demonstrada pelo experimento interno no HAM10000**.

Essa distinção atende ao parecer médico sem transformar uma preocupação legítima em uma afirmação não comprovada e fortalece a defesa ao demonstrar que o trabalho reconhece o problema, implementou uma resposta metodológica e delimitou claramente o que ainda precisa ser validado.
