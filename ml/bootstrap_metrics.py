from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from skin_cancer_ml.metrics import classification_metrics


def percentile_interval(values: list[float], confidence: float) -> dict[str, float | int | None]:
    if not values:
        return {"n": 0, "estimate": None, "lower": None, "upper": None}
    array = np.asarray(values, dtype=float)
    alpha = (1.0 - confidence) / 2.0
    return {
        "n": int(array.size),
        "estimate": float(np.mean(array)),
        "lower": float(np.quantile(array, alpha)),
        "upper": float(np.quantile(array, 1.0 - alpha)),
    }


def bootstrap(predictions_path: str | Path, output_path: str | Path, repeats: int = 1000, seed: int = 42, confidence: float = 0.95) -> dict[str, Any]:
    raw = np.load(predictions_path)
    labels = raw["labels"].astype(int)
    binary_labels = raw["binary_labels"].astype(int)
    class_probabilities = raw["class_probabilities"].astype(float)
    binary_probability = raw["binary_probability"].astype(float)
    rng = np.random.default_rng(seed)
    values: dict[str, list[float]] = {
        "multiclass_macro_f1": [],
        "multiclass_auroc_macro_ovr": [],
        "binary_auroc": [],
        "binary_sensitivity": [],
        "binary_specificity": [],
        "binary_f1": [],
    }
    for _ in range(repeats):
        indices = rng.integers(0, len(labels), size=len(labels))
        metrics = classification_metrics(
            labels[indices],
            class_probabilities[indices],
            binary_labels[indices],
            binary_probability[indices],
        )
        values["multiclass_macro_f1"].append(metrics["multiclass"]["macro_f1"])
        if metrics["multiclass"]["auroc_macro_ovr"] is not None:
            values["multiclass_auroc_macro_ovr"].append(metrics["multiclass"]["auroc_macro_ovr"])
        if metrics["binary"]["auroc"] is not None:
            values["binary_auroc"].append(metrics["binary"]["auroc"])
        values["binary_sensitivity"].append(metrics["binary"]["sensitivity"])
        values["binary_specificity"].append(metrics["binary"]["specificity"])
        values["binary_f1"].append(metrics["binary"]["f1"])

    report: dict[str, Any] = {
        "predictions": str(predictions_path),
        "sample_count": int(len(labels)),
        "bootstrap_repeats": int(repeats),
        "seed": int(seed),
        "confidence_level": float(confidence),
        "intervals": {name: percentile_interval(series, confidence) for name, series in values.items()},
    }
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Intervalos de confiança por bootstrap no teste congelado")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--repeats", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--confidence", type=float, default=0.95)
    args = parser.parse_args()
    bootstrap(args.predictions, args.output, args.repeats, args.seed, args.confidence)


if __name__ == "__main__":
    main()
