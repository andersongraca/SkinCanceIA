# Evidências visuais verificadas

## Entrada aceita

`data/raw/images/ISIC_0024339.jpg` é uma imagem dermatoscópica HAM10000 de 600×450 px, com uma lesão pigmentada central sobre fundo cutâneo. Foi a imagem usada no teste end-to-end do serviço TypeScript e foi aceita pela triagem de qualidade/OOD.

## Entrada rejeitada: carro

`test_assets/ood/public_car_picryl.jpg` é uma fotografia histórica de um carro com pessoas, de 512×452 px. Ela representa uma entrada fora do domínio dermatoscópico e foi usada no teste de rejeição OOD.

## Entrada rejeitada: cabeça/cabelo

`test_assets/ood/public_head_picryl.jpg` é uma imagem de rosto/cabeça sobre fundo preto, de 512×512 px. Ela representa uma entrada não dermatoscópica e foi usada no teste de rejeição OOD.

## Heatmap CNN

`ml_artifacts/ham10000/xai/demo/cnn_gradcam.png` é um overlay Grad-CAM de 160×160 px produzido pelo checkpoint CNN. O mapa utiliza cores frias e quentes para indicar a intensidade relativa da atribuição; não deve ser interpretado como uma máscara clínica.

## Heatmap ViT

`ml_artifacts/ham10000/xai/demo/vit_token_gradient.png` é um mapa de atribuição de tokens de 160×160 px produzido pelo checkpoint ViT. A região da lesão permanece visível no centro do overlay, com intensidade relativa mais concentrada nessa área.

## Heatmap híbrido

`ml_artifacts/ham10000/xai/demo/hybrid_hybrid.png` é o mapa combinado de 160×160 px produzido pelo híbrido CNN–ViT, combinando evidência convolucional e atenção/tokenização. Ele é uma explicação aproximada da decisão, não uma anotação clínica.
