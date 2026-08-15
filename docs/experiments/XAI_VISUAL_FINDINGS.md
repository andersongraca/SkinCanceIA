# Verificação visual de explicabilidade

A imagem HAM10000 `ISIC_0027419.jpg` foi processada pelos checkpoints reais. O Grad-CAM da ResNet-50 foi gerado em `ml_artifacts/ham10000/xai/demo/cnn_gradcam.png`; o mapa apresenta sobreposição colorida visível e destaca regiões da imagem, mas deve ser interpretado como evidência de atribuição do modelo, não como delimitação clínica de uma lesão.

O mapa combinado do híbrido CNN–ViT foi gerado em `ml_artifacts/ham10000/xai/demo/hybrid_hybrid.png`; a sobreposição também está visível e combina sinais convolucionais e de atenção. A inspeção visual confirma que os arquivos não são placeholders vazios. A validação quantitativa da fidelidade dos mapas deverá ser feita separadamente com métricas de localização quando houver máscaras anotadas; o HAM10000 usado neste experimento não fornece, neste pipeline, uma máscara clínica de referência para afirmar causalidade.
