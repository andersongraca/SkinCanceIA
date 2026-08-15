import json
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from ml.skin_cancer_ml.config import ExperimentConfig
from ml.skin_cancer_ml.explain import generate_heatmap
from ml.skin_cancer_ml.models import HybridModel


def test_hybrid_explainability_writes_heatmaps(tmp_path: Path):
    config = ExperimentConfig(data_dir=".", metadata_csv=".", pretrained=False)
    model = HybridModel(num_classes=7, pretrained=False, image_size=224)
    checkpoint = tmp_path / "best.pt"
    torch.save({
        "model_name": "hybrid",
        "model_state": model.state_dict(),
        "classes": list(config.classes),
        "config": config.to_dict(),
    }, checkpoint)
    (tmp_path / "calibration.json").write_text(json.dumps({"multiclass": 1.0, "binary": 1.0}), encoding="utf-8")
    image_path = tmp_path / "image.png"
    Image.fromarray(np.full((224, 224, 3), 128, dtype=np.uint8)).save(image_path)
    result = generate_heatmap(checkpoint, image_path, tmp_path / "heatmap.png")
    assert set(["cnn_gradcam", "vit_token_gradient", "attention_rollout", "hybrid"]).issubset(result["paths"])
    assert all(Path(path).exists() for path in result["paths"].values())
