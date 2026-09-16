# Localização da lesão para explicabilidade

## Objetivo

Os mapas Grad-CAM, atribuição de tokens e ensemble explicam evidência do classificador; eles não são, por si só, máscaras da lesão. Para reduzir ativações em fundo, o sistema usa um localizador auxiliar de lesão treinado com o conjunto oficial ISIC 2016 Part 1, que possui 900 imagens dermatoscópicas e 900 máscaras binárias.

A máscara auxiliar é usada como um gate de visualização: saliências dentro da região prevista permanecem fortes e saliências fora dela são atenuadas. A decisão de classificação continua sendo produzida pelos checkpoints CNN, ViT e Hybrid do HAM10000; o segmentador não altera a classe nem o score.

## Avaliação

O treinamento foi feito com seed 42, divisão 720/90/90 e imagens redimensionadas para 160×160. No conjunto de teste independente do ISIC 2016, o localizador obteve Dice de 0,8245 e IoU de 0,7667. Esses valores avaliam a segmentação no ISIC 2016; não provam a mesma qualidade em todas as imagens HAM10000 ou em fotografias clínicas.

## Limitações

Uma máscara segmentada não torna Grad-CAM uma explicação causal. O ISIC 2016 contém variação de equipamento, iluminação, pelos e composição, e a máscara pode incluir artefatos ou falhar em imagens fora do domínio. O sistema rejeita a máscara quando a área prevista é menor que 1% ou maior que 90%; nesses casos o mapa original é mantido e a falha deve ser revisada.

O checkpoint é distribuído somente para fins acadêmicos e de pesquisa conforme os termos do dataset de origem. O teste de segmentação permanece separado do teste de classificação HAM10000.

## Configuração

Por padrão, o servidor procura:

```text
ml_artifacts/isic2016_segmentation/lesion_segmentation.pt
```

É possível substituir o caminho com:

```text
ML_LESION_SEGMENTER_CHECKPOINT=/caminho/lesion_segmentation.pt
```

## Sensibilidade para pelos e iluminação

O gate possui três presets controlados por `ML_LESION_GATE_MODE`:

| Modo | Limiar da máscara | Kernel morfológico | Uso recomendado |
|---|---:|---:|---|
| `strict` | 0,65 | 3×3 | Imagem limpa, fundo uniforme; reduz falsos positivos do fundo |
| `balanced` | 0,50 | 5×5 | Padrão geral |
| `permissive` | 0,35 | 7×7 | Muitos pelos, sombra ou iluminação irregular; pode incluir mais fundo |

Para uma imagem com muitos pelos, use `permissive` antes de iniciar o servidor:

```powershell
$env:ML_LESION_GATE_MODE = "permissive"
```

Para voltar ao comportamento padrão:

```powershell
$env:ML_LESION_GATE_MODE = "balanced"
```

Também existem ajustes avançados (`ML_LESION_MASK_THRESHOLD`, `ML_LESION_MORPH_KERNEL`, `ML_LESION_MASK_MIN_AREA` e `ML_LESION_MASK_MAX_AREA`), mas eles só devem ser alterados durante uma calibração documentada. Tornar o gate permissivo não melhora o classificador; apenas reduz o risco de cortar a lesão na visualização.

O gate é aplicado no script `ml/skin_cancer_ml/explain.py`. A interface deve descrever esses arquivos como explicações aproximadas e não como segmentação clínica ou prova de causalidade.

## Fonte

ISIC Challenge 2016, Task 1, página oficial: https://challenge.isic-archive.com/data/ . A tabela oficial identifica 900 imagens de treino, 900 máscaras e licença CC0.
