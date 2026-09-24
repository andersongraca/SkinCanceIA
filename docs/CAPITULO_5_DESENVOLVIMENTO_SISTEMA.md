# 5 Desenvolvimento e implementação do sistema

## 5.1 Apresentação do capítulo

Este capítulo descreve o desenvolvimento do sistema SkinCancerCADDermoIA, desde a organização dos dados até a apresentação dos resultados na interface web. O texto substitui o capítulo anteriormente intitulado “Plano de continuidade”, que deverá ser reescrito posteriormente como parte do planejamento acadêmico da dissertação. O foco aqui é registrar o que foi efetivamente implementado, quais ferramentas foram utilizadas, como os módulos se comunicam e de que maneira o sistema foi testado.

A implementação foi conduzida como um protótipo acadêmico de Diagnóstico Auxiliado por Computador (Computer-Aided Diagnosis, CAD). O sistema recebe uma imagem dermatoscópica, verifica sua elegibilidade, executa três modelos de aprendizado profundo, calcula medidas de incerteza e apresenta uma saída agregada acompanhada por mapas de explicabilidade. A ferramenta não substitui a avaliação dermatológica, não produz diagnóstico clínico autônomo e não foi submetida a validação prospectiva com pacientes.

A distinção entre proposta e implementação é importante. No capítulo anterior, foi descrita uma interface baseada em Python/Django e uma avaliação prevista com o ISIC-2019. Na versão implementada, a interface foi construída com React e TypeScript, o backend utiliza Express e tRPC, e o experimento principal de classificação foi realizado com o HAM10000. O ISIC 2016 foi empregado em um módulo auxiliar de localização de lesão para restringir visualmente os mapas de explicabilidade. Essa atualização evita que a dissertação descreva como concluída uma arquitetura diferente daquela que foi realmente executada.

## 5.2 Objetivo do sistema desenvolvido

O objetivo do sistema é oferecer um ambiente integrado para a análise experimental de imagens dermatoscópicas. Em vez de apresentar somente uma classe final, a ferramenta preserva informações intermediárias que permitem acompanhar o caminho computacional da análise. Entre essas informações estão o resultado da triagem, o escore de qualidade, o escore fora do domínio, as previsões dos modelos individuais, a incerteza estimada, os mapas de explicabilidade e as métricas do experimento.

A ferramenta foi organizada em quatro etapas principais. A primeira corresponde ao recebimento e à validação da imagem. A segunda realiza a triagem de qualidade e de compatibilidade com o domínio de referência. A terceira executa os modelos CNN, Vision Transformer e Hybrid. A quarta organiza os resultados e apresenta a classificação, os escores, o histórico da sessão, as métricas e os mapas de explicabilidade.

Esse desenho segue uma preocupação metodológica presente na literatura de sistemas CAD: a predição deve ser acompanhada por mecanismos que permitam observar a qualidade da entrada, o comportamento do modelo e os limites de generalização. Estudos que comparam CNNs, Transformers e modelos híbridos em imagens de pele ressaltam que o desempenho isolado não é suficiente para caracterizar a utilidade de um sistema, especialmente quando há desequilíbrio entre classes e diferenças entre bases de imagens \cite{ref_8, ref_18, ref_22}.

## 5.3 Organização dos dados e definição do problema

**A definição do problema experimental exigiu decisões sobre a unidade de análise, os rótulos, o particionamento e as condições de entrada. Essas decisões determinam o significado das métricas e reduzem fontes conhecidas de viés, como a presença de imagens da mesma lesão em mais de um subconjunto. Nesta seção são apresentados o dataset utilizado, a formulação das tarefas multiclasses e binária, o pré-processamento e o mecanismo empregado para impedir que entradas incompatíveis com o domínio dermatoscópico avancem para os classificadores.**

### 5.3.1 Dataset utilizado

A classificação foi desenvolvida com o HAM10000, conjunto que reúne 10.015 imagens dermatoscópicas distribuídas em sete categorias diagnósticas. As classes utilizadas no experimento são `akiec`, `bcc`, `bkl`, `df`, `mel`, `nv` e `vasc`. O manifesto produzido pelo projeto registra 7.470 grupos de lesão. Essa informação é relevante porque uma mesma lesão pode aparecer em mais de uma imagem; portanto, a divisão dos dados não deve considerar somente o nome do arquivo, mas também a identidade da lesão.

**O HAM10000 é adequado como benchmark de classificação dermatoscópica, mas não deve ser tratado como uma representação completa da população brasileira. O artigo que apresenta o conjunto descreve imagens provenientes de diferentes fontes e modalidades de aquisição, porém o metadata utilizado neste projeto não fornece um rótulo validado de tom de pele ou fototipo de Fitzpatrick. Assim, não é metodologicamente correto estimar, a partir do HAM10000 isoladamente, a distribuição de fototipos da amostra ou afirmar que o desempenho observado se mantém em pessoas com pele mais escura \cite{ref_44, ref_42}.**

O particionamento foi realizado com a seed 42, mantendo grupos de lesão separados entre treinamento, validação e teste. O conjunto de teste congelado possui 1.527 imagens. Os pesos do agregador e os parâmetros operacionais foram definidos com base na validação, sem utilizar o conjunto de teste para seleção. Essa separação reduz o risco de uma estimativa otimista causada pela reutilização do teste durante o desenvolvimento.

Para a tarefa binária, as classes `akiec`, `bcc` e `mel` foram agrupadas como malignas. As demais classes foram tratadas como benignas para a decisão binária. A classificação multiclasses foi preservada nos modelos para que o sistema também pudesse registrar a distribuição de probabilidade entre as sete categorias originais. Dessa maneira, a saída binária é utilizada para a decisão operacional, enquanto a saída multiclasses conserva informação mais detalhada sobre a representação aprendida.

### 5.3.2 Pré-processamento

As imagens são convertidas para o espaço RGB, redimensionadas conforme a configuração do experimento e submetidas à normalização utilizada pelos backbones pré-treinados. O treinamento utiliza transformações de aumento de dados, enquanto validação, teste e inferência utilizam transformações determinísticas. A configuração geral registra imagem de referência de 224 pixels, batch size 16 e frações de 15% para validação e teste. Os checkpoints efetivamente auditados registram configuração de inferência com imagem de 160 pixels e batch size 4, uma escolha associada ao custo computacional do ambiente utilizado.

O tratamento do desbalanceamento combina focal loss com pesos baseados na frequência efetiva das classes. O objetivo não é modificar artificialmente a distribuição do conjunto de teste, mas reduzir a influência excessiva da classe majoritária durante o treinamento. A decisão de preservar a distribuição original na avaliação é necessária para que as métricas representem o cenário definido pelo protocolo experimental.

### 5.3.3 Imagem de entrada e controle do domínio

A interface permite o envio de arquivos JPEG ou PNG com tamanho máximo de 10 MB. Depois do upload, o backend calcula características de qualidade e de domínio, incluindo resolução, proporção, nitidez, contraste, exposição, estatísticas de cor, luminância e força de bordas. Essas características são comparadas com uma referência construída a partir do HAM10000.

A triagem não é um classificador semântico universal. Ela funciona como uma barreira estatística para identificar entradas que se afastam do domínio dermatoscópico utilizado no desenvolvimento. Quando uma imagem é rejeitada, o sistema não executa os modelos de classificação e exibe os motivos da rejeição. A rejeição de uma imagem não dermatológica confirma o funcionamento do mecanismo de controle, mas não permite afirmar que todo carro, régua, rosto ou objeto externo será rejeitado.

![Tela inicial para envio de uma imagem dermatoscópica](https://private-us-east-1.manuscdn.com/sessionFile/c9497zT8i7HtpbpJ5Adedl/sandbox/w5WuaoJ8e7S5Qa95vhRADW-images_1789751118235_na1fn_L21udC9iMTA1ZDlmYy00MzMzLTRiMGMtODk1MC02NGFjZTNhYzY2YjUvU2tpbkNhbmNlclRlbnNvckZsb3ctR2l0L2RvY3MvY2hhcHRlci1zeXN0ZW0vc2NyZWVuc2hvdHMvMDFfdXBsb2FkX2luaXRpYWw.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvYzk0OTd6VDhpN0h0cGJwSjVBZGVkbC9zYW5kYm94L3c1V3Vhb0o4ZTdTNVFhOTV2aFJBRFctaW1hZ2VzXzE3ODk3NTExMTgyMzVfbmExZm5fTDIxdWRDOWlNVEExWkRsbVl5MDBNek16TFRSaU1HTXRPRGsxTUMwMk5HRmpaVE5oWXpZMllqVXZVMnRwYmtOaGJtTmxjbFJsYm5OdmNrWnNiM2N0UjJsMEwyUnZZM012WTJoaGNIUmxjaTF6ZVhOMFpXMHZjMk55WldWdWMyaHZkSE12TURGZmRYQnNiMkZrWDJsdWFYUnBZV3cucG5nIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzkyMDIyNDAwfX19XX0_&Key-Pair-Id=K2QY5QTL8JSY6C&Signature=MEQCIHQL5nJ5hhkV5jccLXA~wXMY8-zbr4DuMOlqxrA7cd~HAiAvlO0gHERB3xxYgtAd5JBWvdUx~PjQB7Jwt46ISo6y2Q__)

**Figura 5.1 – Tela inicial do sistema para seleção da imagem.**
*Fonte: autoria própria, a partir da implementação do SkinCancerCADDermoIA.*

A Figura 5.1 apresenta a tela inicial. O usuário é informado sobre os formatos aceitos e sobre o tamanho máximo do arquivo. Também são apresentadas orientações para utilizar uma imagem bem iluminada, centralizada e com foco adequado. A escolha de colocar essas orientações na própria interface é uma medida de prevenção de erro de entrada, pois a qualidade da imagem interfere tanto na triagem quanto na inferência.

## 5.4 Arquitetura geral da solução

A arquitetura do sistema foi organizada em duas trilhas que se complementam. A primeira é responsável pela classificação. A segunda é responsável pela explicabilidade visual. A trilha de classificação recebe a imagem elegível e executa os três checkpoints. A trilha de explicabilidade utiliza os mapas produzidos por cada modelo e um localizador auxiliar de lesão. O localizador não altera a classe, a probabilidade ou a confiança da classificação; ele é utilizado somente para restringir a área visualizada nos mapas.

![Diagrama de blocos da arquitetura implementada](https://private-us-east-1.manuscdn.com/sessionFile/c9497zT8i7HtpbpJ5Adedl/sandbox/w5WuaoJ8e7S5Qa95vhRADW-images_1789751118235_na1fn_L21udC9iMTA1ZDlmYy00MzMzLTRiMGMtODk1MC02NGFjZTNhYzY2YjUvU2tpbkNhbmNlclRlbnNvckZsb3ctR2l0L2RvY3MvY2hhcHRlci1zeXN0ZW0vZmlndXJhXzVfMV9hcnF1aXRldHVyYQ.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvYzk0OTd6VDhpN0h0cGJwSjVBZGVkbC9zYW5kYm94L3c1V3Vhb0o4ZTdTNVFhOTV2aFJBRFctaW1hZ2VzXzE3ODk3NTExMTgyMzVfbmExZm5fTDIxdWRDOWlNVEExWkRsbVl5MDBNek16TFRSaU1HTXRPRGsxTUMwMk5HRmpaVE5oWXpZMllqVXZVMnRwYmtOaGJtTmxjbFJsYm5OdmNrWnNiM2N0UjJsMEwyUnZZM012WTJoaGNIUmxjaTF6ZVhOMFpXMHZabWxuZFhKaFh6VmZNVjloY25GMWFYUmxkSFZ5WVEucG5nIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzkyMDIyNDAwfX19XX0_&Key-Pair-Id=K2QY5QTL8JSY6C&Signature=MEUCIDgtG6Lc0x~tzMwwTluuXRjwjyuvVaqRmOHwOfJhmphBAiEAno67IBmEHV-DZwKEHBf2UZBKORa3YzwtR7izY7aZ1WI_)

**Figura 5.2 – Diagrama de blocos do sistema implementado.**
*Fonte: autoria própria.*

O fluxo começa no upload da imagem e passa pela validação do arquivo. A entrada elegível segue para o pré-processamento e é encaminhada em paralelo para os três modelos. Cada modelo retorna uma classe multiclasses, uma probabilidade binária, uma confiança, o tempo de inferência e medidas de incerteza. O backend reúne essas saídas e apresenta a decisão agregada na interface.

Em paralelo, o sistema solicita os mapas de explicabilidade. O CNN produz Grad-CAM a partir do último mapa convolucional. O ViT produz atribuição de tokens baseada na relação entre a saída e o gradiente. O Hybrid combina informações do ramo convolucional, dos tokens e da atenção. O módulo de localização auxiliar fornece uma máscara que restringe as saliências ao espaço provável da lesão.

O fluxo completo de comunicação entre os componentes é apresentado na Figura 5.3.

![Diagrama de sequência da análise](https://private-us-east-1.manuscdn.com/sessionFile/c9497zT8i7HtpbpJ5Adedl/sandbox/w5WuaoJ8e7S5Qa95vhRADW-images_1789751118235_na1fn_L21udC9iMTA1ZDlmYy00MzMzLTRiMGMtODk1MC02NGFjZTNhYzY2YjUvU2tpbkNhbmNlclRlbnNvckZsb3ctR2l0L2RvY3MvY2hhcHRlci1zeXN0ZW0vZmlndXJhXzVfMl9zZXF1ZW5jaWE.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvYzk0OTd6VDhpN0h0cGJwSjVBZGVkbC9zYW5kYm94L3c1V3Vhb0o4ZTdTNVFhOTV2aFJBRFctaW1hZ2VzXzE3ODk3NTExMTgyMzVfbmExZm5fTDIxdWRDOWlNVEExWkRsbVl5MDBNek16TFRSaU1HTXRPRGsxTUMwMk5HRmpaVE5oWXpZMllqVXZVMnRwYmtOaGJtTmxjbFJsYm5OdmNrWnNiM2N0UjJsMEwyUnZZM012WTJoaGNIUmxjaTF6ZVhOMFpXMHZabWxuZFhKaFh6VmZNbDl6WlhGMVpXNWphV0UucG5nIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzkyMDIyNDAwfX19XX0_&Key-Pair-Id=K2QY5QTL8JSY6C&Signature=MEUCIBK5MF-rWt8VM2o0GdGBL-j51FgQ4E6SylHgV5OEbkA~AiEAv7-rA2EgG9a4n89tyFsoL0x3MXLoF6P1D-KbdjSY4hU_)

**Figura 5.3 – Sequência de comunicação entre usuário, interface, backend e módulos de aprendizado.**
*Fonte: autoria própria.*

## 5.5 Modelos de aprendizado profundo

**O núcleo de classificação foi organizado em três componentes treináveis com formas distintas de representar a imagem. A CNN prioriza padrões espaciais locais; o Vision Transformer modela relações entre regiões por autoatenção; e o modelo híbrido combina características convolucionais e tokens em uma representação compartilhada. A análise conjunta permite observar se as arquiteturas produzem decisões convergentes, mas não pressupõe que a maior complexidade resulte automaticamente em melhor desempenho. As subseções seguintes descrevem a função de cada componente e as informações devolvidas ao restante do sistema.**

### 5.5.1 CNN ResNet-50

O primeiro componente é uma rede convolucional baseada na ResNet-50 \cite{ref_31}. As convoluções são utilizadas para extrair padrões locais, como bordas, textura, contraste e estruturas de pequena escala. O backbone é carregado por meio da biblioteca `timm`, com pesos pré-treinados quando disponíveis, e recebe uma cabeça multitarefa desenvolvida no próprio projeto.

A cabeça multitarefa possui uma normalização de camada, dropout e duas saídas. A primeira saída contém os logits das sete classes do HAM10000. A segunda saída contém um logit para a tarefa binária benigno–maligno. A representação visual também é preservada para permitir a geração do Grad-CAM. O uso de uma saída auxiliar multiclasses permite que o treinamento não descarte completamente a informação fina das categorias originais.

A escolha da ResNet-50 é coerente com trabalhos que utilizam redes convolucionais como referência para a análise de lesões de pele, mas o papel do modelo neste projeto é experimental: ele funciona como uma linha de base e como um componente de uma análise combinada. O resultado não deve ser interpretado como evidência de superioridade clínica da arquitetura.

### 5.5.2 Vision Transformer

O segundo componente é um Vision Transformer pequeno \cite{ref_32} com patches de tamanho 16 por 16, identificado no código como `vit_small_patch16_224`.

Ao contrário da convolução, que constrói a representação por meio de campos receptivos locais, o mecanismo de autoatenção permite relacionar diferentes regiões da imagem. Essa característica é relevante para lesões cuja interpretação depende da distribuição global de cores, assimetria ou organização morfológica. A literatura recente apresenta os ViTs como uma alternativa para modelar contexto global, mas também destaca sua sensibilidade ao volume e à diversidade dos dados de treinamento \cite{ref_8, ref_25}.

No sistema desenvolvido, os tokens são preservados durante a inferência para possibilitar a atribuição visual. Assim, o ViT não é utilizado somente para retornar uma classe. A interface pode apresentar sua confiança, sua entropia, sua variância de Test-Time Augmentation e seu mapa de atribuição.

### 5.5.3 Modelo híbrido CNN–ViT

O terceiro componente combina um backbone convolucional com uma sequência de tokens e dois blocos de atenção multi-head. O mapa de características produzido pela ResNet-50 é projetado para uma dimensão de embedding de 192. Em seguida, são adicionados um token de classificação e embeddings posicionais. Os tokens passam por blocos de atenção e são normalizados antes da combinação final.

A representação híbrida utiliza duas projeções. A primeira representa o conteúdo extraído pela CNN. A segunda representa o token global produzido pelo ramo de atenção. Um gate aprendido calcula a contribuição relativa dessas duas representações e forma a representação utilizada pela cabeça multitarefa. Essa implementação não corresponde a uma simples concatenação: há uma combinação adaptativa entre informação convolucional e informação baseada em atenção.

O desenho híbrido foi motivado pela discussão apresentada no Capítulo 4. Trabalhos recentes exploram a combinação de CNNs e Transformers para equilibrar a extração de padrões locais com a modelagem de contexto global \cite{ref_4, ref_5, ref_12}. No entanto, a existência de uma arquitetura híbrida no sistema não implica, por si só, que ela seja superior. A comparação deve considerar métricas, calibração, custo computacional e comportamento fora do domínio.

### 5.5.4 Saídas dos modelos

Cada modelo retorna quatro grupos de informações. O primeiro grupo corresponde às probabilidades das sete classes. O segundo corresponde à probabilidade binária de malignidade. O terceiro registra o tempo de inferência. O quarto reúne as medidas de incerteza produzidas com Test-Time Augmentation.

Na inferência com TTA, a imagem original é avaliada juntamente com versões espelhadas. As probabilidades das versões são agregadas por média. A entropia preditiva é calculada sobre a distribuição multiclasses, enquanto a variância é calculada sobre as probabilidades binárias das diferentes versões. Quando esses valores ultrapassam os limiares operacionais, o modelo recomenda abstenção.

A abstenção é apresentada como uma recomendação de revisão, e não como um diagnóstico. Ela significa que a entrada ou a decisão não deve ser tratada como suficientemente estável segundo os critérios definidos para o protótipo.

## 5.6 Agregação das saídas na aplicação

O sistema preserva os resultados individuais e também produz uma saída agregada. Na implementação auditada, as probabilidades produzidas pelos modelos são combinadas com os pesos registrados no artefato do experimento: 0,10 para a CNN, 0,55 para o ViT e 0,35 para o Hybrid. Esses valores foram selecionados utilizando a validação e somam 1,0 após a normalização.

A operação de agregação utilizada pelo backend pode ser descrita por:

$$
 p_{agregado} = 0{,}10p_{CNN} + 0{,}55p_{ViT} + 0{,}35p_{Hybrid}.
$$

A probabilidade agregada é convertida em uma decisão binária com limiar de 0,5. O sistema também combina as distribuições multiclasses e calcula a média das medidas de incerteza. O resultado da aplicação, portanto, não oculta os modelos individuais: a decisão final é apresentada junto com as decisões da CNN, do ViT e do Hybrid.

Esta seção descreve somente a implementação do agregador. A fundamentação conceitual sobre Ensemble Learning permanece no Capítulo 3 e nas referências já utilizadas na dissertação \cite{ref_13, ref_19, ref_24}. Não foi criado neste capítulo um novo desenvolvimento teórico sobre o tema.

![Cartões com as saídas individuais e a saída agregada](https://private-us-east-1.manuscdn.com/sessionFile/c9497zT8i7HtpbpJ5Adedl/sandbox/w5WuaoJ8e7S5Qa95vhRADW-images_1789751118235_na1fn_L21udC9iMTA1ZDlmYy00MzMzLTRiMGMtODk1MC02NGFjZTNhYzY2YjUvU2tpbkNhbmNlclRlbnNvckZsb3ctR2l0L2RvY3MvY2hhcHRlci1zeXN0ZW0vc2NyZWVuc2hvdHMvMDVfbW9kZWxfY2FyZHM.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvYzk0OTd6VDhpN0h0cGJwSjVBZGVkbC9zYW5kYm94L3c1V3Vhb0o4ZTdTNVFhOTV2aFJBRFctaW1hZ2VzXzE3ODk3NTExMTgyMzVfbmExZm5fTDIxdWRDOWlNVEExWkRsbVl5MDBNek16TFRSaU1HTXRPRGsxTUMwMk5HRmpaVE5oWXpZMllqVXZVMnRwYmtOaGJtTmxjbFJsYm5OdmNrWnNiM2N0UjJsMEwyUnZZM012WTJoaGNIUmxjaTF6ZVhOMFpXMHZjMk55WldWdWMyaHZkSE12TURWZmJXOWtaV3hmWTJGeVpITS5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTIwMjI0MDB9fX1dfQ__&Key-Pair-Id=K2QY5QTL8JSY6C&Signature=MEUCIQD8xR918bwbiCpbmkcA0CslqsbRDPXsku1WaojGQWaKvAIgI9jvbTiq0THMij7SdDU~cH8QqxMSV-dMX9HSmBkw2ZU_)

**Figura 5.4 – Visualização dos resultados individuais dos modelos e da saída agregada.**
*Fonte: autoria própria, a partir da execução local.*

A Figura 5.4 mostra a função de inspeção criada para a ferramenta. O usuário consegue comparar as saídas dos modelos, observar a confiança e consultar a entropia e a variância TTA. Essa disposição é importante para identificar situações de discordância entre arquiteturas. Por exemplo, uma decisão agregada pode permanecer liberada quando somente um componente recomenda abstenção, conforme a regra operacional configurada. Esse comportamento deve ser interpretado como uma política ajustável do protótipo.

## 5.7 Implementação da explicabilidade

**A explicabilidade foi incorporada para tornar visíveis as regiões associadas à saída de cada arquitetura. Como CNNs, Transformers e modelos híbridos armazenam representações internas diferentes, não foi aplicado um único procedimento indistintamente a todos os componentes. O sistema gera métodos compatíveis com cada modelo e converte as atribuições em sobreposições alinhadas à geometria original da imagem. Os mapas resultantes apoiam a inspeção técnica da inferência, mas permanecem aproximações matemáticas e não devem ser confundidos com justificativas clínicas ou relações causais.**

### 5.7.1 Grad-CAM para a CNN

O mapa da CNN é gerado a partir do último mapa convolucional. O gradiente da saída binária é utilizado para estimar quais canais contribuíram para a decisão. A combinação ponderada dos mapas de características produz uma saliência espacial que é redimensionada para o tamanho da imagem original.

O Grad-CAM \cite{ref_33} é uma explicação aproximada da sensibilidade do modelo. Ele não é uma segmentação da lesão, não mostra causalidade e não prova que a região destacada seja suficiente para justificar a decisão. Essa limitação deve permanecer explícita no texto e na interface, uma vez que a interpretação visual de um mapa pode ser mais forte do que a evidência fornecida pelo método \cite{ref_12, ref_18}.

### 5.7.2 Atribuição de tokens no ViT

No ViT, os tokens são relacionados ao gradiente da saída selecionada. O token de classificação é utilizado para obter uma atribuição espacial sobre os patches da imagem. Quando a distribuição produzida pelo gradiente é praticamente uniforme, o sistema utiliza o gradiente da entrada como fallback de visualização. Esse fallback evita que a interface apresente uma imagem completamente vazia, mas não transforma o método em uma explicação causal.

### 5.7.3 Mapa do modelo híbrido

O mapa do Hybrid combina três sinais disponíveis na arquitetura: o Grad-CAM do ramo convolucional, a atribuição dos tokens e o rollout de atenção. A combinação é normalizada antes da geração do overlay. O objetivo é permitir a inspeção das regiões que recebem contribuição de mais de uma representação, sem afirmar que o mapa representa exatamente a lógica interna do modelo.

### 5.7.4 Localizador auxiliar e gate visual

Para reduzir a coloração de regiões do fundo, foi treinado um localizador auxiliar com o ISIC 2016 Part 1 \cite{ref_37}. O conjunto possui imagens dermatoscópicas e máscaras binárias de lesão. O experimento registrado utilizou seed 42, divisão 720/90/90 e resolução de 160 × 160. No teste do próprio ISIC 2016, o localizador obteve Dice de 0,8245 e IoU de 0,7667.

A máscara é binarizada, submetida à seleção do maior componente conectado e processada por fechamento morfológico. Na configuração padrão, o gate utiliza o modo `balanced`, limiar 0,50 e kernel 5 × 5. O modo `strict` usa limiar 0,65 e kernel 3 × 3. O modo `permissive` utiliza limiar 0,35 e kernel 7 × 7, sendo indicado para situações com pelos ou iluminação irregular. Esses modos alteram a máscara de visualização, não a classificação.

O uso de uma base de segmentação separada é uma decisão de engenharia e também uma limitação metodológica. O desempenho do localizador no ISIC 2016 não garante o mesmo comportamento no HAM10000, porque os datasets podem diferir em equipamento, iluminação, composição e distribuição de lesões. Trabalhos de segmentação de lesões mostram a importância de avaliar a máscara em dados representativos do domínio de aplicação \cite{ref_1, ref_2}.

A aplicação do gate pode ser representada por:

$$
 S_{gate}(x,y) = S(x,y) \times M(x,y),
$$

em que $$S(x,y)$$ é a saliência normalizada e $$M(x,y)$$ é a máscara binária produzida pelo localizador. Fora da máscara, a saliência é zerada. A opacidade do overlay é proporcional à intensidade da saliência. Assim, regiões sem saliência permanecem visualmente próximas da imagem original, em vez de receberem uma coloração uniforme.

![Grade com os quatro mapas de explicabilidade](https://private-us-east-1.manuscdn.com/sessionFile/c9497zT8i7HtpbpJ5Adedl/sandbox/w5WuaoJ8e7S5Qa95vhRADW-images_1789751118235_na1fn_L21udC9iMTA1ZDlmYy00MzMzLTRiMGMtODk1MC02NGFjZTNhYzY2YjUvU2tpbkNhbmNlclRlbnNvckZsb3ctR2l0L2RvY3MvY2hhcHRlci1zeXN0ZW0vc2NyZWVuc2hvdHMvMDZfeGFpX2hlYXRtYXBzX2dyaWQ.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvYzk0OTd6VDhpN0h0cGJwSjVBZGVkbC9zYW5kYm94L3c1V3Vhb0o4ZTdTNVFhOTV2aFJBRFctaW1hZ2VzXzE3ODk3NTExMTgyMzVfbmExZm5fTDIxdWRDOWlNVEExWkRsbVl5MDBNek16TFRSaU1HTXRPRGsxTUMwMk5HRmpaVE5oWXpZMllqVXZVMnRwYmtOaGJtTmxjbFJsYm5OdmNrWnNiM2N0UjJsMEwyUnZZM012WTJoaGNIUmxjaTF6ZVhOMFpXMHZjMk55WldWdWMyaHZkSE12TURaZmVHRnBYMmhsWVhSdFlYQnpYMmR5YVdRLnBuZyIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5MjAyMjQwMH19fV19&Key-Pair-Id=K2QY5QTL8JSY6C&Signature=MEYCIQDdxPdlsfdy~TdfxQpGiqycn1OLzVWriRey7B~0oCAJjgIhANhLkUr2GNuhuDQl6synSiPSdo4tvB4C0TKi5si7Ez7G)

**Figura 5.5 – Mapas de explicabilidade produzidos para a imagem auditada.**
*Fonte: autoria própria, a partir dos checkpoints treinados e do gate auxiliar.*

A Figura 5.5 mostra os quatro mapas disponíveis na interface. A CNN utiliza Grad-CAM, o ViT utiliza atribuição de tokens, o Hybrid apresenta um mapa combinado e a saída agregada apresenta a composição das saliências. A auditoria quantitativa verificou que os quatro arquivos possuem 600 × 450 pixels e que a diferença máxima de pixels fora da saliência foi igual a zero na execução analisada. Esse resultado confirma a correção da transparência espacial implementada; não confirma, sozinho, a fidelidade clínica dos mapas.

## 5.8 Implementação da aplicação web

**A aplicação web foi desenvolvida para transformar os módulos científicos em um fluxo de uso observável e reproduzível. A interface não executa diretamente os modelos; ela coleta a imagem, apresenta o estado da análise e organiza os resultados recebidos do backend. O servidor, por sua vez, valida as requisições, controla os arquivos, aciona os processos Python e converte as respostas em contratos tipados. Essa separação preserva a independência entre a camada de apresentação e o pipeline de aprendizado profundo, permitindo testar cada parte isoladamente.**

### 5.8.1 Interface do usuário

A interface foi implementada com React 19 e TypeScript. O Vite é utilizado no desenvolvimento e no empacotamento do frontend. A navegação é organizada em quatro abas: Upload, Resultados, Histórico e Métricas. O estado da imagem selecionada, da prévia, do progresso e da classificação é controlado na página principal de diagnóstico.

A utilização de TypeScript permite declarar os contratos das respostas, reduzindo o risco de a interface interpretar de forma incorreta os campos retornados pelo backend. Os componentes visuais foram construídos com Tailwind CSS, Radix UI e ícones do Lucide React. O Recharts foi utilizado na aba de métricas para representar graficamente os desempenhos dos modelos.

Depois que o arquivo é selecionado, a interface exibe uma prévia e os metadados básicos. Durante a análise, a barra de progresso comunica as etapas aproximadas do processamento: preparação, envio, triagem, execução dos modelos e geração dos mapas. A barra é uma indicação de estado da interface, não uma medição direta do tempo gasto em cada etapa do backend.

![Pré-visualização da imagem selecionada](https://private-us-east-1.manuscdn.com/sessionFile/c9497zT8i7HtpbpJ5Adedl/sandbox/w5WuaoJ8e7S5Qa95vhRADW-images_1789751118235_na1fn_L21udC9iMTA1ZDlmYy00MzMzLTRiMGMtODk1MC02NGFjZTNhYzY2YjUvU2tpbkNhbmNlclRlbnNvckZsb3ctR2l0L2RvY3MvY2hhcHRlci1zeXN0ZW0vc2NyZWVuc2hvdHMvMDJfdXBsb2FkX3ByZXZpZXdfaGFtMTAwMDA.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvYzk0OTd6VDhpN0h0cGJwSjVBZGVkbC9zYW5kYm94L3c1V3Vhb0o4ZTdTNVFhOTV2aFJBRFctaW1hZ2VzXzE3ODk3NTExMTgyMzVfbmExZm5fTDIxdWRDOWlNVEExWkRsbVl5MDBNek16TFRSaU1HTXRPRGsxTUMwMk5HRmpaVE5oWXpZMllqVXZVMnRwYmtOaGJtTmxjbFJsYm5OdmNrWnNiM2N0UjJsMEwyUnZZM012WTJoaGNIUmxjaTF6ZVhOMFpXMHZjMk55WldWdWMyaHZkSE12TURKZmRYQnNiMkZrWDNCeVpYWnBaWGRmYUdGdE1UQXdNREEucG5nIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzkyMDIyNDAwfX19XX0_&Key-Pair-Id=K2QY5QTL8JSY6C&Signature=MEYCIQCpm1xdV~iV~tCmnstyAHweOuGvKZyAdr30Cgj1dDxJTQIhAMJGd84LJEVviCo7lXnXJR4goQSVTSjPD1viFNUItOVx)

**Figura 5.6 – Pré-visualização de uma imagem dermatoscópica antes da classificação.**
*Fonte: autoria própria.*

A Figura 5.6 apresenta a pré-visualização da imagem `ISIC_0027419.jpg`. O arquivo é exibido antes do envio da solicitação de classificação, permitindo que o usuário confirme a seleção. Essa etapa também reduz a possibilidade de executar o processamento em um arquivo diferente daquele que se pretendia analisar.

### 5.8.2 Backend e contratos de comunicação

O backend foi desenvolvido com Express e tRPC. As rotas tRPC organizam as operações de upload, classificação, histórico e métricas. O Zod é utilizado para validar os dados recebidos pelas rotas. Depois do upload, o servidor armazena o arquivo em um caminho controlado e retorna um identificador interno. A classificação utiliza esse identificador para localizar a imagem, evitando que o caminho físico seja fornecido diretamente pelo usuário.

O backend chama os módulos Python por processos controlados. A ponte define o caminho do interpretador, o diretório raiz do projeto, o checkpoint do modelo, o arquivo de entrada e o tempo limite da operação. A resposta Python é interpretada como JSON e convertida para o contrato TypeScript utilizado pela interface.

Esse desenho separa as responsabilidades. O Python concentra o carregamento dos checkpoints, o pré-processamento, a inferência e a geração dos mapas. O TypeScript concentra a orquestração das chamadas, a validação das entradas, o armazenamento dos resultados e a apresentação no navegador. A separação também permite testar os módulos científicos sem depender da interface.

### 5.8.3 Histórico e métricas

A aba de histórico consulta os diagnósticos registrados para a sessão. Em ambiente com banco de dados, os registros podem ser persistidos com Drizzle ORM e MariaDB/MySQL. Na configuração local utilizada para a demonstração, foi implementado um fallback em memória para permitir a execução sem senha e sem banco ativo. Esse fallback atende à apresentação em uma única sessão, mas perde os registros quando o servidor é reiniciado.

A aba de métricas carrega os arquivos do experimento HAM10000 e apresenta os resultados dos quatro componentes: CNN, ViT, Hybrid e saída agregada. Cada modelo é associado ao conjunto de teste congelado com 1.527 imagens. A interface apresenta acurácia, sensibilidade, especificidade, F1-score, AUROC e precisão, além de um gráfico de barras para a comparação visual.

![Painel de métricas do experimento](https://private-us-east-1.manuscdn.com/sessionFile/c9497zT8i7HtpbpJ5Adedl/sandbox/DF71v8HOoj3dRYNZcz9Zct-images_1789987897191_na1fn_L21udC9iMTA1ZDlmYy00MzMzLTRiMGMtODk1MC02NGFjZTNhYzY2YjUvU2tpbkNhbmNlclRlbnNvckZsb3ctR2l0L2RvY3MvY2hhcHRlci1zeXN0ZW0vc2NyZWVuc2hvdHMvMDhfbWV0cmljc19kYXNoYm9hcmQ.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvYzk0OTd6VDhpN0h0cGJwSjVBZGVkbC9zYW5kYm94L0RGNzF2OEhPb2ozZFJZTlpjejlaY3QtaW1hZ2VzXzE3ODk5ODc4OTcxOTFfbmExZm5fTDIxdWRDOWlNVEExWkRsbVl5MDBNek16TFRSaU1HTXRPRGsxTUMwMk5HRmpaVE5oWXpZMllqVXZVMnRwYmtOaGJtTmxjbFJsYm5OdmNrWnNiM2N0UjJsMEwyUnZZM012WTJoaGNIUmxjaTF6ZVhOMFpXMHZjMk55WldWdWMyaHZkSE12TURoZmJXVjBjbWxqYzE5a1lYTm9ZbTloY21RLnBuZyIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5MjAyMjQwMH19fV19&Key-Pair-Id=K2QY5QTL8JSY6C&Signature=MEUCIEg617M9LIQoXETRKjQ3~GCQH4UO8wAad5EgzQ1g8ZTBAiEAqPCTGmAmR-lcUAPk7Mk4Oz8MPAGNtJWuFbFiwhczn38_)

**Figura 5.7 – Tabela e gráfico de métricas carregados a partir dos artefatos do experimento.**
*Fonte: autoria própria.*

A Figura 5.7 mostra que a ferramenta não depende de números digitados manualmente na interface. Os valores são carregados dos artefatos registrados pelo pipeline. No teste binário, a saída agregada apresentou acurácia de 0,7498, sensibilidade de 0,8233, especificidade de 0,7319, AUROC de 0,8600, AUPRC de 0,5709 e ECE de 0,0706. Esses valores são resultados de avaliação interna no HAM10000 e não devem ser apresentados como validação clínica.

### 5.8.4 Execução do fluxo completo

A execução completa começa quando o usuário seleciona a imagem. A interface valida o tipo e o tamanho do arquivo. O backend grava o arquivo e inicia a triagem. Se a imagem for elegível, os três modelos são executados e as respostas são agregadas. Em seguida, são gerados os mapas individuais e o mapa agregado. O resultado é registrado na sessão e a interface muda para a aba de resultados.

![Estado intermediário de processamento](https://private-us-east-1.manuscdn.com/sessionFile/c9497zT8i7HtpbpJ5Adedl/sandbox/w5WuaoJ8e7S5Qa95vhRADW-images_1789751118235_na1fn_L21udC9iMTA1ZDlmYy00MzMzLTRiMGMtODk1MC02NGFjZTNhYzY2YjUvU2tpbkNhbmNlclRlbnNvckZsb3ctR2l0L2RvY3MvY2hhcHRlci1zeXN0ZW0vc2NyZWVuc2hvdHMvMDNfcHJvY2Vzc2luZ19waXBlbGluZQ.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvYzk0OTd6VDhpN0h0cGJwSjVBZGVkbC9zYW5kYm94L3c1V3Vhb0o4ZTdTNVFhOTV2aFJBRFctaW1hZ2VzXzE3ODk3NTExMTgyMzVfbmExZm5fTDIxdWRDOWlNVEExWkRsbVl5MDBNek16TFRSaU1HTXRPRGsxTUMwMk5HRmpaVE5oWXpZMllqVXZVMnRwYmtOaGJtTmxjbFJsYm5OdmNrWnNiM2N0UjJsMEwyUnZZM012WTJoaGNIUmxjaTF6ZVhOMFpXMHZjMk55WldWdWMyaHZkSE12TUROZmNISnZZMlZ6YzJsdVoxOXdhWEJsYkdsdVpRLnBuZyIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5MjAyMjQwMH19fV19&Key-Pair-Id=K2QY5QTL8JSY6C&Signature=MEUCIQDs3G0sNemXK-w0HFx2phCfv1cNLchYqVDnHm4dI2gLkwIgXovh-5WbrJOFZqX6VIpDiIE23kvYpe65iElYRYbbT6w_)

**Figura 5.8 – Estado da interface durante a triagem, inferência e geração dos mapas.**
*Fonte: autoria própria.*

A Figura 5.8 registra a interface durante o processamento. Nessa etapa, o usuário recebe uma indicação de que a imagem está sendo enviada e analisada. A execução auditada da ferramenta levou aproximadamente 25 segundos no ambiente de teste, sendo cerca de 13 segundos para a classificação e 12 segundos para os mapas. O tempo depende do hardware, do interpretador Python e da carga dos três checkpoints.

## 5.9 Testes funcionais realizados na ferramenta

**Os testes funcionais foram planejados para verificar a integração entre entrada, triagem, classificação, explicabilidade e apresentação dos resultados. Eles não substituem a avaliação estatística no conjunto de teste nem constituem validação clínica. Seu objetivo é demonstrar que os componentes conseguem percorrer o fluxo previsto e que falhas ou rejeições são comunicadas ao usuário. Para isso, foram examinados um caso dermatoscópico aceito, as saídas individuais dos modelos, o registro no histórico e uma imagem fora do domínio.**

### 5.9.1 Imagem dermatoscópica elegível

A primeira execução foi realizada com a imagem `ISIC_0027419.jpg`, utilizada como exemplo dermatoscópico. A imagem foi aceita pela triagem, encaminhada aos três modelos e processada pelo módulo XAI. O resultado agregado retornou a classe binária `malignant` com confiança de 85,82%. A entropia preditiva foi 0,7329 e a variância TTA foi 0,001667. Com os limiares operacionais utilizados, o resultado agregado não recomendou abstenção.

O resultado não deve ser lido como confirmação de câncer. A classe retornada é a saída de um modelo treinado em um conjunto de imagens, e a confiança é uma probabilidade operacional do sistema. A confirmação diagnóstica depende de avaliação clínica e, quando indicada, de procedimentos complementares.

![Resultado completo da classificação](https://private-us-east-1.manuscdn.com/sessionFile/c9497zT8i7HtpbpJ5Adedl/sandbox/w5WuaoJ8e7S5Qa95vhRADW-images_1789751118235_na1fn_L21udC9iMTA1ZDlmYy00MzMzLTRiMGMtODk1MC02NGFjZTNhYzY2YjUvU2tpbkNhbmNlclRlbnNvckZsb3ctR2l0L2RvY3MvY2hhcHRlci1zeXN0ZW0vc2NyZWVuc2hvdHMvMDRfcmVzdWx0X2Z1bGw.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvYzk0OTd6VDhpN0h0cGJwSjVBZGVkbC9zYW5kYm94L3c1V3Vhb0o4ZTdTNVFhOTV2aFJBRFctaW1hZ2VzXzE3ODk3NTExMTgyMzVfbmExZm5fTDIxdWRDOWlNVEExWkRsbVl5MDBNek16TFRSaU1HTXRPRGsxTUMwMk5HRmpaVE5oWXpZMllqVXZVMnRwYmtOaGJtTmxjbFJsYm5OdmNrWnNiM2N0UjJsMEwyUnZZM012WTJoaGNIUmxjaTF6ZVhOMFpXMHZjMk55WldWdWMyaHZkSE12TURSZmNtVnpkV3gwWDJaMWJHdy5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTIwMjI0MDB9fX1dfQ__&Key-Pair-Id=K2QY5QTL8JSY6C&Signature=MEQCID2SdLexcpDWccKnb786n6rhNewpAq1fof30P1RAlNkJAiAGS529c-~oZVq~NCTB8islxjD2-nkOORpF6k6qWQoBTA__)

**Figura 5.9 – Resultado completo com imagem, elegibilidade, decisão, confiança e incerteza.**
*Fonte: autoria própria.*

### 5.9.2 Visualização dos modelos

A Figura 5.4 permite observar as quatro saídas do sistema lado a lado. A visualização foi criada para que a ferramenta não esconda a divergência entre os modelos. Essa escolha é importante porque uma saída agregada pode parecer estável mesmo quando os modelos individuais apresentam comportamentos diferentes.

No conjunto de teste, o Ensemble apresentou o maior AUROC entre as saídas avaliadas, mas o resultado deve ser interpretado em conjunto com a especificidade, a sensibilidade, o ECE e a AUPRC. O Hybrid apresentou ECE de 0,2269, valor que indica pior calibração entre os componentes comparados. A inclusão da calibração e da incerteza no sistema procura evitar que uma única porcentagem de confiança seja interpretada como certeza.

### 5.9.3 Histórico da sessão

Depois da classificação, o diagnóstico é inserido no histórico da sessão. A interface apresenta o nome do arquivo, a data, a classe final, a confiança e a versão do modelo. Ao selecionar os detalhes, o usuário pode consultar as saídas da CNN, do ViT e do Hybrid.

![Histórico de diagnósticos da sessão](https://private-us-east-1.manuscdn.com/sessionFile/c9497zT8i7HtpbpJ5Adedl/sandbox/w5WuaoJ8e7S5Qa95vhRADW-images_1789751118235_na1fn_L21udC9iMTA1ZDlmYy00MzMzLTRiMGMtODk1MC02NGFjZTNhYzY2YjUvU2tpbkNhbmNlclRlbnNvckZsb3ctR2l0L2RvY3MvY2hhcHRlci1zeXN0ZW0vc2NyZWVuc2hvdHMvMDdfaGlzdG9yeQ.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvYzk0OTd6VDhpN0h0cGJwSjVBZGVkbC9zYW5kYm94L3c1V3Vhb0o4ZTdTNVFhOTV2aFJBRFctaW1hZ2VzXzE3ODk3NTExMTgyMzVfbmExZm5fTDIxdWRDOWlNVEExWkRsbVl5MDBNek16TFRSaU1HTXRPRGsxTUMwMk5HRmpaVE5oWXpZMllqVXZVMnRwYmtOaGJtTmxjbFJsYm5OdmNrWnNiM2N0UjJsMEwyUnZZM012WTJoaGNIUmxjaTF6ZVhOMFpXMHZjMk55WldWdWMyaHZkSE12TURkZmFHbHpkRzl5ZVEucG5nIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzkyMDIyNDAwfX19XX0_&Key-Pair-Id=K2QY5QTL8JSY6C&Signature=MEYCIQDFCL8t7i6B-EdvQYXiYliSoSzRLizpSoX7382MPuOR8AIhAJQUpuTX-O-aEHRSLvPQ3dzaAEdDdcMKws4TlV-rZd9C)

**Figura 5.10 – Histórico local após a execução de uma classificação.**
*Fonte: autoria própria.*

A Figura 5.10 demonstra que a ferramenta mantém uma trilha mínima da execução. Na configuração sem MariaDB, essa trilha é temporária. Essa limitação deve ser registrada na dissertação, pois o histórico local não possui a mesma persistência de um sistema conectado a um banco de dados.

### 5.9.4 Imagem fora do domínio

Como teste de controle, foi utilizada uma imagem não dermatológica. A triagem retornou o motivo `outside_dermoscopy_domain` e impediu que a imagem fosse encaminhada aos modelos. Esse caso verifica a integração entre a referência estatística e o fluxo da aplicação.

![Rejeição de imagem fora do domínio](https://private-us-east-1.manuscdn.com/sessionFile/c9497zT8i7HtpbpJ5Adedl/sandbox/w5WuaoJ8e7S5Qa95vhRADW-images_1789751118235_na1fn_L21udC9iMTA1ZDlmYy00MzMzLTRiMGMtODk1MC02NGFjZTNhYzY2YjUvU2tpbkNhbmNlclRlbnNvckZsb3ctR2l0L2RvY3MvY2hhcHRlci1zeXN0ZW0vc2NyZWVuc2hvdHMvMDlfb29kX3JlamVjdGlvbg.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvYzk0OTd6VDhpN0h0cGJwSjVBZGVkbC9zYW5kYm94L3c1V3Vhb0o4ZTdTNVFhOTV2aFJBRFctaW1hZ2VzXzE3ODk3NTExMTgyMzVfbmExZm5fTDIxdWRDOWlNVEExWkRsbVl5MDBNek16TFRSaU1HTXRPRGsxTUMwMk5HRmpaVE5oWXpZMllqVXZVMnRwYmtOaGJtTmxjbFJsYm5OdmNrWnNiM2N0UjJsMEwyUnZZM012WTJoaGNIUmxjaTF6ZVhOMFpXMHZjMk55WldWdWMyaHZkSE12TURsZmIyOWtYM0psYW1WamRHbHZiZy5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTIwMjI0MDB9fX1dfQ__&Key-Pair-Id=K2QY5QTL8JSY6C&Signature=MEUCIQDQ2qtAQZJxYYFY2tevmu6OvoS9agS-ssEspnhkemHFjQIgPBRINzLl2-R4qHiHGcbwUNzOrvuIgdw5oP4kqkkIVKo_)

**Figura 5.11 – Rejeição de uma entrada não dermatológica antes da classificação.**
*Fonte: autoria própria.*

A Figura 5.11 mostra que a rejeição não ocorre de forma silenciosa. A interface apresenta o status, o escore de qualidade, o escore OOD, a dimensão da imagem e os motivos identificados. O sistema, portanto, fornece uma justificativa operacional para não executar o classificador. O teste, porém, não mede a sensibilidade e a especificidade de um detector OOD universal. Para essa conclusão seria necessário um painel amplo, independente e rotulado com diferentes objetos, fotografias clínicas, imagens degradadas e imagens dermatoscópicas de outros equipamentos.

![Painel quadruplicado dos testes da ferramenta](https://private-us-east-1.manuscdn.com/sessionFile/c9497zT8i7HtpbpJ5Adedl/sandbox/w5WuaoJ8e7S5Qa95vhRADW-images_1789751118235_na1fn_L21udC9iMTA1ZDlmYy00MzMzLTRiMGMtODk1MC02NGFjZTNhYzY2YjUvU2tpbkNhbmNlclRlbnNvckZsb3ctR2l0L2RvY3MvY2hhcHRlci1zeXN0ZW0vcGFpbmVsX3Rlc3Rlc19zaXN0ZW1h.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvYzk0OTd6VDhpN0h0cGJwSjVBZGVkbC9zYW5kYm94L3c1V3Vhb0o4ZTdTNVFhOTV2aFJBRFctaW1hZ2VzXzE3ODk3NTExMTgyMzVfbmExZm5fTDIxdWRDOWlNVEExWkRsbVl5MDBNek16TFRSaU1HTXRPRGsxTUMwMk5HRmpaVE5oWXpZMllqVXZVMnRwYmtOaGJtTmxjbFJsYm5OdmNrWnNiM2N0UjJsMEwyUnZZM012WTJoaGNIUmxjaTF6ZVhOMFpXMHZjR0ZwYm1Wc1gzUmxjM1JsYzE5emFYTjBaVzFoLnBuZyIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5MjAyMjQwMH19fV19&Key-Pair-Id=K2QY5QTL8JSY6C&Signature=MEQCIDBjcoFpeTFf~PtkJYG4Dan-xRgeqPS~b6qrw3MpLzETAiAzNDpcDn-OQNdTnDw8Tt-g9Xpe4Fi11mYRbQM3IMqBiA__)

**Figura 5.12 – Painel com quatro estados da aplicação: upload, resultado, métricas e rejeição fora do domínio.**
*Fonte: autoria própria, a partir das execuções locais.*

O painel da Figura 5.12 reúne, em uma única composição, quatro momentos do uso da ferramenta. No primeiro quadrante, a imagem é selecionada e exibida antes da inferência. No segundo, são apresentados a elegibilidade, o resultado agregado, a incerteza, os modelos individuais e os mapas. No terceiro, são mostradas as métricas carregadas dos artefatos do experimento. No quarto, uma entrada não dermatológica é interrompida pela triagem. A composição foi incluída para evidenciar que o sistema não é apenas um classificador isolado: ele possui etapas de entrada, controle, análise e comunicação do resultado.

## 5.10 Ferramentas de desenvolvimento e suas funções

A implementação utilizou ferramentas de software com funções distintas. As ferramentas de aprendizado profundo foram utilizadas para construir, treinar, carregar e executar os modelos. As ferramentas de visão computacional foram utilizadas para ler imagens, processar máscaras e produzir overlays. As ferramentas web organizaram a interface e a comunicação com o backend. As ferramentas de engenharia foram utilizadas para testar, empacotar e versionar o sistema.

| Camada | Ferramentas utilizadas | Função no projeto |
| --- | --- | --- |
| Linguagem científica | Python 3.11 | Treinamento, inferência, métricas e explicabilidade |
| Aprendizado profundo | PyTorch, torchvision e timm | Modelos, tensores, backbones e checkpoints |
| Dados e métricas | NumPy, pandas e scikit-learn | Manipulação, partições e avaliação |
| Imagens | Pillow e OpenCV | Leitura, redimensionamento, morfologia e composição visual |
| Visualização | Matplotlib | Colormaps e figuras experimentais |
| Interface | React, TypeScript e Vite | Aplicação web e gerenciamento de estado |
| Backend | Express, tRPC e Zod | Rotas, contratos e validação |
| Componentes visuais | Tailwind CSS, Radix UI e Lucide React | Layout, componentes e ícones |
| Gráficos | Recharts | Tabelas e gráficos da aba de métricas |
| Persistência | Drizzle ORM e MariaDB/MySQL | Persistência opcional dos registros |
| Testes | Vitest e pytest | Verificação do frontend, backend e módulos Python |
| Engenharia | Git, GitHub, pnpm e VS Code | Versionamento, dependências e desenvolvimento |

As bibliotecas utilizadas são ferramentas de implementação e não constituem, por si só, resultados científicos do trabalho. Por essa razão, os métodos, arquiteturas e conjuntos de dados são citados no ponto em que são empregados, enquanto as dependências de software são registradas como parte do ambiente computacional. Essa distinção evita atribuir às bibliotecas resultados que pertencem ao protocolo experimental desenvolvido nesta pesquisa.

### 5.10.1 Proveniência do código e atribuição das ferramentas

**A implementação foi construída como uma composição de componentes próprios e dependências de código aberto. A auditoria do repositório não identificou arquivos ou trechos explicitamente marcados como copiados de um projeto de terceiros. Essa constatação não elimina a obrigação de revisar as licenças das dependências antes de uma distribuição pública; ela apenas delimita o que foi desenvolvido no escopo deste trabalho e o que foi utilizado como infraestrutura.**

**A principal reutilização de software ocorre na camada dos backbones. A biblioteca `timm` fornece implementações de modelos de visão, incluindo variantes da ResNet e do Vision Transformer, além de utilitários para carregamento de pesos. O sistema não reimplementa essas arquiteturas fundamentais a partir de operações elementares; ele instancia os backbones pela biblioteca e acrescenta módulos específicos para o problema estudado. O código da biblioteca é distribuído sob Apache 2.0, enquanto os pesos pré-treinados podem estar sujeitos às condições da base de pré-treinamento correspondente. Por essa razão, a atribuição da biblioteca e a verificação da licença dos pesos devem permanecer separadas da autoria dos módulos desenvolvidos neste projeto \cite{ref_38}.**

**A fronteira de autoria pode ser resumida da seguinte maneira: a definição da cabeça multitarefa, com saídas multiclasses e binária, foi implementada no projeto; a arquitetura híbrida, com projeção convolucional em tokens, blocos de atenção e gate de fusão, também foi implementada no projeto; a seleção dos pesos do agregador, a calibração, a inferência com TTA, a triagem de qualidade, o controle fora do domínio e os critérios de abstenção pertencem ao pipeline desenvolvido; o localizador auxiliar, o pós-processamento morfológico e a aplicação do gate aos mapas foram igualmente integrados no escopo desta pesquisa. Em contraste, PyTorch, `torchvision`, `timm`, NumPy, scikit-learn, OpenCV, React, Vite, Express, tRPC, Drizzle, Vitest e pytest são ferramentas utilizadas para implementar, executar ou testar esses componentes.**

**Essa distinção também evita uma atribuição inadequada de originalidade. A ResNet-50 e o Vision Transformer são arquiteturas consolidadas na literatura, e o Grad-CAM é um método de explicabilidade previamente publicado \cite{ref_31, ref_32, ref_33}. A contribuição de implementação deste capítulo está na adaptação dessas ideias a um pipeline integrado de análise dermatoscópica, na definição das interfaces entre os módulos, na preservação das saídas intermediárias e na criação dos mecanismos de auditoria; não está na reivindicação de autoria das arquiteturas ou do método de explicabilidade em si.**

### 5.10.2 Comparação com modelos e sistemas relacionados

**A comparação com trabalhos relacionados foi realizada pelo escopo metodológico, e não por uma ordenação direta de acurácias. Resultados numéricos só podem ser comparados de forma responsável quando coincidem o dataset, a definição das classes, o particionamento, o protocolo de pré-processamento, o critério de seleção do modelo e o conjunto de teste. Como essas condições não são necessariamente iguais entre os estudos, a tabela a seguir identifica convergências e diferenças de desenho, sem afirmar superioridade estatística do sistema desenvolvido.**

| Abordagem ou trabalho | Característica central descrita na literatura | Como aparece no sistema desenvolvido | Diferença que deve ser preservada na interpretação |
| --- | --- | --- | --- |
| **ResNet-50 \cite{ref_31}** | **Rede residual utilizada como base para extração hierárquica de características visuais** | **Backbone convolucional do componente CNN, associado à cabeça multitarefa** | **A referência é arquitetural; não constitui, por si só, um resultado dermatológico comparável** |
| **Vision Transformer \cite{ref_32, ref_8}** | **Representação baseada em patches e autoatenção para modelar relações globais** | **Componente ViT pequeno, com atribuição de tokens na explicabilidade** | **O uso do mesmo paradigma não implica equivalência de treinamento, dados ou desempenho** |
| **Comparação CNN–ViT com XAI \cite{ref_18}** | **Estudo que confronta famílias convolucionais e Transformer e inclui explicabilidade** | **O sistema mantém as saídas dos três modelos e apresenta mapas individuais** | **A ferramenta acrescenta triagem de entrada, incerteza, histórico e integração web, mas não deve importar as métricas do estudo sem reproduzir seu protocolo** |
| **Arquitetura híbrida CNN–ViT com XAI \cite{ref_12}** | **Combinação de características convolucionais e atenção em uma arquitetura híbrida** | **Modelo híbrido próprio, com projeção em tokens, dois blocos de atenção e gate aprendido** | **A semelhança conceitual não significa que as arquiteturas, perdas ou estratégias de treinamento sejam idênticas** |
| **Ensemble com ViT e outros classificadores \cite{ref_13}** | **Agregação de modelos heterogêneos para classificação de lesões** | **Agregação das probabilidades calibradas da CNN, do ViT e do Hybrid, com pesos escolhidos na validação** | **A composição dos modelos e o protocolo de seleção dos pesos são diferentes; não há base para afirmar que um ensemble é superior ao outro** |
| **Ensemble CNN–ViT e ensemble de lesões \cite{ref_19, ref_24}** | **Uso de múltiplos classificadores para reduzir a dependência de uma única representação** | **Saída agregada acompanhada das previsões individuais e dos indicadores de incerteza** | **O sistema desenvolvido enfatiza rastreabilidade operacional, mas ainda necessita de validação externa para sustentar qualquer conclusão clínica** |

**Em relação às ferramentas de software, o projeto não propõe um novo framework de aprendizado profundo nem uma nova biblioteca de interface. PyTorch organiza tensores, treinamento e inferência; `timm` fornece os backbones reutilizados; NumPy, scikit-learn e OpenCV apoiam o processamento e a avaliação; e React, TypeScript, Express e tRPC estruturam a aplicação executável. A escolha por essa combinação, em vez de uma implementação integral em TensorFlow/Django, corresponde à arquitetura efetivamente construída e não deve ser apresentada como prova de que uma tecnologia é universalmente superior à outra.**

**A comparação mais adequada, portanto, ocorre em dois níveis. No nível algorítmico, o sistema reúne em um mesmo experimento uma CNN, um ViT e um híbrido, preservando suas saídas e produzindo uma agregação calibrada. No nível de sistema, acrescenta controle de elegibilidade, rejeição fora do domínio, recomendação de abstenção, geração de explicações, histórico de sessão e painel de métricas. Esses elementos caracterizam a integração realizada neste trabalho, mas não autorizam afirmar que o protótipo esteja clinicamente validado ou que supere as ferramentas e os modelos dos estudos relacionados.**

## 5.11 Verificação de reprodutibilidade e auditoria

A reprodutibilidade foi tratada em três níveis. No primeiro nível, foram registrados os manifestos, a seed, os grupos de lesão, os arquivos de configuração e os checkpoints. No segundo, foram executados testes de código, build de produção e testes dos módulos Python. No terceiro, foi executado o fluxo completo pela mesma rota utilizada pela interface.

A auditoria funcional registrou aprovação no TypeScript, no Vitest, no build de produção e nos testes Python. Também registrou a execução real da CNN, do ViT, do Hybrid e da saída agregada. Os quatro mapas foram encontrados como arquivos PNG de 600 × 450 pixels. O upload retornou uma URL local, a classificação retornou as URLs dos mapas, o histórico recuperou um diagnóstico e a aba de métricas carregou quatro modelos com 1.527 amostras cada.

A auditoria também identificou um problema visual em uma versão anterior. O overlay utilizava opacidade fixa e, por isso, podia colorir regiões sem saliência. A implementação foi corrigida para que a opacidade seja proporcional à saliência e para que os pixels fora da região selecionada permaneçam iguais à imagem original. A diferença máxima de pixels fora da saliência foi igual a zero na execução auditada.

Esse resultado deve ser descrito com precisão. Ele demonstra uma propriedade do renderizador, não a correção clínica do mapa. Um overlay que respeita a máscara pode continuar representando uma atribuição instável ou incompleta. Por essa razão, a discussão dos mapas deve mencionar a necessidade de testes de fidelidade, estabilidade e avaliação por especialistas.

## 5.12 Limitações da implementação

A primeira limitação está relacionada ao domínio dos dados. O classificador foi treinado e testado principalmente em imagens dermatoscópicas do HAM10000. Não é possível transferir automaticamente os resultados para fotografias clínicas comuns, imagens de celular ou populações que não estejam representadas no conjunto de desenvolvimento.

A segunda limitação está relacionada à diversidade demográfica. O HAM10000 não permite, por si só, demonstrar equidade por tom de pele, localização anatômica ou população brasileira. Uma análise de subgrupos exigiria dados externos com metadados confiáveis e termos de uso compatíveis com a pesquisa.

A terceira limitação envolve o localizador auxiliar. O Dice e o IoU foram calculados no ISIC 2016, enquanto a classificação principal foi avaliada no HAM10000. A mudança de domínio pode produzir máscaras incompletas, excessivamente amplas ou deslocadas. O gate deve ser tratado como um mecanismo visual auxiliar, não como uma segmentação clínica validada para todas as entradas.

A quarta limitação envolve a persistência. O fallback em memória permite demonstrar o sistema sem MariaDB, mas os registros são perdidos quando o processo é encerrado. A apresentação ao professor deve ocorrer em uma única sessão ou utilizar a configuração com banco persistente quando for necessário demonstrar histórico entre reinicializações.

A quinta limitação é o custo computacional. A execução de três checkpoints e dos módulos XAI é mais lenta do que uma classificação baseada em um único modelo. O tempo registrado na auditoria é específico do hardware e da configuração utilizada. Ele não deve ser apresentado como latência universal.

Por fim, os mapas de explicabilidade são aproximações matemáticas da sensibilidade do modelo. Eles não provam causalidade, não substituem a segmentação clínica e não demonstram que o modelo tomou uma decisão por uma razão clinicamente válida. Essa ressalva deve aparecer tanto no texto quanto na interface.

### 5.12.1 Representatividade demográfica e validade externa

**A observação da banca sobre a representatividade demográfica constitui uma limitação central do experimento, e não apenas uma possibilidade de melhoria de desempenho. O fato de HAM10000 e ISIC serem referências importantes para a computação em imagens dermatológicas não significa que seus resultados possam ser generalizados automaticamente para todas as populações, modalidades de aquisição ou apresentações clínicas \cite{ref_44}. Em particular, a ausência de metadados validados de tom de pele no experimento principal impede uma auditoria direta por fototipo e impede concluir que a acurácia medida no teste HAM10000 seja equivalente entre diferentes grupos populacionais.**

**Essa preocupação é consistente com estudos que avaliaram a diversidade dos dados dermatológicos. O DDI reúne 656 imagens de 570 pacientes, com diagnósticos confirmados por patologia e representação dos fototipos I a VI. Em uma comparação planejada entre fototipos claros e escuros, modelos de inteligência artificial apresentaram limitações mais acentuadas em imagens de pele escura e em doenças menos frequentes; o ajuste fino com imagens diversificadas reduziu essa diferença, mas não eliminou a necessidade de validação independente \cite{ref_40}. De forma semelhante, o Fitzpatrick17k contém 16.577 imagens clínicas anotadas por fototipo e mostrou que o desempenho tende a ser maior em tipos de pele semelhantes àqueles presentes no treinamento \cite{ref_41}. Uma revisão recente reforça que a sub-representação e a falta de rótulos verificáveis dificultam a avaliação de generalização entre tons de pele \cite{ref_42}.**

**Para aproximar a avaliação do contexto brasileiro, o PAD-UFES-20 constitui uma fonte externa relevante. Esse conjunto foi coletado no Brasil com smartphones e reúne 2.298 imagens clínicas de 1.373 pacientes e 1.641 lesões, além de informações clínicas que incluem o fototipo de Fitzpatrick. Os diagnósticos de carcinoma basocelular, carcinoma espinocelular e melanoma são confirmados por biópsia no conjunto. Entretanto, as imagens clínicas de smartphone não são equivalentes às imagens dermatoscópicas do HAM10000; por isso, o PAD-UFES-20 deve ser utilizado inicialmente como avaliação externa de mudança de domínio, e não misturado diretamente ao treinamento como se tivesse a mesma distribuição \cite{ref_39}.**

**A questão das lesões acrais também precisa ser formulada com cautela. O protocolo atual não foi desenhado para medir especificamente o desempenho em lesões de palmas, plantas ou unidade ungueal em uma população brasileira. Portanto, não se deve afirmar que o sistema reconhece adequadamente essas apresentações nem que a distribuição do HAM10000 seja suficiente para representá-las. A resposta experimental exige um subconjunto externo com localização anatômica registrada, diagnóstico confiável e quantidade suficiente de casos acrais, além da apresentação de métricas separadas para esse grupo.**

**Essa lacuna possui relevância clínica no contexto nacional. Uma coorte brasileira de melanoma acral descreveu 48 casos e destacou a escassez de dados brasileiros sobre as características epidemiológicas, clínicas, dermoscópicas e histopatológicas dessa apresentação. O estudo também reforça que lesões plantares podem apresentar padrões e dificuldades diagnósticas próprios. Essa evidência não permite inferir o desempenho do sistema proposto, mas justifica a inclusão de localização anatômica e diagnóstico confirmado no protocolo de validação externa \cite{ref_43}.**

**Na implementação atual, a triagem de qualidade e o escore fora do domínio avaliam propriedades visuais da imagem, como resolução, iluminação, nitidez, cor e distância em relação à referência do HAM10000. Esses mecanismos podem identificar entradas incompatíveis com o domínio de aquisição, mas não identificam fototipo de forma validada e não corrigem eventual desigualdade de desempenho entre grupos. O gate auxiliar utilizado nos mapas de explicabilidade também restringe a visualização da saliência; ele não altera a classificação e não constitui uma solução para viés demográfico.**

**A correção metodológica proposta para a etapa seguinte é manter o teste HAM10000 congelado e acrescentar uma validação externa pré-especificada. Essa validação deverá registrar, para cada base e para cada subgrupo disponível, o número de imagens e pacientes, a modalidade de aquisição, a distribuição de diagnósticos, a sensibilidade, a especificidade, a AUROC, a AUPRC, o F1-score, a calibração, a taxa de abstenção e os intervalos de confiança. Quando houver poucos casos em determinado fototipo ou localização, o resultado deverá ser apresentado como exploratório, sem conclusões de equidade. O treinamento com dados externos só deverá ocorrer depois dessa avaliação inicial e mediante um protocolo explícito de particionamento, controle de pacientes repetidos, autorização de uso e análise de impacto.**

### 5.12.2 Implementação do avaliador externo

**Para responder à limitação de representatividade identificada na qualificação, foi implementado um avaliador externo estratificado, separado do módulo de treinamento. O avaliador recebe um manifesto autorizado contendo o caminho da imagem, o diagnóstico, o identificador do paciente, o identificador da lesão, o fototipo ou outra anotação de tom de pele e a localização anatômica. A implementação não infere fototipo a partir dos pixels, pois uma estimativa automática de cor não equivale a um rótulo clínico validado. O protocolo foi preparado para comparar os checkpoints treinados no HAM10000 com dados externos, preservando o teste interno e registrando a modalidade de aquisição e a disponibilidade dos metadados \cite{ref_39, ref_40, ref_41, ref_42, ref_44}.**

**A avaliação externa é executada antes de qualquer ajuste fino. Para cada base e subgrupo, o sistema registra suporte, acurácia, acurácia balanceada, precisão, sensibilidade, especificidade, F1-score, AUROC, AUPRC, erro esperado de calibração e taxa de abstenção. Também são preservados os resultados por imagem, a matriz de confusão e as verificações de duplicidade por paciente e por lesão. Quando não há casos suficientes ou quando o subgrupo contém apenas uma classe, o resultado é marcado como exploratório e as métricas indefinidas não são substituídas por valores artificiais.**

**O avaliador foi implementado como uma etapa de auditoria e não como um mecanismo automático de retreinamento. Portanto, a sua existência no código-fonte não significa que a classificação já esteja validada para todos os fototipos ou para a população brasileira. Os resultados demográficos somente devem ser incorporados à dissertação depois da execução com os arquivos autorizados das bases externas e da revisão dos respectivos metadados. Para lesões acrais, o protocolo exige localização anatômica registrada, diagnóstico confiável e suporte suficiente para uma análise independente \cite{ref_43}.**

## 5.13 Síntese do desenvolvimento

O sistema desenvolvido integra uma cadeia de processamento que começa com a validação da entrada e termina com a apresentação de uma classificação acompanhada por evidências operacionais. O uso combinado de uma CNN, de um Vision Transformer e de um modelo híbrido permitiu preservar diferentes representações da imagem. A aplicação também incorporou triagem de qualidade, verificação de domínio, incerteza, recomendação de abstenção, histórico, métricas e mapas de explicabilidade.

A contribuição deste capítulo é registrar a passagem da proposta para a implementação. A ferramenta não é apresentada como um produto diagnóstico acabado. Ela é apresentada como um protótipo acadêmico capaz de executar um pipeline reprodutível, produzir artefatos auditáveis e expor ao usuário as limitações que precisam ser consideradas antes de qualquer aplicação clínica.

A versão atual atende à demonstração funcional prevista para o trabalho, mas a validação externa, a análise de equidade, a avaliação de fidelidade dos mapas e a participação de especialistas continuam sendo requisitos para uma conclusão científica mais ampla. Esses pontos devem ser discutidos na seção de limitações e em trabalhos futuros, sem serem descritos como resultados já alcançados.

## Arquivos de apoio às figuras

Os diagramas editáveis e as capturas utilizadas neste capítulo estão organizados no diretório `docs/chapter-system/`. A lista de evidências da captura está no arquivo `docs/chapter-system/screenshots/capture_evidence.json`. As imagens foram produzidas durante uma execução local da ferramenta e devem ser mantidas como figuras de autoria própria, com indicação da origem da imagem de teste quando ela não for de autoria do pesquisador.
