# Validação local no Windows

**Data:** 20 de agosto de 2026  
**Projeto:** SkinCancerCADDermoIA — PROCC/UFS

## Ambiente

O banco MariaDB local respondeu em `127.0.0.1:3306`, o backend foi servido em `http://localhost:3000` e o `.venv` Windows continha as dependências necessárias para inferência: PyTorch 2.6.0+cu124, torchvision 0.21.0+cu124, timm 1.0.28, scikit-learn 1.9.0, OpenCV, Pillow, PyYAML, pandas e NumPy.

O modo de demonstração local criou e reutilizou o usuário `local-demo` no banco. A ausência de `OAUTH_SERVER_URL` foi apenas informada pelo SDK OAuth; não impediu o modo demo porque o ambiente não está em produção.

## Fluxo OOD

Uma imagem pública fora do domínio dermatoscópico foi enviada por uma chamada tRPC direta. O backend criou o registro da imagem, calculou a elegibilidade e retornou `status: rejected`, com motivo `outside_dermoscopy_domain`. O registro temporário foi removido após o teste.

## Fluxo HAM10000

A imagem pública `ISIC_0024306.jpg` do HAM10000 foi enviada por uma chamada tRPC direta. O fluxo completo foi concluído:

| Etapa | Resultado |
|---|---|
| Usuário autenticado | `local-demo` |
| Upload | Registro de imagem criado |
| Elegibilidade | Aceita; 600 × 450; OOD score 0,619, abaixo do limiar 196,230 |
| CNN ResNet-50 | `benign` |
| Vision Transformer | `benign` |
| Híbrido CNN-ViT | `benign` |
| Ensemble | `benign`, confiança 91,78% |
| Heatmaps | CNN Grad-CAM, ViT token-gradient e híbrido persistidos |
| Diagnóstico | Registro criado no MariaDB |

A imagem, o diagnóstico e os heatmaps deste teste foram removidos ao final, para não poluir o banco de desenvolvimento.

## Métricas persistidas

O script `scripts/persist_real_metrics.ts` foi criado para ler `ml_artifacts/ham10000/ensemble/test_metrics.json` e persistir as métricas binárias reais dos três componentes e do ensemble. A aba **Métricas** da interface existente passou a exibir quatro linhas, todas com `n = 1.527`:

| Modelo | Acurácia | Sensibilidade | Especificidade | F1 | AUROC | Precisão |
|---|---:|---:|---:|---:|---:|---:|
| CNN (ResNet-50) | 73% | 73% | 73% | 52% | 83% | 40% |
| Vision Transformer | 73% | 85% | 69% | 55% | 85% | 41% |
| Híbrido CNN-ViT | 74% | 80% | 73% | 55% | 84% | 42% |
| Ensemble Learning | 75% | 82% | 73% | 56% | 86% | 43% |

Os percentuais são arredondados no armazenamento, enquanto o arquivo JSON continua sendo a fonte dos valores de maior precisão.

## Observação científica

A validação confirma o encadeamento técnico local e a integração com o banco; não constitui validação clínica nem autorização para uso diagnóstico. A interface React não foi alterada.
