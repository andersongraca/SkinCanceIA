# Relatório final de revisão da qualificação, continuidade do mestrado e perspectivas de doutorado

**Projeto:** SkinCancerCADDermoIA
**Natureza do documento:** diagnóstico acadêmico, plano de correção, matriz de resposta ao parecer, plano de continuidade do mestrado, auditoria e perspectivas posteriores de pesquisa
**Autor do relatório:** Manus AI
**Data de consolidação:** 17 de setembro de 2026
**Versão técnica auditada:** branch `feat/scientific-ml-backend`, commit `cb03a0e`

> **Síntese executiva.** O parecer é favorável, porém condiciona a continuidade à remoção das duplicações do Capítulo 2 e à revisão linguística integral. A condição é procedente. Além das falhas indicadas pelo avaliador, o manuscrito contém inconsistências na estrutura da Revisão Sistemática da Literatura (RSL), na numeração e nas citações, números não rastreáveis apresentados como “Fonte: Autor”, resíduos de compilação e divergências entre a proposta escrita e o sistema efetivamente implementado. A versão final deve apresentar o trabalho como **protótipo acadêmico de apoio à classificação de imagens dermatoscópicas**, e não como sistema de diagnóstico. Os únicos resultados quantitativos do classificador que podem ser atribuídos ao sistema, com os documentos disponíveis, são os resultados internos do teste HAM10000 com 1.527 imagens. Eles não constituem validação clínica, externa ou prospectiva.[1]

## 1. Finalidade, base documental e regra de evidência

Este relatório converte o parecer e os artefatos técnicos em um plano executável de conclusão do **mestrado**. Ele responde a cada observação do avaliador, diagnostica o manuscrito, propõe um novo sumário, delimita o conteúdo do sistema implementado e define auditorias científica e de software. A perspectiva de doutorado aparece somente depois desse plano, como possibilidade posterior à defesa, e não como substituição das atividades necessárias para concluir a dissertação.

As recomendações foram elaboradas a partir do artigo de qualificação, do parecer do avaliador e dos documentos versionados do sistema. A auditoria registra um protótipo operacional em demonstração local, testes automatizados, inferência dos quatro resultados exibidos e métricas congeladas do HAM10000. A mesma auditoria afirma expressamente que esse funcionamento **não é validação clínica, não prova causalidade e não autoriza uso diagnóstico**.[1]

A redação final deve seguir uma regra simples de evidência:

1. **Resultado executado e registrado** pode ser descrito no passado, acompanhado de dataset, partição, tamanho amostral, métrica e fonte do artefato.
2. **Funcionalidade implementada e testada** pode ser descrita como verificação de engenharia, sem convertê-la em evidência clínica.
3. **Experimento ainda não executado** deve aparecer como protocolo, limitação, etapa pendente ou trabalho futuro, nunca com número estimado.
4. **Afirmação bibliográfica** deve ser sustentada por fonte primária conferida na bibliografia. Uma tabela sem referência por linha, dataset, partição e tarefa não deve permanecer.
5. **Informação ausente dos logs**, como taxa de aprendizado, lote, épocas, temperatura aprendida, hardware ou duração de treinamento, deve ser recuperada dos artefatos originais ou marcada como “não documentada”. Não deve ser reconstruída por suposição.

As citações numéricas deste relatório apontam para os documentos de auditoria e para as páginas oficiais dos datasets. Ao transferir os trechos para a dissertação, elas devem ser convertidas para o padrão ABNT autor-data já adotado no trabalho, sem misturar estilos.

## 2. Resposta item por item ao parecer

### 2.1 Comentário 1 — mérito, atualidade e relevância do trabalho

**Diagnóstico.** O comentário é positivo e não exige correção pontual. Entretanto, o mérito reconhecido deve ser preservado sem aumentar o alcance das conclusões. A contribuição comprovada é a integração de comparação entre arquiteturas, Ensemble, incerteza, triagem operacional e visualizações XAI em um protótipo acadêmico.

**Ação.** Reescrever título, resumo, objetivo geral e conclusão para distinguir: o problema clínico que motiva a pesquisa; a tarefa computacional de classificação; o protótipo de apoio acadêmico; e a ausência de validação clínica.

**Evidência de conclusão.** A versão recompilada não usa “sistema de diagnóstico” para designar o protótipo e não afirma “confiança clínica”, “superioridade clínica” ou “uso médico” com base nas métricas internas.

**Resposta-modelo ao avaliador.**

> Agradeço a avaliação positiva. Manterei a contribuição centrada na comparação entre CNN, Vision Transformer e modelo híbrido, no Ensemble, na revisão sistemática e no protótipo acadêmico. A versão revisada deixará explícito que os resultados demonstram viabilidade técnica em avaliação interna e não validade clínica.

### 2.2 Comentário 2 — duplicação de quase metade do Capítulo 2

**Diagnóstico.** A observação é procedente e crítica. As seções 2.2, 2.3 e 2.4 reaparecem em 2.5, 2.6 e 2.7. A duplicação compromete a organização, a paginação, o sumário, as referências cruzadas e a percepção de rigor editorial.

**Ação.** Manter uma única seção de datasets, uma de CNNs e uma de Vision Transformers. Material não redundante das cópias deve ser incorporado somente se acrescentar conceito, referência ou transição necessária. Depois da exclusão, todas as seções subsequentes devem ser renumeradas e o documento deve ser recompilado.

**Evidência de conclusão.** Comparação textual confirma que nenhum dos três blocos permanece repetido; sumário, lista de figuras, lista de tabelas, referências cruzadas e paginação são gerados novamente; nenhuma chamada para tabela ou seção removida fica órfã.

**Resposta-modelo ao avaliador.**

> A duplicação foi reconhecida como falha crítica. Removerei os blocos redundantes, preservarei uma única versão de Datasets, CNNs e Transformers, revisarei as transições e recompilarei o documento para atualizar sumário, numeração, paginação e referências cruzadas.

### 2.3 Comentário 3 — “promissula”/“promissor” na Seção 2.8.1

**Diagnóstico.** Há divergência entre o parecer e o PDF disponível. O parecer registra “promissula”, enquanto a extração textual do PDF apresenta “uma solução promissor”. Em ambos os casos, a forma correta é **“uma solução promissora”**.

**Ação.** Pesquisar no arquivo-fonte as variantes `promissula`, `promissor` e a frase completa. Corrigir a concordância e verificar a prova renderizada.

**Evidência de conclusão.** O fonte e o PDF exibem “uma solução promissora”, sem ocorrência residual das formas incorretas.

**Resposta-modelo ao avaliador.**

> Conferi a divergência entre o parecer e o PDF. Na versão fornecida aparece “solução promissor”; corrigirei a expressão para “solução promissora” no arquivo-fonte e confirmarei visualmente a nova compilação.

### 2.4 Comentário 4 — “padastro” nos Agradecimentos

**Diagnóstico.** A extração textual do PDF disponível mostra “padrasto”, embora o parecer registre “padastro”. Isso pode resultar de diferença de versão ou de leitura visual. Não é possível certificar o fonte sem inspecioná-lo.

**Ação.** Buscar as duas grafias no arquivo-fonte, manter somente “padrasto” e revisar todo o parágrafo dos Agradecimentos, inclusive espaços após pontuação, como “foi.Com” e “ensinou.Que”, se ainda presentes.

**Evidência de conclusão.** O fonte e o PDF final exibem “padrasto”; o parágrafo foi lido na prova final e não contém falhas de espaçamento ou pontuação.

**Resposta-modelo ao avaliador.**

> No PDF atualmente disponível, a grafia aparece como “padrasto”. Ainda assim, conferirei o arquivo-fonte e a prova final para garantir que essa forma corrigida permaneça na versão submetida.

### 2.5 Comentário 5 — encadeamento e ortografia na Seção 3.2.1

**Diagnóstico.** As formas “selecionandos”, “citerios”, “exlusão” e “elecionados” prejudicam a legibilidade e a reprodutibilidade do fluxo da RSL. O problema é maior que a ortografia: o texto também alterna 234 e 199 como total inicial sem explicar a deduplicação.

**Ação.** Corrigir as palavras e reescrever o parágrafo para distinguir identificação, deduplicação, triagem por título/resumo, leitura integral e inclusão. Recuperar no Parsifal os valores efetivos de cada etapa.

**Evidência de conclusão.** O fluxo apresenta uma única sequência auditável. Se 234 forem os registros brutos e 199 os registros após deduplicação, o texto informa explicitamente o número de duplicatas removidas. O total final de 51 estudos deve ser mantido somente se confirmado.

**Resposta-modelo ao avaliador.**

> Corrigirei as quatro grafias e reescreverei o período para tornar explícitas as etapas de deduplicação, triagem por título e resumo, aplicação dos critérios, leitura integral e inclusão dos 51 estudos. Os números intermediários serão preenchidos a partir do registro do Parsifal.

### 2.6 Comentário 6 — gênero em “A pré-processamento”

**Diagnóstico.** A construção incorreta aparece no bloco original e na cópia. A exclusão da cópia não elimina a necessidade de corrigir a ocorrência preservada.

**Ação.** Substituir por **“O pré-processamento das imagens”** e executar busca global por problemas semelhantes de gênero e concordância.

**Evidência de conclusão.** Não há ocorrência de “A pré-processamento” no fonte nem no PDF.

**Resposta-modelo ao avaliador.**

> A observação procede. Substituirei a ocorrência preservada por “O pré-processamento das imagens” e incluirei essa verificação na revisão gramatical global.

### 2.7 Comentário 7 — quebra do padrão de citação em “Ali et al. [49]”

**Diagnóstico.** O manuscrito mistura citação numérica e autor-data. Também há múltiplos trabalhos de autores homônimos em 2025, o que exige conferir sufixos `a`, `b` e `c` em todas as citações e na lista de referências.

**Ação.** Identificar a entrada correspondente a `[49]`, convertê-la para a forma autor-data ABNT, harmonizar ano e sufixo e procurar todas as citações numéricas residuais. A Tabela 8, que usa `[1]–[4]`, deve ser normalizada pelo mesmo critério.

**Evidência de conclusão.** O texto inteiro adota um único sistema autor-data. Cada citação aponta para uma entrada bibliográfica existente, e cada entrada citada aparece na bibliografia.

**Resposta-modelo ao avaliador.**

> Uniformizarei “Ali et al. [49]” para a forma autor-data correspondente à entrada bibliográfica correta. Também revisarei os sufixos de ano e eliminarei citações numéricas remanescentes nas tabelas e no corpo do texto.

### 2.8 Comentário 8 — expansão incorreta de HAM10000

**Diagnóstico.** O manuscrito registra “Human Against Machine with 100000 Training Images”. A denominação correta contém **10000**, enquanto o manifesto específico do experimento registra **10.015 imagens**. O nome histórico e a contagem do arquivo usado são informações diferentes.[4]

**Ação.** Corrigir a denominação nas ocorrências preservadas e nas tabelas. Informar separadamente que o manifesto experimental contém 10.015 imagens, 7.470 grupos de lesão e sete classes.[4]

**Evidência de conclusão.** Não há ocorrência de “100000 Training Images”. A descrição não confunde o nome do dataset com a contagem auditada.

**Resposta-modelo ao avaliador.**

> Corrigirei a expansão para “Human Against Machine with 10000 Training Images” e informarei separadamente que o manifesto do experimento registra 10.015 imagens. Assim, a denominação da base não será confundida com sua contagem auditada.

### 2.9 Comentário 9 — falha de compilação de caracteres, como `\tilde{A}`

**Diagnóstico.** A ocorrência exata não é recuperável com segurança na extração textual, mas isso não invalida a observação visual do avaliador. Há ainda um resíduo de preâmbulo LaTeX visível na página 60 do PDF analisado. Trata-se de falha de compilação/formatação, não apenas de estilo.

**Ação.** Localizar a expressão no fonte; garantir codificação UTF-8 e sintaxe matemática válida; remover o preâmbulo impresso; recompilar com log; inspecionar fórmulas, acentos, hifens, quebras de palavra e caracteres especiais página a página.

**Evidência de conclusão.** O log de compilação não contém erro relevante; não existe preâmbulo impresso no corpo; a expressão matemática é exibida corretamente na prova visual.

**Resposta-modelo ao avaliador.**

> Revisarei a sintaxe de `\tilde{A}` e dos demais caracteres no arquivo-fonte, removerei o resíduo de preâmbulo, recompilarei a dissertação e farei inspeção visual integral do PDF antes do depósito.

### 2.10 Comentário 10 — especificação dos pares duplicados 2.2/2.5, 2.3/2.6 e 2.4/2.7

**Diagnóstico.** O comentário detalha operacionalmente a falha do item 2. Embora a correção possa ser executada em uma única refatoração, a evidência deve confirmar cada par.

**Ação.** Registrar na revisão que 2.2/2.5, 2.3/2.6 e 2.4/2.7 foram comparadas; excluir 2.5–2.7 ou absorver somente conteúdo não redundante; conferir citações e tabelas em cada bloco.

**Evidência de conclusão.** A matriz de alterações informa o destino de cada par, e uma busca por frases iniciais confirma que nenhum bloco literal foi preservado duas vezes.

**Resposta-modelo ao avaliador.**

> A especificação dos três pares foi incorporada ao plano de correção. Eliminarei cada cópia, revisarei as transições e as referências e confirmarei no PDF recompilado que cada conceito aparece uma única vez.

### 2.11 Comentário 11 — tons de pele, população brasileira e lesões acrais

**Diagnóstico.** A observação é central para a validade externa. O manifesto do experimento contém classes, contagens e grupos, mas não fornece variáveis suficientes de fototipo, tom de pele, população, país, dispositivo ou localização anatômica para demonstrar equidade.[4] Portanto, não é válido afirmar que o sistema generaliza para pele escura, população miscigenada brasileira ou lesões acrais.

**Ação.** Inserir uma subseção de viés de representação e validade externa. Declarar a ausência de metadados de subgrupo, separar desempenho interno de equidade e propor validação externa autorizada com tom de pele, sítio anatômico, dispositivo, instituição e padrão de referência. Resultados de literatura próximos de 99% não podem ser atribuídos ao sistema; os resultados internos do Ensemble são acurácia 0,7498 e AUROC 0,8600.[1]

**Evidência de conclusão.** Resumo, discussão e conclusão contêm a limitação. Nenhuma frase afirma equidade ou generalização brasileira. O protocolo futuro define métricas por subgrupo e intervalos de confiança, sem prometer direção do efeito.

**Resposta-modelo ao avaliador.**

> A observação será incorporada como limitação central. O manifesto disponível não permite quantificar fototipos, miscigenação ou lesões acrais; por isso, não afirmarei equidade nem generalização clínica para a população brasileira. Proporei validação externa com subgrupos tonais, anatômicos, institucionais e de dispositivo e distinguirei os resultados da literatura dos resultados internos do Ensemble.

### 2.12 Comentário 12 — aprovação condicionada às correções

**Diagnóstico.** A condição ainda deve ser considerada **pendente**. Não foi fornecido um novo fonte revisado nem um PDF recompilado que permita certificar as correções.

**Ação.** Executar o checklist da Seção 11 deste relatório; gerar nova versão; conferir sumário, paginação, referências, tabelas e caracteres; registrar a versão submetida.

**Evidência de conclusão.** Novo PDF, log de compilação, checklist assinado, matriz comentário–ação–evidência atualizada e inspeção visual completa.

**Resposta-modelo ao avaliador.**

> Reconheço o caráter condicional da recomendação. Antes dos próximos passos, entregarei uma versão recompilada com as duplicações removidas, revisão linguística integral, citações uniformizadas, nomenclatura do HAM10000 corrigida e inspeção final de caracteres, acompanhada de uma lista de verificação das alterações.

## 3. Diagnóstico acadêmico do artigo atual

### 3.1 Conclusão diagnóstica

O artigo mistura três estágios do projeto. O primeiro é uma revisão de literatura extensa, mas estruturalmente duplicada. O segundo é uma proposta prospectiva baseada em ISIC-2019 e Django. O terceiro é um sistema já implementado com HAM10000, um localizador ISIC 2016 e uma aplicação React/TypeScript/Express/Python. Como esses estágios não estão distinguidos, o leitor não consegue determinar quais afirmações são revisão, plano ou resultado.

A revisão deve transformar o documento em uma cadeia lógica única:

> **problema e lacuna → evidência da literatura → pergunta e objetivo → dados e método implementado → resultados internos → auditoria → limitações → próximos passos.**

### 3.2 Principais problemas e decisões de correção

| Dimensão | Diagnóstico atual | Consequência | Decisão necessária |
|---|---|---|---|
| Estrutura | Seções 2.2–2.4 duplicadas em 2.5–2.7 | Paginação artificial, redundância e sumário incorreto | Excluir as cópias e renumerar todo o documento |
| RSL | Totais de 234 e 199 aparecem como busca inicial | Fluxo não reprodutível | Recuperar números no Parsifal e explicitar deduplicação |
| Sumário | 3.1.2 e 3.1.3 repetem “Critérios de Inclusão e Exclusão” | Título não corresponde ao conteúdo | Renomear 3.1.3 para “Questões de Pesquisa” |
| Citações | Mistura autor-data, `[49]` e `[1]–[4]` | Inconsistência bibliográfica | Aplicar ABNT autor-data de ponta a ponta |
| Tabelas | Números de tabela e chamadas estão quebrados | Evidência difícil de rastrear | Regenerar numeração e conferir cada chamada |
| Resultados | Tabela “Fonte: Autor” apresenta 89,45%–94,23% sem protocolo rastreável | Risco de atribuição indevida ao sistema | Rastrear fonte primária ou remover; usar tabela auditada separada |
| Escopo | Objetivo alterna dois sistemas, três arquiteturas e Ensemble | Pergunta e avaliação desalinhadas | Declarar CNN, ViT, Hybrid e Ensemble no mesmo escopo |
| Dados | Proposta usa ISIC-2019, implementação usa HAM10000 e ISIC 2016 | Método descrito não reproduz o sistema | Atualizar dados e separar classificação de gate XAI |
| Software | Texto promete Django, implementação usa React/Express/tRPC/Python | Arquitetura factual incorreta | Descrever a pilha auditada; marcar Django como plano substituído |
| XAI | Heatmaps são tratados como confiança/relevância clínica | Excesso epistemológico | Descrever saliência aproximada, gate visual e limites de causalidade |
| Linguagem clínica | “Diagnóstico”, “confiança clínica” e “superioridade” excedem a evidência | Risco científico e ético | Usar “classificação experimental” e “apoio computacional” |
| Equidade | Não há análise por tom de pele ou lesão acral | Generalização não demonstrada | Declarar limitação e propor validação externa estratificada |
| Compilação | Resíduo de preâmbulo e caracteres problemáticos | Aparência de documento não finalizado | Corrigir fonte, recompilar e inspecionar visualmente |

### 3.3 Escopo científico recomendado

A dissertação deve responder a uma pergunta delimitada: **como CNN, ViT, modelo híbrido e Ensemble se comportam em uma avaliação interna e reprodutível de imagens dermatoscópicas do HAM10000, incluindo discriminação, calibração, incerteza e visualizações XAI?**

O texto não deve prometer dois “sistemas de diagnóstico”. O Ensemble é uma combinação dos três componentes e não um quarto modelo treinado de forma independente. O localizador ISIC 2016 é uma ramificação auxiliar que afeta apenas a visualização. A triagem OOD e a abstenção são controles operacionais configuráveis, não garantias de segurança clínica.

### 3.4 Objetivo geral recomendado

> **Desenvolver e avaliar, em protocolo experimental reprodutível, um protótipo de apoio à classificação de imagens dermatoscópicas que compare uma CNN, um Vision Transformer, um modelo híbrido e um Ensemble ponderado quanto a discriminação, calibração, incerteza e comportamento das saliências, sem reivindicar uso diagnóstico autônomo.**

### 3.5 Objetivos específicos recomendados

1. Consolidar uma divisão do HAM10000 por grupos de lesão e documentar proveniência, classes, licença, seed e partições.
2. Comparar CNN ResNet-50, ViT `vit_small_patch16_224` e modelo híbrido sob o protocolo registrado.
3. Avaliar o Ensemble ponderado com pesos escolhidos exclusivamente na validação.
4. Reportar acurácia, sensibilidade, especificidade, AUROC, AUPRC e ECE, acrescentando intervalos de confiança e análises complementares quando executadas.
5. Avaliar entropia, variância TTA e política de abstenção como sinais de incerteza operacional.
6. Descrever e auditar a triagem de qualidade e a distância OOD sem atribuir cobertura semântica universal.
7. Avaliar os métodos XAI e o gate de localização como visualizações aproximadas, mantendo-os separados do caminho de classificação.
8. Documentar a aplicação full-stack, seus testes, sua reprodutibilidade e suas limitações de persistência.
9. Delimitar ameaças à validade, com ênfase em mudança de domínio, desbalanceamento, tons de pele e lesões acrais.

## 4. Novo sumário proposto

O sumário abaixo serve para a **dissertação final**. Para a versão imediatamente posterior à qualificação, os Capítulos 5 e 6 podem ser parcialmente apresentados como resultados preliminares e plano de continuidade, desde que cada item pendente seja identificado como tal.

### Elementos pré-textuais

- Folha de rosto
- Folha de aprovação
- Dedicatória e agradecimentos
- Resumo e Abstract
- Palavras-chave e Keywords
- Lista de abreviaturas e siglas
- Listas de figuras e tabelas
- Sumário gerado automaticamente

### Capítulo 1 — Introdução

1.1 Contexto clínico e computacional
1.2 Problema de pesquisa
1.3 Motivação e lacuna científica
1.4 Viés de representação e relevância para a população brasileira
1.5 Objetivo geral
1.6 Objetivos específicos
1.7 Contribuições e escopo
1.8 Organização da dissertação

### Capítulo 2 — Fundamentação teórica

2.1 Lesões cutâneas, dermatoscopia e tarefa computacional
2.2 Datasets, rótulos, desbalanceamento e mudança de domínio
2.3 Redes Neurais Convolucionais
2.4 Vision Transformers
2.5 Arquiteturas híbridas e Ensemble Learning
2.6 Transferência de aprendizado, perdas e amostragem
2.7 Calibração, incerteza e classificação seletiva
2.8 Explicabilidade, saliência e localização auxiliar
2.9 Métricas de classificação, calibração, segmentação e XAI
2.10 Limites de aplicabilidade clínica de modelos computacionais

### Capítulo 3 — Revisão sistemática e estado da arte

3.1 Objetivo e questões de pesquisa
3.2 Protocolo e adaptação PICO-C
3.3 Bases, strings e período de busca
3.4 Critérios de inclusão, exclusão e qualidade
3.5 Identificação, deduplicação, triagem e inclusão
3.6 Extração e síntese dos dados
3.7 Resultados quantitativos da RSL
3.8 Comparação por arquitetura, dataset, tarefa e métrica
3.9 Evidência sobre calibração, XAI e Ensemble
3.10 Viés demográfico, validade externa e lacunas
3.11 Implicações da RSL para o sistema desenvolvido

### Capítulo 4 — Metodologia e sistema desenvolvido

4.1 Delineamento experimental e afirmações permitidas
4.2 HAM10000: proveniência, classes e agrupamento binário
4.3 Particionamento por grupos de lesão e teste congelado
4.4 Pré-processamento e treinamento
4.5 CNN, ViT e Hybrid
4.6 Cabeça multitarefa e Ensemble ponderado
4.7 Test-Time Augmentation, entropia e variância
4.8 Abstenção e triagem de qualidade/OOD
4.9 ISIC 2016 e gate auxiliar de localização
4.10 XAI por arquitetura
4.11 Arquitetura full-stack e persistência
4.12 Controle de versão, ética, licença e reprodutibilidade

### Capítulo 5 — Resultados

5.1 Integridade dos dados e das partições
5.2 Resultados internos de classificação
5.3 Calibração e incerteza
5.4 Avaliação da política de abstenção
5.5 Avaliação da triagem OOD
5.6 Resultados do localizador ISIC 2016
5.7 Avaliação dos mapas XAI
5.8 Ablations executadas
5.9 Custo computacional
5.10 Resultados da auditoria de software

### Capítulo 6 — Discussão

6.1 Síntese dos achados
6.2 Comparação com a RSL sob protocolos compatíveis
6.3 Por que o Ensemble não é superior em todos os critérios
6.4 Calibração, incerteza e significado da abstenção
6.5 XAI: localização, fidelidade e causalidade
6.6 Validade interna, externa e de construto
6.7 Equidade, tons de pele, lesões acrais e população brasileira
6.8 Implicações de engenharia
6.9 Limitações da dissertação

### Capítulo 7 — Conclusão e trabalhos futuros

7.1 Resposta ao problema de pesquisa
7.2 Contribuições efetivamente demonstradas
7.3 Trabalhos futuros após a dissertação
7.4 Transição para a agenda de doutorado

### Referências e apêndices

- Referências em padrão ABNT autor-data
- Apêndice A — Protocolo completo da RSL
- Apêndice B — Tabela dos estudos incluídos
- Apêndice C — Manifesto e listas de partição
- Apêndice D — Configuração de treinamento e checkpoints
- Apêndice E — Matrizes de confusão e curvas
- Apêndice F — Auditoria científica e de software
- Apêndice G — Instruções de reprodução

## 5. O que escrever sobre o sistema desenvolvido

### 5.1 Status e fronteira de uso

O sistema deve ser apresentado como protótipo acadêmico integrado. Ele recebe imagem dermatoscópica, realiza triagem de qualidade e de distância estatística em relação ao domínio, executa três checkpoints, combina probabilidades, calcula sinais de incerteza, aplica regra de abstenção e produz mapas de saliência. O protótipo não é dispositivo médico e não substitui avaliação clínica.[1] [2]

**Trecho pronto para inserção.**

> O sistema desenvolvido é um protótipo acadêmico de apoio computacional à análise de imagens dermatoscópicas. Sua saída principal é uma classificação binária de malignidade produzida por um Ensemble de três checkpoints, acompanhada das previsões individuais, de estimativas de incerteza, de uma política de abstenção, de triagem de qualidade e domínio e de mapas de saliência. O protótipo não substitui avaliação médica, não foi validado prospectivamente e não deve ser apresentado como dispositivo diagnóstico.

### 5.2 Dados e particionamento

O manifesto registra 10.015 imagens, 10.015 linhas de metadados, nenhuma imagem faltante, sete classes e 7.470 grupos de lesão. A seed é 42. Os grupos estão divididos em 5.228 para treino, 1.121 para validação e 1.121 para teste. O teste congelado possui 1.527 imagens.[4] [5]

A tarefa binária agrupa `akiec`, `bcc` e `mel` como classes operacionais malignas. Essa convenção deve ser descrita como decisão de modelagem; ela não equivale, por si só, a confirmação histopatológica de câncer em cada imagem. No teste há 300 imagens do agrupamento operacional maligno e 1.227 das demais classes.

| Classe | Treino | Validação | Teste |
|---|---:|---:|---:|
| `akiec` | 230 | 49 | 48 |
| `bcc` | 351 | 97 | 66 |
| `bkl` | 782 | 145 | 172 |
| `df` | 67 | 38 | 10 |
| `mel` | 779 | 148 | 186 |
| `nv` | 4.689 | 1.000 | 1.016 |
| `vasc` | 101 | 12 | 29 |
| **Total** | **6.999** | **1.489** | **1.527** |

**Trecho pronto para inserção.**

> O pipeline de classificação utiliza o HAM10000. O manifesto experimental registra 10.015 imagens, sete classes e 7.470 grupos de lesão. A divisão foi realizada por grupo, com seed 42, para reduzir o risco de que imagens correlacionadas da mesma lesão aparecessem em partições diferentes. Foram destinados 5.228 grupos ao treino, 1.121 à validação e 1.121 ao teste. O teste congelado contém 1.527 imagens e não foi usado para selecionar os pesos do Ensemble. Para a saída binária, `akiec`, `bcc` e `mel` foram agrupadas operacionalmente como malignas e as demais classes como benignas. Esse agrupamento é uma convenção computacional do experimento e não substitui confirmação clínica ou histopatológica.

### 5.3 Arquiteturas e treinamento

A CNN usa ResNet-50; o ViT usa `vit_small_patch16_224`; o Hybrid combina representação ResNet-50, tokens e atenção multi-head por um gate aprendido. Cada checkpoint contém cabeça multitarefa de sete classes e saída binária.[2]

Os documentos registram transferência de aprendizado, focal loss, pesos por número efetivo de amostras, amostragem balanceada apenas no treino, AdamW, clipping de gradiente, scheduler cosseno e calibração por temperatura. Os valores numéricos de épocas, lote, taxa de aprendizado, parâmetros da focal loss, norma de clipping e temperatura aprendida não devem ser inventados. Devem ser extraídos de logs, checkpoints ou configuração versionada.

| Campo metodológico | Situação atual | Tratamento na dissertação |
|---|---|---|
| Backbones | Documentados | Reportar nominalmente |
| Transferência de aprendizado | Documentada | Reportar |
| Focal loss e pesos efetivos | Documentados conceitualmente | Reportar fórmula e recuperar parâmetros |
| AdamW, clipping e scheduler cosseno | Documentados | Reportar e recuperar valores |
| Batch size e épocas | Não confirmados nos artefatos resumidos | Preencher por logs ou “não documentado” |
| Taxa de aprendizado | Não confirmada | Preencher por logs ou “não documentado” |
| Temperatura aprendida | Não confirmada | Recuperar por checkpoint/log |
| Hardware e duração do treino | Não confirmados | Medir ou declarar ausência |
| Número de parâmetros | Não consolidado | Calcular por script versionado |

**Trecho pronto para inserção.**

> Foram documentados transferência de aprendizado, focal loss, ponderação por número efetivo de amostras, amostragem balanceada somente no treino, AdamW, clipping de gradiente, scheduler cosseno e calibração por temperatura. Validação e teste preservaram a distribuição original. Os hiperparâmetros numéricos são apresentados na tabela de configuração somente quando recuperados dos logs e checkpoints versionados; campos sem registro são identificados como não documentados, sem reconstrução por inferência.

### 5.4 Ensemble, TTA, incerteza e abstenção

Os pesos do Ensemble foram selecionados na validação e somam 1: CNN 0,10; ViT 0,55; Hybrid 0,35.[1] Para a probabilidade maligna:

\[
p_E = 0{,}10p_{CNN} + 0{,}55p_{ViT} + 0{,}35p_{Hybrid}.
\]

Com três transformações de Test-Time Augmentation (TTA), a média de um modelo \(m\) pode ser descrita por:

\[
\bar p_m = \frac{1}{3}\sum_{k=1}^{3} p_m(T_k(x)),
\]

com variância:

\[
Var_{TTA}(m) = \frac{1}{3}\sum_{k=1}^{3}(p_m(T_k(x))-\bar p_m)^2.
\]

Para a distribuição binária agregada \(p=(p_0,p_1)\), a entropia é:

\[
H(p)=-\sum_{c\in\{0,1\}} p_c\log p_c.
\]

A configuração auditada recomenda abstenção quando pelo menos dois modelos individuais votam pela abstenção, ou a entropia agregada excede 0,75, ou a variância TTA excede 0,03.[1] [2] Esses limiares são regras operacionais e precisam de avaliação risco–cobertura antes de qualquer interpretação de segurança.

**Trecho pronto para inserção.**

> O Ensemble combina as probabilidades malignas por \(p_E=0{,}10p_{CNN}+0{,}55p_{ViT}+0{,}35p_{Hybrid}\). Os pesos foram selecionados no conjunto de validação e o teste permaneceu congelado. Cada checkpoint executa três transformações em TTA. O sistema calcula entropia preditiva e variância entre as transformações. Na configuração auditada, recomenda-se abstenção quando dois modelos individuais votam pela abstenção, quando a entropia agregada excede 0,75 ou quando a variância TTA excede 0,03. Esses valores são controles operacionais configuráveis; não representam probabilidade clínica nem garantia de segurança.

### 5.5 Triagem de qualidade e OOD

A triagem avalia resolução, proporção, nitidez, exposição, contraste, uniformidade e características de cor/luminância. A distância OOD usa centro e escala robustos derivados do HAM10000, com limiar no percentil 99,5 da validação.[2]

Uma imagem não dermatológica foi rejeitada na auditoria, mas um caso não demonstra cobertura universal.[1] A dissertação deve reportar esse evento como teste funcional. Uma avaliação científica de OOD exige painel independente e rotulado, falsos aceites, falsos rejeites, AUROC-OOD, AUPR-OOD e FPR em TPR prefixada.

### 5.6 Gate auxiliar e XAI

O localizador usa ISIC 2016 Part 1, com 900 imagens e máscaras, divisão 720/90/90, seed 42 e entrada 160×160. No teste ISIC 2016 obteve Dice 0,8245 e IoU 0,7667.[3] Esses valores não medem o desempenho do gate no HAM10000.

O modo `balanced`, usado na auditoria, adota limiar 0,50 e kernel morfológico 5×5. `strict` usa 0,65 e 3×3; `permissive` usa 0,35 e 7×7. A implementação mantém o maior componente conectado, aplica fechamento morfológico e rejeita áreas menores que 1% ou maiores que 90%.[2] [3]

A máscara afeta somente o mapa:

\[
S_{gate}(x,y)=normalize(S(x,y))\cdot \mathbf{1}[M(x,y)>0{,}5].
\]

A opacidade é:

\[
\alpha(x,y)=0{,}70\cdot S_{gate}(x,y)^{0{,}75}.
\]

A CNN usa Grad-CAM; o ViT usa atribuição `token × gradient`, com fallback de gradiente da entrada; o Hybrid combina Grad-CAM, tokens e rollout; o Ensemble agrega saliências.[2] A auditoria confirmou que pixels fora da saliência permanecem idênticos à imagem original. Isso é uma propriedade da renderização e não prova fidelidade, causalidade ou relevância clínica.[1]

**Trecho pronto para inserção.**

> O localizador auxiliar gera uma máscara provável de lesão e restringe somente as visualizações XAI. Com o preset `balanced`, a probabilidade de segmentação é binarizada em 0,50 e pós-processada com maior componente conectado e fechamento morfológico 5×5. No teste ISIC 2016, o localizador obteve Dice 0,8245 e IoU 0,7667. A máscara não participa do caminho de classificação, não altera classe ou probabilidade e não aumenta a acurácia por si só. O gate também não converte Grad-CAM, atribuição de tokens ou rollout em segmentação clínica ou explicação causal.

### 5.7 Aplicação full-stack

A versão auditada usa React 19, TypeScript e Vite no frontend. O backend usa Express, tRPC e Zod e chama módulos Python por processos controlados. Há suporte opcional a Drizzle e MySQL/MariaDB. Na demonstração auditada, o banco estava desligado e o histórico usava memória local, sendo perdido após reinicialização.[1] [2]

**Trecho pronto para inserção.**

> A interface foi implementada em React 19, TypeScript e Vite. O backend utiliza Express, tRPC e Zod e inicia módulos Python de inferência por processos controlados, com timeout e sem aceitar caminhos arbitrários fornecidos pelo usuário. Drizzle com MySQL/MariaDB está disponível como opção de persistência. Na demonstração auditada, imagens, diagnósticos e histórico utilizaram fallback em memória; portanto, os registros foram perdidos após a reinicialização do servidor. A arquitetura Django descrita na proposta inicial foi substituída e não corresponde à versão apresentada.

### 5.8 Resultados internos que podem ser reportados

| Modelo | Acurácia | Sensibilidade | Especificidade | AUROC | AUPRC | ECE |
|---|---:|---:|---:|---:|---:|---:|
| CNN | 0,7302 | 0,7333 | 0,7294 | 0,8293 | 0,5332 | 0,0544 |
| ViT | 0,7256 | **0,8533** | 0,6944 | 0,8500 | 0,5565 | **0,0456** |
| Hybrid | 0,7439 | 0,7967 | 0,7311 | 0,8370 | 0,4833 | 0,2269 |
| Ensemble | **0,7498** | 0,8233 | **0,7319** | **0,8600** | **0,5709** | 0,0706 |

Fonte documental: auditoria da versão `cb03a0e`, com 1.527 imagens no teste HAM10000.[1]

A interpretação deve ser moderada. O Ensemble lidera acurácia, especificidade, AUROC e AUPRC entre os registros apresentados. O ViT tem maior sensibilidade e menor ECE. O Hybrid tem ECE 0,2269, pior que os demais. Portanto, o Ensemble **não é superior em todos os critérios**.

**Trecho pronto para inserção.**

> No teste interno de 1.527 imagens, o Ensemble obteve acurácia 0,7498, sensibilidade 0,8233, especificidade 0,7319, AUROC 0,8600, AUPRC 0,5709 e ECE 0,0706. O ViT apresentou a maior sensibilidade, 0,8533, e o menor ECE, 0,0456. O Hybrid apresentou ECE 0,2269, indicando calibração relativa pior. Assim, o Ensemble obteve melhor discriminação agregada nas métricas reportadas, mas não foi superior em todos os critérios. Esses números provêm de avaliação interna congelada; não são acurácia clínica, não demonstram desempenho de 99% e não devem ser comparados diretamente a outros estudos sem harmonização de dataset, rótulos, partição e protocolo.

### 5.9 Resultados de auditoria de engenharia

A auditoria verificou `tsc --noEmit` sem erros, nove testes Vitest, build de produção, 12 testes Python aprovados e três ignorados, inferência CNN/ViT/Hybrid/Ensemble, quatro mapas PNG 600×450, upload, classificação, artefatos, histórico em uma sessão e rejeição de uma imagem não dermatológica.[1]

Os três testes ignorados dependem de cópia preparada do HAM10000 e ativos OOD externos ausentes do repositório. O build emitiu aviso de bundle JavaScript acima de 500 kB. Esses fatos devem ser registrados como cobertura incompleta e oportunidade de otimização.

Na imagem `ISIC_0027419.jpg`, o gate `balanced` ocupou aproximadamente 22,0% da entrada. As frações com saliência foram 10,22% na CNN, 22,42% no ViT e 15,33% no Hybrid; a diferença máxima fora da saliência foi zero nos quatro mapas.[1] Esses números descrevem um caso auditado de renderização, não desempenho médio de XAI.

Uma execução auditada levou cerca de 25 segundos, dos quais 13 segundos para classificação e 12 para mapas. A barra da interface é estimada, não telemetria do backend.[1] Qualquer conclusão sobre eficiência deve incluir hardware, repetições, distribuição de latência e memória.

## 6. Seção proposta de auditoria científica e de software

### 6.1 Objetivo e princípio

A auditoria deve separar duas perguntas:

- **Auditoria científica:** os dados, partições, métodos, resultados e conclusões são rastreáveis e reproduzíveis?
- **Auditoria de software:** a implementação executa o comportamento declarado, trata erros previsíveis e produz artefatos consistentes?

Aprovação de build, testes ou rota de upload não comprova validade científica. Da mesma forma, uma boa AUROC não comprova robustez do software, persistência, segurança ou rastreabilidade.

### 6.2 Identidade da versão auditada

A dissertação deve congelar e registrar:

- repositório, branch e commit;
- hash dos manifestos e listas de partição;
- hash dos checkpoints;
- versão do Python, PyTorch, `timm`, Node e dependências;
- seed de cada etapa;
- comandos de treino, avaliação, auditoria e inicialização;
- variáveis de ambiente relevantes;
- hardware e sistema operacional;
- data e responsável pela execução.

O ponto de partida disponível é `feat/scientific-ml-backend` no commit `cb03a0e`.[1]

### 6.3 Auditoria científica proposta

| Objeto | Verificação | Evidência mínima | Estado com os documentos atuais |
|---|---|---|---|
| Proveniência | Dataset, versão, licença e DOI | Manifesto e fonte oficial | Documentado para HAM10000 |
| Integridade | Imagens, metadados e faltantes | Contagens e hash | 10.015 linhas/imagens; 0 faltantes |
| Independência | Partição por grupo de lesão | Lista de grupos por split | Resumo documentado; anexar listas completas |
| Teste congelado | Ausência de seleção no teste | Histórico de experimentos | Declarado; requer logs/versionamento |
| Rótulo binário | Mapeamento das sete classes | Código e manifesto | Documentado |
| Treinamento | Hiperparâmetros completos | Configuração e logs | Parcial; recuperar campos ausentes |
| Ensemble | Pesos escolhidos na validação | Script e resultado da busca | Pesos documentados; anexar procedimento |
| Métricas | Recomputação a partir de predições | Predições por imagem e script | Valores documentados; publicar artefato derivado |
| Incerteza | Entropia, TTA e calibração | Código, parâmetros e curvas | Regras documentadas; avaliação seletiva pendente |
| OOD | Limiar e painel independente | Dados, rótulos e falsos aceites/rejeites | Teste funcional; avaliação científica pendente |
| Gate | Split ISIC e métricas | Lista do split e checkpoint | Dice/IoU documentados no ISIC 2016 |
| XAI | Fidelidade, estabilidade e sanidade | Protocolo e resultados | Renderização auditada; validade XAI pendente |
| Estatística | IC e comparação pareada | Bootstrap/teste predefinido | Não documentado; executar |
| Subgrupos | Tom de pele, localização e dispositivo | Metadados autorizados | Ausentes no manifesto atual |

### 6.4 Auditoria estatística mínima

Antes do depósito, recomenda-se gerar predições por imagem do teste congelado e calcular intervalos de confiança de 95% por bootstrap agrupado por lesão. Comparações entre modelos devem preservar o pareamento da mesma unidade. Se forem escolhidos testes estatísticos, a hipótese, a unidade de reamostragem, o número de réplicas e a correção para múltiplas comparações devem ser definidos antes da execução.

A análise deve incluir matriz de confusão binária, resultados por classe, macro-F1, balanced accuracy, curva ROC, curva precisão–revocação, Brier, curva de confiabilidade e ECE. Sensibilidade em especificidade prefixada e especificidade em sensibilidade prefixada são mais informativas para decisões delimitadas que acurácia isolada.

### 6.5 Auditoria de software proposta

| Camada | Teste | Critério de aceitação | Caveat |
|---|---|---|---|
| TypeScript | `tsc --noEmit` | Zero erros | Não mede comportamento em execução |
| Backend | Vitest | Todos os testes versionados aprovados | Cobertura deve ser reportada |
| Python | Pytest | Testes locais aprovados | Três casos externos continuam ignorados |
| Build | Vite/esbuild | Build concluído | Bundle >500 kB requer otimização |
| Checkpoints | Carga e hash | Hash e arquitetura compatíveis | Licença deve acompanhar distribuição |
| Inferência | Quatro saídas | CNN, ViT, Hybrid e Ensemble consistentes | Testar falhas e timeout |
| XAI | Dimensão e invariância | PNGs esperados; fundo inalterado | Não prova fidelidade científica |
| Upload | Validação de arquivo | Formatos e limites rejeitados corretamente | Incluir imagens corrompidas e adversariais |
| OOD | Casos positivos e negativos | Razões de rejeição registradas | Um caso não mede cobertura universal |
| Persistência | Reinício e recuperação | Estado conforme configuração | Fallback atual perde histórico |
| Segurança | Caminho, tamanho, timeout e erros | Sem caminho arbitrário; logs sem dados sensíveis | Não é auditoria de cibersegurança completa |
| Reprodutibilidade | Execução limpa | Ambiente reconstruído por instruções | Fixar versões e artefatos externos |

### 6.6 Relatório de auditoria a anexar

O apêndice deve conter: identificação da versão; ambiente; comandos; resultados de cada teste; falhas e testes ignorados; hashes; amostra dos artefatos; recomputação das métricas; discrepâncias encontradas; decisão “aprovado”, “aprovado com ressalva” ou “pendente” por item; e assinatura/data do responsável.

**Trecho pronto para inserção.**

> A auditoria verificou compilação TypeScript, testes automatizados, build de produção, inferência, geração de artefatos, upload, histórico local, carregamento de métricas e uma rejeição OOD. Essas verificações demonstram funcionamento do protótipo na versão e no ambiente registrados. Elas não substituem intervalos de confiança, análise de erro, validação externa, avaliação de subgrupos, comparação com especialistas ou estudo prospectivo. Por essa razão, os resultados de engenharia e os resultados científicos são apresentados em subseções distintas.

## 7. Plano de Continuidade do Mestrado

### 7.1 Objetivo do plano

O objetivo do Plano de Continuidade é transformar o texto de qualificação e o protótipo já desenvolvido em uma **dissertação final coerente, reproduzível e defensável**. O plano não exige que o sistema se torne produto clínico. Ele exige que o trabalho entregue corresponda ao que foi efetivamente implementado, que os resultados internos sejam recalculados com rigor, que o parecer seja respondido integralmente e que as limitações de população, domínio e aplicabilidade sejam declaradas.

O mestrado será concluído com cinco entregas centrais:

1. manuscrito corrigido, sem duplicações e com RSL reconciliada;
2. descrição fiel do sistema CNN–ViT–Hybrid–Ensemble e da aplicação React/TypeScript/Express/Python;
3. avaliação interna reprodutível, acompanhada de intervalos de confiança, calibração e análise de erro;
4. auditoria separada em evidência científica e verificação de software;
5. discussão explícita do parecer sobre tons de pele, população brasileira e lesões acrais, apoiada por validação externa exploratória quando tecnicamente viável.

### 7.2 Prioridades obrigatórias antes da defesa

#### Prioridade A — correção acadêmica e resposta ao parecer

Devem ser removidas as duplicações 2.2/2.5, 2.3/2.6 e 2.4/2.7. O fluxo da RSL deve ser recuperado no Parsifal para explicar 234 registros, 199 após a etapa correspondente e 51 estudos incluídos, caso esses números sejam confirmados. Erros de ortografia, concordância, citações e compilação devem ser corrigidos no fonte e confirmados no PDF. Esta prioridade é condição explícita do parecer.

#### Prioridade B — alinhamento entre dissertação e sistema desenvolvido

A dissertação deve substituir o plano ISIC-2019/Django pela implementação comprovada: HAM10000 para classificação; ISIC 2016 para o localizador auxiliar; CNN ResNet-50; ViT; Hybrid; Ensemble ponderado; React/TypeScript/Vite; Express/tRPC/Zod; e módulos Python/PyTorch. O texto deve separar claramente classificação, gate XAI, triagem OOD e interface.

#### Prioridade C — fechamento da avaliação científica interna

As predições por imagem do teste congelado devem ser arquivadas e usadas para recomputar métricas, matrizes de confusão e intervalos de confiança de 95% por bootstrap agrupado por lesão. Devem ser acrescentados macro-F1, balanced accuracy, Brier score e curva de calibração. A comparação entre modelos deve preservar o pareamento das mesmas lesões. Os resultados já documentados continuam válidos como ponto de partida, mas não substituem essa recomputação.

#### Prioridade D — resposta empírica mínima ao viés demográfico

O parecer não exige que o mestrado resolva a equidade clínica, mas exige que a lacuna seja tratada seriamente. O PAD-UFES-20 é uma opção de validação externa brasileira exploratória: contém 2.298 imagens clínicas de smartphone, 1.373 pacientes, 1.641 lesões e metadados que incluem tipo de pele Fitzpatrick; aproximadamente 58% das amostras possuem confirmação por biópsia.[8] Como o domínio difere da dermatoscopia HAM10000, uma queda de desempenho deve ser interpretada como evidência de mudança de domínio, não como falha de implementação.

O DDI também pode ser usado como avaliação externa autorizada de disparidade. O estudo original mostrou queda de AUROC de um modelo HAM10000 entre Fitzpatrick I–II e V–VI e demonstrou que desempenho no dataset de origem não garante transporte para tons de pele mais escuros.[9] Se licenças, mapeamento de rótulos ou tempo impedirem a execução, a dissertação deve apresentar o protocolo e declarar a avaliação como limitação, sem inventar resultado.

#### Prioridade E — auditoria e pacote de reprodução

Devem ser congelados commit, ambiente, versões, hashes dos checkpoints, manifestos, splits, comandos, logs e parâmetros. A dissertação deve usar TRIPOD+AI para conferir transparência de relato e desempenho por subgrupo, e PROBAST+AI para organizar risco de viés nos domínios participantes/fontes, preditores, desfecho e análise.[10] [11]

### 7.3 Experimentos do mestrado

| Bloco | Experimento | Entrega mínima | Critério de conclusão |
|---|---|---|---|
| Classificação | Recompor CNN, ViT, Hybrid e Ensemble no teste congelado | Predições por imagem e tabela de métricas | Script reproduz resultados documentados dentro da precisão definida |
| Estatística | Bootstrap agrupado por lesão | IC 95% para métricas principais | Seed, réplicas e unidade de reamostragem registrados |
| Calibração | ECE, Brier e curva de confiabilidade | Figura e tabela por modelo | Conjunto de calibração separado do teste |
| Incerteza | Curva risco–cobertura | AURC, cobertura e erro condicional | Limiares não escolhidos no teste final |
| OOD | Painel pequeno, rotulado e independente | Falsos aceites/rejeites por categoria | Categorias e limitações explicitadas |
| Gate | Sem gate, strict, balanced e permissive | Área, máscara inválida, Dice/IoU quando houver referência | Separar efeito visual de qualquer efeito no classificador |
| XAI | Fidelidade, estabilidade e teste de sanidade mínimos | Uma métrica de cada categoria | Não usar plausibilidade visual como prova causal |
| Eficiência | Latência e memória | Média, dispersão, hardware e repetições | Ambiente descrito e barra da UI não usada como cronômetro |
| Validação externa | PAD-UFES-20 e/ou DDI, se autorizados | Métricas globais e por subgrupo disponível | Sem ajuste no teste externo; rótulos compatibilizados previamente |

### 7.4 Cronograma proposto até a defesa

| Período | Atividades | Entregáveis |
|---|---|---|
| 17–30 de setembro de 2026 | Remover duplicações; corrigir linguagem, citações e compilação; recuperar fluxo Parsifal; congelar escopo e versão do sistema | Manuscrito estruturalmente corrigido; matriz de resposta ao parecer; release candidate do código |
| 1–15 de outubro de 2026 | Recuperar hiperparâmetros; arquivar predições; recomputar métricas; matrizes de confusão; bootstrap; calibração | Capítulo de Metodologia fechado; tabelas e figuras internas reproduzíveis |
| 16–31 de outubro de 2026 | Curva risco–cobertura; painel OOD; ablação do gate; testes mínimos de XAI; latência e memória | Capítulo de Resultados com auditoria científica e de engenharia |
| 1–10 de novembro de 2026 | Validação externa exploratória no PAD-UFES-20 e/ou DDI, se viável; análise de mudança de domínio, tons de pele e limitações | Subseção que responde diretamente ao parecer clínico; resultados ou protocolo justificado |
| 11–20 de novembro de 2026 | Escrever Discussão, Ameaças à Validade, Limitações, Conclusão e Trabalhos Futuros | Primeira versão integral da dissertação |
| 21–30 de novembro de 2026 | Revisão do orientador; correções metodológicas; referências ABNT; revisão ortográfica humana | Versão de pré-banca/depósito |
| 1–7 de dezembro de 2026 | Auditoria final do código, artefatos, PDF, logs, tabelas, figuras e checklist | Pacote final reproduzível e PDF sem erros |
| 8–15 de dezembro de 2026 | Preparar apresentação, demonstração controlada, perguntas da banca e versão de contingência | Slides, roteiro, demo testada e defesa simulada |

O cronograma deve ser ajustado à data oficial de depósito. Se uma etapa experimental ameaçar a entrega, a prioridade é preservar rigor: reduzir o objetivo e declarar a limitação é cientificamente melhor que apresentar um resultado incompleto ou não rastreável.

### 7.5 Critérios para considerar o mestrado pronto para defesa

O trabalho estará pronto quando o parecer tiver resposta verificável; o novo sumário corresponder ao texto; método, dados e software descreverem a versão real; métricas puderem ser reproduzidas; auditoria científica estiver separada da auditoria de engenharia; limitações demográficas e clínicas estiverem explícitas; e o pacote final contiver fonte, PDF, código, versões, checkpoints autorizados, hashes, splits, predições e logs.

### 7.6 O que não deve ser exigido para concluir o mestrado

Não é necessário criar uma coorte brasileira multicêntrica, executar estudo prospectivo, implantar aprendizado federado, obter autorização como dispositivo médico ou provar benefício ao paciente. Essas atividades exigem colaboração institucional, aprovação ética, amostra e tempo compatíveis com uma pesquisa posterior. O mestrado deve entregar um baseline rigoroso e auditável e indicar honestamente onde a evidência termina.

## 8. Limitações da dissertação e trabalhos futuros

### 8.1 Limitações que devem permanecer explícitas na dissertação

As limitações descrevem o alcance da evidência **já produzida**. Elas não devem ser redigidas como promessas de correção futura.

1. **Validação interna.** O teste agrupado reduz vazamento entre imagens da mesma lesão, mas permanece no domínio HAM10000. Não demonstra transporte para novos centros, pacientes, câmeras ou protocolos.
2. **Desbalanceamento.** O teste contém 300 imagens no agrupamento maligno e 1.227 nas demais classes. Classes raras têm contagens muito pequenas, como `df` com 10 e `vasc` com 29.[4]
3. **Rótulo operacional.** O agrupamento de `akiec` com classes malignas é uma decisão da tarefa e deve ser clinicamente justificado; não equivale a diagnóstico individual.
4. **Ausência de subgrupos.** O manifesto não contém dados suficientes de fototipo, tom de pele, população brasileira, lesão acral, dispositivo ou instituição.[4]
5. **Mudança de domínio.** HAM10000 e ISIC 2016 são dermatoscópicos; não há evidência para fotografia clínica ou celular.
6. **Gate externo ao classificador.** Dice e IoU foram medidos no ISIC 2016. O gate não altera a classificação e pode falhar com pelos, régua, bolhas, sombra ou iluminação.[3]
7. **XAI não causal.** Grad-CAM, tokens, rollout e agregação indicam sensibilidade aproximada, não razão causal ou correção clínica.[1]
8. **OOD limitado.** A rejeição de uma imagem externa comprova o caminho funcional, não reconhecimento universal.[1]
9. **Abstenção não validada clinicamente.** Entropia, variância e votos são regras configuráveis. Falta curva risco–cobertura e avaliação por subgrupo.
10. **Calibração heterogênea.** O ECE do Hybrid é 0,2269, substancialmente pior que o dos demais modelos.[1]
11. **Estatística incompleta.** Não foram apresentados intervalos de confiança ou testes pareados nos artefatos resumidos.
12. **Reprodutibilidade parcial.** Alguns hiperparâmetros, hardware e duração do treino não estão nos documentos fornecidos; três testes dependem de ativos externos não versionados.[1]
13. **Persistência limitada.** No modo auditado, o histórico em memória é perdido ao reiniciar o servidor.[1]
14. **Licenciamento.** HAM10000 é documentado como CC BY-NC 4.0 para uso acadêmico não comercial, e o checkpoint do gate deve respeitar os termos de origem.[3] [4]

**Trecho pronto para inserção.**

> Os resultados correspondem a avaliação interna congelada e não constituem validação clínica prospectiva. A divisão por grupos reduz o risco de vazamento entre imagens correlacionadas, mas não elimina mudança de domínio, viés de seleção ou dependência de equipamento. O manifesto não fornece evidência suficiente para analisar equidade entre fototipos, população miscigenada brasileira ou lesões acrais. O localizador foi avaliado no ISIC 2016 e restringe somente a visualização XAI; seus resultados não demonstram segmentação equivalente no HAM10000. Os mapas não provam causalidade, e a triagem OOD não reconhece universalmente todo objeto externo.

### 8.2 Atividades que ainda pertencem à dissertação

Estas atividades completam a promessa metodológica da dissertação e não devem ser empurradas automaticamente para o doutorado:

- recuperar e versionar a configuração completa de treino;
- recomputar as métricas a partir das predições por imagem;
- gerar intervalos de confiança por bootstrap agrupado;
- adicionar macro-F1, balanced accuracy, Brier e matrizes de confusão;
- comparar CNN, ViT, Hybrid e Ensemble por protocolo pareado;
- avaliar calibração com conjunto separado;
- construir curva risco–cobertura da regra de abstenção;
- executar painel OOD limitado e independente;
- quantificar XAI por pelo menos um teste de fidelidade, um de estabilidade e um de sanidade;
- comparar `sem gate`, `strict`, `balanced` e `permissive`, deixando claro que a função atual é visual;
- medir latência, memória e hardware com repetições;
- finalizar auditoria de software e pacote de reprodução.

Se tempo, dados ou registros impedirem uma dessas atividades, a dissertação deve declarar a pendência e reduzir o objetivo correspondente. Não é aceitável manter o objetivo e substituir o resultado por expectativa.

### 8.3 Trabalhos futuros após a dissertação

Os trabalhos futuros devem começar onde termina a evidência interna:

1. validação externa bloqueada em dataset autorizado;
2. coorte brasileira multi-institucional com tom de pele, localização acral, dispositivo e referência diagnóstica;
3. avaliação temporal e leave-one-center-out;
4. recalibração e adaptação de domínio sem vazamento do teste externo;
5. OOD semântico e classificação seletiva orientada a risco;
6. segmentação robusta no domínio-alvo e avaliação de falhas;
7. XAI quantitativo e avaliação por dermatologistas;
8. aprendizado federado, privacidade e dados não-IID;
9. estudo retrospectivo com leitores e, somente depois, modo silencioso prospectivo;
10. engenharia de persistência, segurança, monitoramento de deriva e documentação regulatória.

**Trecho pronto para inserção.**

> Como trabalhos futuros, propõe-se validar o sistema em instituições, dispositivos e períodos independentes; estudar desempenho e calibração por tom de pele e localização anatômica, com inclusão deliberada de lesões acrais; avaliar adaptação de domínio, OOD semântico e classificação seletiva; e conduzir avaliação de XAI com métricas quantitativas e especialistas. Estudos com leitores ou prospectivos dependerão de aprovação ética, governança de dados, referência diagnóstica adequada e critérios de segurança previamente definidos.

## 9. Perspectivas de doutorado após a conclusão do mestrado

### 9.1 Tese central

Esta seção **não integra o Plano de Continuidade do mestrado**. Ela registra uma linha de pesquisa posterior, condicionada à conclusão da dissertação, ingresso no doutorado, orientação, parcerias, aprovação ética e acesso a dados. A agenda doutoral não deve buscar apenas uma nova variação de CNN–ViT. A pergunta central deve migrar de “qual arquitetura tem a maior métrica no benchmark?” para:

> **Em quais populações, instituições, dispositivos e condições um sistema multimodelo permanece discriminativo, calibrado e útil, e em quais situações deve se abster ou deixar de produzir uma classificação?**

A contribuição esperada é um protocolo de evidência para robustez, equidade, segurança e translação clínica. Queda de desempenho, ausência de benefício ou identificação de condições de não uso são resultados científicos válidos.

### 9.2 Perguntas de pesquisa

**RQ1.** Qual é a diferença de discriminação, calibração e cobertura seletiva entre CNN, ViT, Hybrid e Ensemble por grupo de lesão, instituição, dispositivo, tom de pele e localização anatômica, com ênfase acral?

**RQ2.** Quanto do desempenho interno se perde sob validação externa, e quais componentes de mudança de domínio explicam a perda?

**RQ3.** Recalibração ou adaptação local reduz ECE e Brier sem degradar sensibilidade nos subgrupos vulneráveis?

**RQ4.** Um detector que combine mudança covariável e OOD semântico reduz classificações indevidas em imagens externas sem rejeitar excessivamente casos dermatológicos válidos?

**RQ5.** Qual política de classificação seletiva minimiza risco entre casos aceitos para uma cobertura operacional previamente definida?

**RQ6.** Segmentação e gate melhoram localização, fidelidade e estabilidade das explicações, e em quais condições cortam evidência útil ou incluem fundo?

**RQ7.** Em que medida métricas quantitativas de XAI se alinham à avaliação de dermatologistas?

**RQ8.** Treinamento federado e mecanismos de privacidade preservam utilidade, calibração e equidade aceitáveis em dados não-IID?

**RQ9.** O uso assistido melhora decisão, tempo e encaminhamento de especialistas em estudo controlado, ou produz automation bias?

**RQ10.** Quais controles de risco, rastreabilidade, cibersegurança e monitoramento são necessários para uma finalidade pretendida delimitada?

### 9.3 Hipóteses falsificáveis

- **H1:** mudança de domínio reduzirá desempenho e/ou calibração em centros, dispositivos, tons de pele e locais anatômicos não representados. A hipótese será rejeitada se diferenças clinicamente relevantes não forem observadas sob intervalos adequados.
- **H2:** recalibração no domínio-alvo reduzirá ECE e Brier nesse domínio, mas não necessariamente AUROC ou transporte para outro centro.
- **H3:** OOD semântico independente reduzirá falsos aceites externos ao custo de algum aumento em falsos rejeites dermatológicos.
- **H4:** reduzir cobertura por abstenção diminuirá risco condicional, mas pode tornar o fluxo inviável ou reduzir sensibilidade em subgrupos.
- **H5:** o gate melhorará métricas de localização, fidelidade ou estabilidade visual, sem pressupor ganho de classificação.
- **H6:** federado com agregação segura apresentará trade-off entre utilidade, pior centro, comunicação e privacidade; a direção não é presumida.
- **H7:** melhor fidelidade automática de XAI não implicará necessariamente maior concordância ou melhor decisão clínica.
- **H8:** assistência de IA terá efeito heterogêneo entre leitores e poderá causar automation bias.

### 9.4 Camadas de dados

- **D0 — baseline interno:** HAM10000 atual, split por grupo, teste congelado e sete classes.
- **D1 — validação pública/externa:** conjuntos públicos ou autorizados, sem ajuste de limiares.
- **D2 — coorte brasileira:** dados multi-institucionais, múltiplos dispositivos, tempo, localização anatômica, lesões acrais, tom de pele coletado por protocolo ético e padrão de referência.
- **D3 — painel OOD:** baixa qualidade, outro domínio dermatoscópico, fotografia clínica, conteúdo dermatológico fora da tarefa e objetos não dermatológicos.

### 9.5 Desenhos experimentais

| RQ | Desenho | Comparadores | Desfechos primários | Unidade e análise | Critério de refutação/decisão |
|---|---|---|---|---|---|
| RQ1 | Validação estratificada e hierárquica | CNN, ViT, Hybrid, Ensemble | Sensibilidade, AUPRC, ECE, risco–cobertura | Lesão/paciente; IC por centro e subgrupo | Não declarar diferença se IC for inconclusivo |
| RQ2 | Validação externa bloqueada e leave-one-center-out | Interno vs. centros externos | Queda absoluta/relativa, Brier, ECE | Centro e lesão; modelo hierárquico | Generalização rejeitada se queda exceder margem predefinida |
| RQ3 | Estudo de recalibração/adaptação com conjuntos separados | Sem ajuste, temperatura, método não paramétrico, adaptação | ECE, Brier, sensibilidade fixa | Calibração distinta do teste | Método falha se melhora um domínio e degrada outro além da margem |
| RQ4 | Painel OOD independente | Distância atual, baseline semântico, combinação | AUROC-OOD, AUPR-OOD, FPR@TPR, falso aceite/rejeite | Imagem e categoria OOD | Rejeitar método sem vantagem consistente e com rejeição clínica excessiva |
| RQ5 | Classificação seletiva | Regra atual, entropia, variância, score aprendido | AURC, risco condicional, cobertura | Lesão e subgrupo | Política inadequada se risco não cair ou cobertura útil colapsar |
| RQ6 | Fatorial de gate/XAI | Sem gate, strict, balanced, permissive; métodos XAI | Dice/IoU, deletion/insertion, estabilidade, falha | Imagem e anotação | Não alegar ganho se só houver plausibilidade visual |
| RQ7 | Estudo cego com especialistas | Métodos XAI e imagem sem mapa | Concordância, utilidade, erro, confiança | Leitor e caso; modelo misto | Métrica automática não validada se não se alinha ao desfecho predefinido |
| RQ8 | Experimento federado multi-institucional ou simulado | Centralizado, local, FedAvg/alternativa | AUROC/AUPRC, pior centro, privacidade, comunicação | Centro e rodada | Não alegar equivalência sem margem e poder definidos |
| RQ9 | Estudo cruzado randomizado com leitores | Sem IA vs. IA | Sensibilidade, especificidade, tempo, encaminhamento | Leitor–caso; ordem randomizada | Benefício rejeitado se efeito for nulo/heterogêneo ou houver dano relevante |
| RQ10 | Engenharia de requisitos e modo silencioso | Baseline vs. monitorado | Incidentes, deriva, disponibilidade, rastreabilidade | Período e versão | Uso assistivo não avança sem gates éticos e de segurança |

### 9.6 Métricas e plano estatístico

Para classificação, usar AUROC e AUPRC, sensibilidade em especificidade fixa, especificidade em sensibilidade fixa, macro-F1, balanced accuracy e matriz de confusão. Para calibração, usar ECE, Brier e curva de confiabilidade. Para classificação seletiva, usar risco–cobertura, AURC, erro condicional, cobertura no risco máximo prefixado e taxa de encaminhamento. Para OOD, usar AUROC-OOD, AUPR-OOD, FPR em TPR fixada, falso aceite e falso rejeite.

As análises devem ser pré-registradas. Nenhum limiar pode ser escolhido no teste externo. Centro, paciente e lesão devem ser tratados de acordo com a dependência dos dados. Classes e subgrupos raros devem ser apresentados com incerteza ampla, sem conclusão de equivalência baseada apenas em ausência de significância.

### 9.7 Equidade e coorte brasileira

Tom de pele, raça, origem e localização anatômica são variáveis sensíveis e distintas. Não se deve inferi-las automaticamente da imagem sem validação e justificativa. A coleta precisa de aprovação ética, governança, desidentificação e protocolo reprodutível. O desenho deve incluir intencionalmente lesões acrais e centros fora de uma única referência, mas não pode prometer representatividade nacional antes de verificar a amostra.

A análise deve reportar desempenho e calibração por grupo, interseções relevantes, pior grupo e amplitude entre grupos. Uma aparente melhora média não compensa degradação inaceitável de sensibilidade em subgrupo vulnerável.

### 9.8 Privacidade e aprendizado federado

O estudo deve começar por um modelo de ameaça. Comparar treinamento centralizado, local e federado em dados não-IID por centro. Se forem usados agregação segura ou privacidade diferencial, registrar parâmetros, orçamento de privacidade, ataques testados, comunicação e perda de utilidade. Uma simulação federada deve ser rotulada como simulação, não como implantação hospitalar.

### 9.9 Avaliação com especialistas e translação

Somente após validação externa e critérios de segurança, executar estudo retrospectivo randomizado com condição sem IA e com IA. Medir desempenho, tempo, confiança, encaminhamento, discordância e automation bias. Um estudo prospectivo inicial deve ocorrer em modo silencioso, sem influenciar cuidado, salvo aprovação ética e institucional específica.

A tese pode mapear finalidade pretendida, população, exclusões, risco de falso negativo, cibersegurança, versionamento, monitoramento e controle de mudanças. Esse mapeamento não certifica nem autoriza o produto.

### 9.10 Cronograma em quatro anos

| Período | Entregas | Gate de continuidade |
|---|---|---|
| Ano 1 | Baseline publicado; protocolo pré-registrado; ablações; calibração; OOD; classificação seletiva; XAI; submissões éticas | Configuração reproduzível, teste congelado e aprovações em andamento |
| Ano 2 | Coorte brasileira auditada; validação por centro, dispositivo, tom de pele e localização; análise de domain shift | Qualidade de rótulos, tamanho de subgrupos e precisão dos ICs |
| Ano 3 | Recalibração/adaptação; OOD semântico; segmentação robusta; federado e privacidade | Teste externo final ainda intocado e colaboração institucional ativa |
| Ano 4 | Estudo com leitores; modo silencioso se autorizado; análise de risco; monitoramento; artigos e tese | Evidência suficiente, aprovação ética e ausência de dano operacional não mitigado |

### 9.11 Critério de sucesso doutoral

O doutorado só deve reivindicar avanço quando houver melhoria predefinida, intervalo de confiança compatível, ausência de degradação inaceitável nos subgrupos e replicação em centro ou período independente. Se nenhuma intervenção melhorar os desfechos, a contribuição pode ser a demonstração reprodutível dos limites e a definição de condições de não uso.


## 10. Declaração obrigatória de limites clínicos

Esta declaração deve aparecer no resumo, na metodologia, na discussão, na conclusão, na interface e em qualquer apresentação pública. Versões abreviadas podem ser usadas, mas não devem omitir a ausência de validação clínica.

> **Declaração de limites clínicos.** O SkinCancerCADDermoIA é um protótipo acadêmico de pesquisa para classificação experimental de imagens dermatoscópicas. Não é dispositivo médico, não fornece diagnóstico, não substitui anamnese, exame clínico, dermatoscopia por especialista, biópsia ou avaliação histopatológica. As métricas disponíveis provêm de teste interno do HAM10000 e não demonstram eficácia prospectiva, benefício ao paciente, equidade entre tons de pele, validade para a população brasileira, desempenho em lesões acrais, generalização para fotografias clínicas ou celulares, nem segurança em novos equipamentos e instituições. Confiança do modelo, entropia, variância TTA e abstenção são sinais computacionais, não probabilidades clínicas. Mapas de saliência e máscaras auxiliares não provam causalidade nem identificam necessariamente toda a lesão. A triagem OOD reduz alguns usos incompatíveis, mas não rejeita universalmente imagens externas. Qualquer estudo com pessoas, uso assistivo ou integração em fluxo de cuidado depende de aprovação ética, governança institucional, validação independente e enquadramento regulatório aplicável.

### 10.1 Formulações permitidas e formulações a evitar

| Evitar | Preferir | Razão |
|---|---|---|
| “sistema de diagnóstico” | “protótipo acadêmico de classificação” | Não há validação clínica nem autorização diagnóstica |
| “detecta câncer” | “estima classe binária operacional em imagens dermatoscópicas” | A tarefa usa rótulos e agrupamento computacional |
| “confiança clínica” | “probabilidade/confiança do modelo” | Score do modelo não é probabilidade clínica validada |
| “explicação causal” | “mapa de saliência aproximado” | Gradientes e atenção não provam causalidade |
| “segmentação da lesão no HAM10000” | “gate avaliado no ISIC 2016 e aplicado à visualização” | Dice/IoU não foram medidos no domínio de classificação |
| “o Ensemble é superior” | “o Ensemble liderou métricas específicas no teste interno” | ViT liderou sensibilidade e ECE |
| “rejeita imagens fora do domínio” | “rejeitou o caso externo auditado; cobertura ampla não foi demonstrada” | Um exemplo não autoriza universalização |
| “generaliza para o Brasil” | “generalização brasileira não foi avaliada” | Faltam coorte e metadados de subgrupo |
| “99% de acurácia” | “resultados internos da Seção 5.8” | Números próximos de 99% pertencem à literatura, não ao protótipo |

## 11. Checklist de revisão e depósito

O checklist deve ser executado no arquivo-fonte e novamente no PDF renderizado. Uma correção textual só pode ser marcada como concluída depois da inspeção visual.

### 11.1 Estrutura e sumário

- [ ] Remover as duplicações 2.2/2.5, 2.3/2.6 e 2.4/2.7.
- [ ] Incorporar somente conteúdo não redundante e rastrear seu destino.
- [ ] Renumerar todas as seções subsequentes.
- [ ] Renomear a seção de questões de pesquisa atualmente repetida como critérios.
- [ ] Decidir e corrigir a hierarquia de 3.2.1.1/3.2.2.
- [ ] Gerar sumário, lista de figuras e lista de tabelas automaticamente.
- [ ] Conferir títulos do sumário contra o corpo e eliminar redundância conceitual.

### 11.2 RSL e referências

- [ ] Recuperar no Parsifal os totais de identificação, duplicatas, triagem, texto completo e inclusão.
- [ ] Reconciliar 234, 199 e 51 sem inferir valores ausentes.
- [ ] Explicar PICO ou PICO-C e usar nomenclatura consistente.
- [ ] Corrigir chamadas de tabelas e referências cruzadas.
- [ ] Converter `[49]` e `[1]–[4]` para autor-data.
- [ ] Conferir sufixos 2025a/2025b/2025c e correspondência entre citações e bibliografia.
- [ ] Identificar dataset, tarefa, partição e fonte em cada linha de tabela de literatura.
- [ ] Remover ou rastrear a tabela autoral com 89,45%–94,23%.
- [ ] Separar resultados de literatura dos resultados do sistema.

### 11.3 Linguagem e terminologia

- [ ] Corrigir “solução promissora” no fonte e no PDF.
- [ ] Confirmar “padrasto” nos Agradecimentos.
- [ ] Corrigir “selecionandos”, “citerios”, “exlusão” e “elecionados”.
- [ ] Corrigir “O pré-processamento”.
- [ ] Corrigir espaços após pontuação, como `Dr.Edward`, `foi.Com` e `ensinou.Que`, se presentes.
- [ ] Revisar gênero, número, concordância, regência, pontuação e acentuação.
- [ ] Substituir linguagem diagnóstica por classificação experimental quando se referir ao protótipo.
- [ ] Executar revisão humana integral, além do corretor automático.

### 11.4 Dados, método e resultados

- [ ] Corrigir HAM10000 para “10000 Training Images” e informar separadamente 10.015 imagens.
- [ ] Descrever sete classes, agrupamento binário, 7.470 grupos, seed 42 e partições.
- [ ] Substituir ISIC-2019 por HAM10000 na classificação, salvo experimento comprovado.
- [ ] Manter ISIC 2016 somente no localizador auxiliar.
- [ ] Atualizar Django para React/TypeScript/Vite, Express/tRPC/Zod e Python.
- [ ] Documentar CNN, ViT, Hybrid e pesos 0,10/0,55/0,35.
- [ ] Recuperar hiperparâmetros dos logs; marcar ausências sem inventar.
- [ ] Reportar a tabela auditada com 1.527 imagens.
- [ ] Explicar que ViT liderou sensibilidade e que Ensemble não liderou todos os critérios.
- [ ] Destacar ECE 0,2269 do Hybrid.
- [ ] Acrescentar intervalos de confiança e testes apenas depois de executados.
- [ ] Não chamar métricas internas de validação clínica.

### 11.5 Gate, XAI, OOD e abstenção

- [ ] Desenhar caminhos separados para classificação e gate.
- [ ] Informar ISIC 2016, 720/90/90, 160×160, Dice 0,8245 e IoU 0,7667.
- [ ] Documentar `strict`, `balanced` e `permissive`.
- [ ] Declarar que o gate não altera classe nem probabilidade.
- [ ] Declarar fallback e limites de área de 1% e 90%.
- [ ] Tratar diferença zero fora da saliência como teste de renderização.
- [ ] Não atribuir causalidade aos mapas.
- [ ] Tratar OOD como barreira estatística limitada e abstenção como regra operacional.
- [ ] Identificar ablações planejadas como não executadas.

### 11.6 Auditoria, compilação e prova final

- [ ] Fixar branch, commit, hashes e versões de dependências.
- [ ] Anexar manifesto, listas de split, comandos e logs.
- [ ] Registrar 12 testes Python aprovados, três ignorados e aviso de bundle acima de 500 kB.
- [ ] Testar persistência com e sem banco e descrever o modo apresentado.
- [ ] Corrigir `\tilde{A}` e remover o preâmbulo LaTeX visível no corpo.
- [ ] Compilar com log sem erro relevante e revisar cada página do PDF.
- [ ] Conferir páginas em branco, quebras, hifens, tabelas e figuras.
- [ ] Atualizar referências a páginas somente após a paginação final.
- [ ] Arquivar fonte, PDF, log e checklist da versão depositada.

### 11.7 Validade clínica, ética e equidade

- [ ] Inserir a declaração de limites clínicos da Seção 10.
- [ ] Declarar ausência de validação prospectiva, externa, celular e fotografia clínica.
- [ ] Declarar ausência de avaliação suficiente por tom de pele e localização acral.
- [ ] Não inferir equidade a partir da média global.
- [ ] Não apresentar score de confiança como risco clínico ou sugerir benefício ao paciente.
- [ ] Respeitar licença e termos dos datasets/checkpoints.
- [ ] Condicionar estudos com pessoas à aprovação ética e governança.

## 12. Matriz comentário–ação–evidência

| ID | Comentário ou achado | Prioridade | Ação verificável | Evidência de conclusão | Estado inicial |
|---|---|---|---|---|---|
| P01 | Mérito e relevância | Preservar | Limitar contribuições à evidência disponível | Resumo e conclusão sem alegação clínica | Pendente na nova versão |
| P02 | Duplicação do Capítulo 2 | Obrigatória | Remover 2.5–2.7 redundantes | Comparação textual, sumário e PDF | Pendente |
| P03 | “promissula/promissor” | Obrigatória | Corrigir para “solução promissora” | Busca no fonte e inspeção visual | Pendente |
| P04 | “padastro/padrasto” | Obrigatória | Confirmar “padrasto” | Fonte e PDF final | A verificar |
| P05 | Erros e fluxo em 3.2.1 | Obrigatória | Reescrever seleção da RSL | Números do Parsifal e parágrafo final | Pendente |
| P06 | “A pré-processamento” | Obrigatória | Corrigir concordância | Busca global sem ocorrências | Pendente |
| P07 | “Ali et al. [49]” | Obrigatória | Normalizar autor-data | Busca por citações numéricas | Pendente |
| P08 | HAM10000 como 100000 | Obrigatória | Corrigir nome e separar 10.015 imagens | Fonte, PDF e tabela de dados | Pendente |
| P09 | `\tilde{A}`/compilação | Obrigatória | Corrigir sintaxe e inspecionar PDF | Log e prova visual | Pendente |
| P10 | Três pares repetidos | Obrigatória | Auditar cada par | Matriz de destino e busca textual | Pendente |
| P11 | Tons de pele e lesões acrais | Alta | Criar limitação e protocolo externo | Introdução, Discussão e Futuro | Pendente |
| P12 | Aprovação condicional | Crítica | Executar checklist integral | Novo PDF, log e checklist | Pendente |
| A01 | Sumário repete critérios | Obrigatória | Renomear “Questões de Pesquisa” | Sumário e corpo coerentes | Pendente |
| A02 | RSL alterna 234/199/51 | Obrigatória | Explicar cada etapa | Fluxograma e registro Parsifal | Pendente |
| A03 | Tabelas e referências cruzadas | Obrigatória | Regenerar e conferir chamadas | Lista de conferência por tabela | Pendente |
| A04 | Tabela de 89,45%–94,23% | Obrigatória | Rastrear ou remover | Fonte por linha ou exclusão | Pendente |
| A05 | Objetivos alternam escopo | Obrigatória | Alinhar quatro componentes e tarefa | Objetivos, método e resultados consistentes | Pendente |
| A06 | Django diverge do sistema | Obrigatória se sistema atual | Atualizar arquitetura | Figura e texto React/Express/Python | Pendente |
| A07 | ISIC-2019 diverge do experimento | Obrigatória se sistema atual | Usar HAM10000 e separar ISIC 2016 | Seção de dados revisada | Pendente |
| A08 | Gate não descrito | Obrigatória para XAI | Criar seção própria | Dados, presets, equação e limites | Pendente |
| A09 | Métricas internas sem IC | Alta | Bootstrap agrupado | Script, seed e tabela com IC | Não executado |
| A10 | OOD baseado em um caso | Alta | Painel independente | Métricas e catálogo de erros | Não executado |
| A11 | XAI sem fidelidade/sanidade | Alta | Executar protocolo quantitativo | Deletion/insertion, estabilidade e randomização | Não executado |
| A12 | Persistência em memória | Alta | Documentar e testar reinício | Teste e ressalva no texto | Parcialmente auditado |
| A13 | Três testes Python ignorados | Média | Versionar ativos ou justificar | Suite completa ou caveat permanente | Pendente |
| A14 | Bundle >500 kB | Média | Otimizar ou registrar | Relatório de build | Pendente |
| A15 | Resíduo de preâmbulo na p. 60 | Obrigatória | Remover comandos impressos | Prova visual | Pendente |
| A16 | Limites clínicos insuficientes | Crítica | Inserir declaração da Seção 10 | Resumo, discussão e interface | Pendente |

## 13. Trechos-modelo consolidados

Os trechos seguintes podem ser inseridos após ajuste de numeração e citações. Eles foram redigidos sem inventar referências ou resultados.

### 13.1 Título sugerido

> **Protótipo acadêmico de classificação de lesões dermatoscópicas com CNN, Vision Transformer, Ensemble e saliência restrita por localização**

### 13.2 Resumo sugerido

> Este trabalho desenvolve e avalia tecnicamente um protótipo acadêmico de apoio à classificação de imagens dermatoscópicas. O sistema compara uma rede neural convolucional, um Vision Transformer e um modelo híbrido e combina suas probabilidades em um Ensemble ponderado. O pipeline incorpora triagem de qualidade e domínio, Test-Time Augmentation, estimativas de incerteza, política de abstenção e mapas de saliência. A classificação utiliza o HAM10000 com divisão por grupos de lesão e teste congelado de 1.527 imagens. No teste interno, o Ensemble obteve acurácia 0,7498, sensibilidade 0,8233, especificidade 0,7319, AUROC 0,8600, AUPRC 0,5709 e ECE 0,0706. Separadamente, um localizador treinado no ISIC 2016 restringe somente as visualizações XAI e obteve Dice 0,8245 e IoU 0,7667 no teste desse dataset. Os resultados demonstram viabilidade técnica interna, mas não constituem diagnóstico, validação clínica prospectiva, prova causal das explicações ou evidência de generalização para fotografias clínicas, população brasileira, tons de pele ou lesões acrais.

### 13.3 Reconciliação com a proposta de qualificação

> A proposta de qualificação previa classificação no ISIC-2019 e uma interface Python/Django. Durante o desenvolvimento, o protocolo foi consolidado no HAM10000 para classificação, enquanto o ISIC 2016 Part 1 foi utilizado separadamente para o localizador auxiliar de XAI. A aplicação entregue foi implementada em React/TypeScript/Vite no frontend e Express/tRPC/Zod no servidor, com módulos Python de inferência. Esta seção descreve a versão efetivamente auditada; a arquitetura e os dados originalmente planejados são tratados como histórico do projeto, não como implementação corrente.

### 13.4 Discussão dos resultados

> O Ensemble apresentou os maiores valores de acurácia, especificidade, AUROC e AUPRC entre os registros internos, mas não dominou todos os critérios. O ViT alcançou a maior sensibilidade e o menor ECE. O Hybrid apresentou ECE 0,2269, sugerindo pior calibração relativa. Esses resultados desaconselham uma narrativa de superioridade geral e indicam que a escolha do modelo depende do desfecho priorizado. Como todos os resultados provêm do mesmo teste interno HAM10000, eles não estimam diretamente desempenho em novos centros, dispositivos ou grupos demográficos.

### 13.5 RSL com campos pendentes

> Foram recuperados 234 registros nas cinco bases. Após a remoção de **[número confirmado]** duplicatas, permaneceram **[número confirmado]** registros para triagem. Em seguida, **[número confirmado]** textos completos foram avaliados e 51 estudos foram incluídos. Os valores entre colchetes devem ser preenchidos a partir do registro do Parsifal; não foram inferidos a partir da diferença entre totais divergentes do manuscrito.

### 13.6 Conclusão sugerida

> Os resultados demonstram a viabilidade técnica de integrar classificação, Ensemble, triagem, incerteza, abstenção e explicabilidade em um protótipo dermatoscópico. A avaliação interna não demonstra eficácia clínica, equidade, causalidade das explicações ou transporte para fotografias clínicas e população brasileira. A principal contribuição da dissertação é um baseline reproduzível e auditável, acompanhado de uma caracterização explícita das falhas e das condições em que as saídas não devem ser interpretadas como decisão clínica. O avanço seguinte exige validação externa estratificada, calibração, avaliação de risco seletivo, análise de XAI e participação de especialistas sob governança ética.

## 14. Critérios de aceite da revisão

A revisão pode ser considerada pronta para submissão somente quando: (1) os três pares duplicados forem removidos e a estrutura recompilada; (2) o fluxo da RSL for reconciliado com o Parsifal; (3) citações e referências usarem um único padrão autor-data; (4) erros linguísticos e de compilação forem corrigidos e inspecionados; (5) dados, arquitetura e resultados corresponderem à versão auditada; (6) números sem rastreabilidade forem removidos ou referenciados; (7) resultados científicos e testes de engenharia estiverem separados; (8) limitações da dissertação não forem confundidas com trabalhos futuros; (9) a declaração de limites clínicos aparecer nos pontos de maior visibilidade; e (10) fonte, PDF, log, manifestos, scripts e checklist forem arquivados com versão identificável.

Até que esses critérios sejam comprovados em nova compilação, o estado correto é **revisão planejada, não correção concluída**.

## Referências

[1]: file:///home/ubuntu/work/SkinCanceIA/docs/PRESENTATION_AUDIT_2026-09-17.md "Auditoria pré-apresentação do SkinCancerCADDermoIA"

[2]: file:///home/ubuntu/work/SkinCanceIA/docs/PROFESSOR_PRESENTATION_GUIDE.md "Roteiro de apresentação ao professor e propostas para o artigo"

[3]: file:///home/ubuntu/work/SkinCanceIA/docs/LESION_SEGMENTATION.md "Localização da lesão para explicabilidade"

[4]: file:///home/ubuntu/work/SkinCanceIA/docs/datasets/HAM10000_MANIFEST.json "Manifesto do dataset HAM10000 usado no projeto"

[5]: file:///home/ubuntu/work/SkinCanceIA/docs/datasets/HAM10000_SPLIT_SUMMARY.csv "Resumo das partições do HAM10000"

[6]: https://doi.org/10.7910/DVN/DBW86T "HAM10000 Dataset, Harvard Dataverse"

[7]: https://challenge.isic-archive.com/data/ "ISIC Challenge Datasets"

[8]: https://data.mendeley.com/datasets/zr7vgbcyr2/1 "PAD-UFES-20: a skin lesion dataset composed of patient data and clinical images collected from smartphones"

[9]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9374341/ "Disparities in dermatology AI performance on a diverse, curated clinical image set"

[10]: https://www.bmj.com/content/385/bmj-2023-078378 "TRIPOD+AI statement: updated guidance for reporting clinical prediction models"

[11]: https://www.bmj.com/content/388/bmj-2024-082505 "PROBAST+AI: quality, risk of bias, and applicability assessment tool"

[12]: https://www.scielo.br/j/abd/a/XFLJ37RNwYSY6kBwPGQgSyj/?lang=en "Plantar acral melanoma: a Brazilian cohort"
