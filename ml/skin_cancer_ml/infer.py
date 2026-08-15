from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json

import numpy as np
import torch
from PIL import Image

from .config import ExperimentConfig
from .data import build_transforms
from .models import build_model


def _config_from_dict(raw: dict[str, Any]) -> ExperimentConfig:
    raw = dict(raw)
    raw["classes"] = tuple(raw.get("classes", []))
    raw["malignant_classes"] = tuple(raw.get("malignant_classes", []))
    return ExperimentConfig(**raw)


def load_model(checkpoint_path: str | Path, device: torch.device) -> tuple[torch.nn.Module, ExperimentConfig, dict[str, Any]]:
    checkpoint = torch.load(checkpoint_path, map_location=device)
    config = _config_from_dict(checkpoint["config"])
    model = build_model(checkpoint["model_name"], len(config.classes), pretrained=False, image_size=config.image_size)
    model.load_state_dict(checkpoint["model_state"])
    model.to(device).eval()
    return model, config, checkpoint


def _predict_tensor(model: torch.nn.Module, tensor: torch.Tensor, device: torch.device) -> tuple[np.ndarray, np.ndarray]:
    with torch.no_grad():
        output = model(tensor.to(device))
        return output.class_logits.detach().cpu().numpy(), output.binary_logits.detach().cpu().numpy()


def predict_image(checkpoint_path: str | Path, image_path: str | Path, tta: bool = True) -> dict[str, Any]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, config, checkpoint = load_model(checkpoint_path, device)
    with Image.open(image_path) as image:
        image = image.convert("RGB")
        transform = build_transforms(config.image_size, train=False)
        tensors = [transform(image)]
        if tta:
            tensors.extend([transform(image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)), transform(image.transpose(Image.Transpose.FLIP_TOP_BOTTOM))])
    batch = torch.stack(tensors)
    class_logits, binary_logits = _predict_tensor(model, batch, device)
    calibration_path = Path(checkpoint_path).with_name("calibration.json")
    calibration = json.loads(calibration_path.read_text(encoding="utf-8")) if calibration_path.exists() else {"multiclass": 1.0, "binary": 1.0}
    class_probability_samples = torch.softmax(torch.tensor(class_logits / max(float(calibration.get("multiclass", 1.0)), 0.05)), dim=1).numpy()
    binary_probability_samples = torch.sigmoid(torch.tensor(binary_logits / max(float(calibration.get("binary", 1.0)), 0.05))).numpy()
    class_probabilities = class_probability_samples.mean(axis=0)
    binary_probability = float(binary_probability_samples.mean())
    predictive_entropy = float(-(class_probabilities * np.log(np.clip(class_probabilities, 1e-8, 1.0))).sum() / np.log(len(config.classes)))
    tta_variance = float(binary_probability_samples.var())
    fine_index = int(class_probabilities.argmax())
    fine_class = config.classes[fine_index]
    classification = "malignant" if binary_probability >= 0.5 else "benign"
    confidence = binary_probability if classification == "malignant" else 1.0 - binary_probability
    return {
        "classification": classification,
        "confidence": round(confidence * 100.0, 4),
        "probabilities": {"benign": round(1.0 - binary_probability, 8), "malignant": round(binary_probability, 8)},
        "fineGrainedClass": fine_class,
        "fineGrainedProbabilities": {label: round(float(prob), 8) for label, prob in zip(config.classes, class_probabilities)},
        "uncertainty": {"predictiveEntropy": predictive_entropy, "ttaVariance": tta_variance, "abstain": bool(predictive_entropy > 0.65 or tta_variance > 0.02)},
        "ttaSamples": len(tensors),
        "modelVersion": str(checkpoint.get("config", {}).get("model_name", checkpoint["model_name"])),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inferência de uma imagem dermatoscópica")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--no-tta", action="store_true")
    args = parser.parse_args()
    print(json.dumps(predict_image(args.checkpoint, args.image, tta=not args.no_tta), ensure_ascii=False))


if __name__ == "__main__":
    main()
