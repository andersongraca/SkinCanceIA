from pathlib import Path

import pytest
import torch
from PIL import Image

from ml.skin_cancer_ml.lesion_segmentation import predict_lesion_mask, segmentation_sensitivity_config


CHECKPOINT = Path(__file__).parents[1] / "ml_artifacts" / "isic2016_segmentation" / "lesion_segmentation.pt"


@pytest.mark.skipif(not CHECKPOINT.exists(), reason="checkpoint ISIC não instalado")
def test_lesion_segmenter_returns_mask_and_metadata():
    image = Image.new("RGB", (600, 450), (180, 140, 130))
    mask, metadata = predict_lesion_mask(image, CHECKPOINT, torch.device("cpu"))
    assert mask.ndim == 2
    assert mask.shape == (160, 160)
    assert 0.0 <= float(mask.mean()) <= 1.0
    assert metadata["imageSize"] == 160


@pytest.mark.parametrize(
    ("mode", "threshold", "kernel"),
    [("strict", 0.65, 3), ("balanced", 0.50, 5), ("permissive", 0.35, 7)],
)
def test_lesion_gate_presets(monkeypatch, mode, threshold, kernel):
    monkeypatch.setenv("ML_LESION_GATE_MODE", mode)
    config = segmentation_sensitivity_config()
    assert config["threshold"] == threshold
    assert config["kernel"] == kernel
