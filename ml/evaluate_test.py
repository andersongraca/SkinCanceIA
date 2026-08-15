from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader

from skin_cancer_ml.data import DermoscopyDataset
from skin_cancer_ml.infer import load_model
from skin_cancer_ml.metrics import classification_metrics
from skin_cancer_ml.train import _collate


def evaluate(checkpoint_path: str | Path, test_csv: str | Path, batch_size: int = 32) -> dict[str, Any]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, config, checkpoint = load_model(checkpoint_path, device)
    frame = __import__("pandas").read_csv(test_csv)
    loader = DataLoader(
        DermoscopyDataset(frame, config, train=False),
        batch_size=batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        collate_fn=_collate,
    )
    calibration_path = Path(checkpoint_path).with_name("calibration.json")
    calibration = json.loads(calibration_path.read_text(encoding="utf-8")) if calibration_path.exists() else {"multiclass": 1.0, "binary": 1.0}
    class_temperature = max(float(calibration.get("multiclass", 1.0)), 0.05)
    binary_temperature = max(float(calibration.get("binary", 1.0)), 0.05)
    class_logits: list[np.ndarray] = []
    binary_logits: list[np.ndarray] = []
    class_labels: list[np.ndarray] = []
    binary_labels: list[np.ndarray] = []
    with torch.no_grad():
        for batch in loader:
            output = model(batch["image"].to(device))
            class_logits.append(output.class_logits.float().cpu().numpy())
            binary_logits.append(output.binary_logits.float().cpu().numpy())
            class_labels.append(batch["class_index"].numpy())
            binary_labels.append(batch["binary_label"].numpy().astype(int))
    class_logit_array = np.concatenate(class_logits)
    binary_logit_array = np.concatenate(binary_logits)
    labels = np.concatenate(class_labels)
    binary_targets = np.concatenate(binary_labels)
    class_probabilities = torch.softmax(torch.tensor(class_logit_array / class_temperature), dim=1).numpy()
    binary_probability = torch.sigmoid(torch.tensor(binary_logit_array / binary_temperature)).numpy()
    metrics = classification_metrics(labels, class_probabilities, binary_targets, binary_probability, class_names=list(config.classes))
    result = {
        "checkpoint": str(checkpoint_path),
        "model": checkpoint["model_name"],
        "device": str(device),
        "sample_count": int(len(labels)),
        "calibration": calibration,
        "metrics": metrics,
    }
    output_dir = Path(checkpoint_path).parent
    np.savez(
        output_dir / "test_predictions.npz",
        labels=labels,
        binary_labels=binary_targets,
        class_probabilities=class_probabilities,
        binary_probability=binary_probability,
    )
    output_path = Path(checkpoint_path).with_name("test_metrics.json")
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Avaliação final no conjunto de teste HAM10000")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--test-csv", required=True)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    evaluate(args.checkpoint, args.test_csv, args.batch_size)


if __name__ == "__main__":
    main()
