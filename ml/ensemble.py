from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

from skin_cancer_ml.config import DEFAULT_CLASSES
from skin_cancer_ml.data import DermoscopyDataset
from skin_cancer_ml.infer import load_model
from skin_cancer_ml.metrics import classification_metrics
from skin_cancer_ml.train import _collate


MODEL_NAMES = ("cnn", "vit", "hybrid")


def calibrated_probabilities(logits: np.ndarray, binary_logits: np.ndarray, calibration: dict[str, float]) -> tuple[np.ndarray, np.ndarray]:
    class_temperature = max(float(calibration.get("multiclass", 1.0)), 0.05)
    binary_temperature = max(float(calibration.get("binary", 1.0)), 0.05)
    class_probs = torch.softmax(torch.tensor(logits / class_temperature), dim=1).numpy()
    binary_probs = torch.sigmoid(torch.tensor(binary_logits / binary_temperature)).numpy()
    return class_probs, binary_probs


def validation_arrays(root: Path, name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    model_dir = root / name
    raw = np.load(model_dir / "best_validation_logits.npz")
    calibration = json.loads((model_dir / "calibration.json").read_text(encoding="utf-8"))
    class_probs, binary_probs = calibrated_probabilities(raw["class_logits"], raw["binary_logits"], calibration)
    return raw["labels"], raw["binary_labels"], class_probs, binary_probs


def fit_weights(root: Path) -> dict[str, float]:
    arrays = [validation_arrays(root, name) for name in MODEL_NAMES]
    labels, binary_labels = arrays[0][0], arrays[0][1]
    best_score = -float("inf")
    best_weights = (1 / 3, 1 / 3, 1 / 3)
    minimum_weight = 0.10
    for first in np.arange(minimum_weight, 1.001, 0.05):
        for second in np.arange(minimum_weight, 1.001 - first + 1e-9, 0.05):
            third = 1.0 - first - second
            if third < minimum_weight - 1e-9:
                continue
            weights = np.asarray([first, second, max(third, 0.0)])
            class_probs = sum(weights[i] * arrays[i][2] for i in range(3))
            binary_probs = sum(weights[i] * arrays[i][3] for i in range(3))
            metrics = classification_metrics(labels, class_probs, binary_labels, binary_probs)
            macro_f1 = metrics["multiclass"]["macro_f1"]
            binary_auroc = metrics["binary"]["auroc"] or 0.0
            score = 0.5 * macro_f1 + 0.5 * binary_auroc
            if score > best_score:
                best_score = score
                best_weights = tuple(float(value) for value in weights)
    return {name: weight for name, weight in zip(MODEL_NAMES, best_weights)}


def test_arrays(root: Path, test_csv: Path, batch_size: int) -> tuple[np.ndarray, np.ndarray, dict[str, tuple[np.ndarray, np.ndarray]]]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    test_frame = pd.read_csv(test_csv)
    result: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    labels: np.ndarray | None = None
    binary_labels: np.ndarray | None = None
    for name in MODEL_NAMES:
        checkpoint = root / name / "best.pt"
        model, config, _ = load_model(checkpoint, device)
        loader = DataLoader(DermoscopyDataset(test_frame, config, train=False), batch_size=batch_size, shuffle=False, num_workers=config.num_workers, collate_fn=_collate)
        class_logits: list[np.ndarray] = []
        binary_logits: list[np.ndarray] = []
        classes: list[np.ndarray] = []
        binaries: list[np.ndarray] = []
        with torch.no_grad():
            for batch in loader:
                output = model(batch["image"].to(device))
                class_logits.append(output.class_logits.float().cpu().numpy())
                binary_logits.append(output.binary_logits.float().cpu().numpy())
                classes.append(batch["class_index"].numpy())
                binaries.append(batch["binary_label"].numpy().astype(int))
        result[name] = (np.concatenate(class_logits), np.concatenate(binary_logits))
        if labels is None:
            labels = np.concatenate(classes)
            binary_labels = np.concatenate(binaries)
    assert labels is not None and binary_labels is not None
    return labels, binary_labels, result


def main() -> None:
    parser = argparse.ArgumentParser(description="Ensemble calibrado CNN-ViT-híbrido")
    parser.add_argument("--root", required=True, help="Diretório que contém cnn/, vit/ e hybrid/")
    parser.add_argument("--test-csv", required=True)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    root = Path(args.root)
    weights = fit_weights(root)
    labels, binary_labels, test_logits = test_arrays(root, Path(args.test_csv), args.batch_size)
    class_probs: list[np.ndarray] = []
    binary_probs: list[np.ndarray] = []
    component_test_metrics: dict[str, Any] = {}
    for name in MODEL_NAMES:
        calibration = json.loads((root / name / "calibration.json").read_text(encoding="utf-8"))
        classes, binaries = calibrated_probabilities(test_logits[name][0], test_logits[name][1], calibration)
        class_probs.append(classes)
        binary_probs.append(binaries)
        component_test_metrics[name] = classification_metrics(labels, classes, binary_labels, binaries, class_names=DEFAULT_CLASSES)
    ensemble_classes = sum(weights[name] * class_probs[index] for index, name in enumerate(MODEL_NAMES))
    ensemble_binary = sum(weights[name] * binary_probs[index] for index, name in enumerate(MODEL_NAMES))
    ensemble_metrics = classification_metrics(labels, ensemble_classes, binary_labels, ensemble_binary, class_names=DEFAULT_CLASSES)
    output_dir = root / "ensemble"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "weights.json").write_text(json.dumps(weights, indent=2), encoding="utf-8")
    np.savez(
        output_dir / "test_predictions.npz",
        labels=labels,
        binary_labels=binary_labels,
        class_probabilities=ensemble_classes,
        binary_probability=ensemble_binary,
    )
    report = {
        "models": list(MODEL_NAMES),
        "weights_selected_on": "validation",
        "weights": weights,
        "test_sample_count": int(len(labels)),
        "component_test_metrics": component_test_metrics,
        "ensemble_test_metrics": ensemble_metrics,
    }
    (output_dir / "test_metrics.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
