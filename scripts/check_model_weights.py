from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "ml"))

from skin_cancer_ml.models import build_model


model = build_model("cnn", 7, pretrained=True, image_size=160)
print(type(model).__name__)
print(sum(parameter.numel() for parameter in model.parameters()))
