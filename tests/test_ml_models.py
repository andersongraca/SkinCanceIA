import torch

from ml.skin_cancer_ml.models import CNNModel, HybridModel, ViTModel


def test_cnn_multitask_shapes():
    model = CNNModel(num_classes=7, pretrained=False)
    output = model(torch.randn(2, 3, 224, 224))
    assert output.class_logits.shape == (2, 7)
    assert output.binary_logits.shape == (2,)
    assert output.aux["feature_map"].ndim == 4


def test_vit_multitask_shapes():
    model = ViTModel(num_classes=7, pretrained=False)
    output = model(torch.randn(2, 3, 224, 224))
    assert output.class_logits.shape == (2, 7)
    assert output.binary_logits.shape == (2,)
    assert output.aux["tokens"].ndim == 3


def test_hybrid_multitask_shapes_and_attention():
    model = HybridModel(num_classes=7, pretrained=False)
    output = model(torch.randn(2, 3, 224, 224))
    assert output.class_logits.shape == (2, 7)
    assert output.binary_logits.shape == (2,)
    assert output.aux["gate"].shape == (2, 1)
    assert len(output.aux["attentions"]) == 2
    assert output.aux["attentions"][0].shape[0] == 2
