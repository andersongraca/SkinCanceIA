from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from skin_cancer_ml.metrics import classification_metrics


def evaluate_subgroups(
    predictions_path: str | Path,
    metadata_csv: str | Path,
    group_column: str,
    output_path: str | Path,
    class_names: list[str] | None = None,
) -> dict[str, Any]:
    raw = np.load(predictions_path)
    metadata = pd.read_csv(metadata_csv)
    if len(metadata) != len(raw["labels"]):
        raise ValueError("O metadata de subgrupos deve ter exatamente uma linha por predição, na mesma ordem.")
    if group_column not in metadata.columns:
        raise ValueError(f"Coluna de subgrupo ausente: {group_column}")

    labels = raw["labels"].astype(int)
    binary_labels = raw["binary_labels"].astype(int)
    class_probabilities = raw["class_probabilities"].astype(float)
    binary_probability = raw["binary_probability"].astype(float)
    names = class_names or [f"class_{index}" for index in range(class_probabilities.shape[1])]
    groups = metadata[group_column].fillna("missing").astype(str)
    result: dict[str, Any] = {
        "predictions": str(predictions_path),
        "metadata": str(metadata_csv),
        "group_column": group_column,
        "sample_count": int(len(metadata)),
        "class_names": names,
        "subgroups": {},
        "fairness_gaps": {},
    }
    for group in sorted(groups.unique()):
        mask = groups.to_numpy() == group
        metrics = classification_metrics(
            labels[mask],
            class_probabilities[mask],
            binary_labels[mask],
            binary_probability[mask],
            class_names=names,
        )
        result["subgroups"][group] = {
            "support": int(mask.sum()),
            "metrics": metrics,
        }

    subgroup_values = result["subgroups"]
    for metric_name, path in (
        ("binary_auroc", ("binary", "auroc")),
        ("binary_sensitivity", ("binary", "sensitivity")),
        ("binary_specificity", ("binary", "specificity")),
        ("multiclass_macro_f1", ("multiclass", "macro_f1")),
    ):
        values = [entry["metrics"][path[0]][path[1]] for entry in subgroup_values.values() if entry["metrics"][path[0]][path[1]] is not None]
        if values:
            result["fairness_gaps"][metric_name] = {
                "minimum": float(min(values)),
                "maximum": float(max(values)),
                "absolute_gap": float(max(values) - min(values)),
            }

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Avaliação por subgrupo com rótulos externos validados")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--group-column", required=True, help="Coluna validada, por exemplo fitzpatrick_group")
    parser.add_argument("--output", required=True)
    parser.add_argument("--class-names", nargs="*", default=None)
    args = parser.parse_args()
    evaluate_subgroups(args.predictions, args.metadata, args.group_column, args.output, args.class_names)


if __name__ == "__main__":
    main()
