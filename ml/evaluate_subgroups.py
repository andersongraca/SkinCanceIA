from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from skin_cancer_ml.metrics import classification_metrics


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def evaluate_subgroups(
    predictions_path: str | Path,
    metadata_csv: str | Path,
    group_column: str,
    output_path: str | Path,
    class_names: list[str] | None = None,
    min_group_support: int = 20,
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
        "min_group_support_for_gaps": int(min_group_support),
        "subgroups": {},
        "fairness_gaps": {},
    }
    group_array = groups.to_numpy()
    for group in sorted(groups.unique()):
        mask = group_array == group
        subgroup_binary = binary_labels[mask]
        positive_support = int(subgroup_binary.sum())
        negative_support = int(len(subgroup_binary) - positive_support)
        metrics = _json_safe(classification_metrics(
            labels[mask],
            class_probabilities[mask],
            subgroup_binary,
            binary_probability[mask],
            class_names=names,
        ))
        binary_validity = {
            "auroc": positive_support > 0 and negative_support > 0,
            "sensitivity": positive_support > 0,
            "specificity": negative_support > 0,
        }
        result["subgroups"][group] = {
            "support": int(mask.sum()),
            "positive_support": positive_support,
            "negative_support": negative_support,
            "eligible_for_fairness_gaps": int(mask.sum()) >= min_group_support and positive_support > 0 and negative_support > 0,
            "binary_metric_validity": binary_validity,
            "metrics": metrics,
        }

    subgroup_values = result["subgroups"]
    result["fairness_gap_groups"] = {
        "eligible": [group for group, entry in subgroup_values.items() if entry["eligible_for_fairness_gaps"]],
        "excluded": [group for group, entry in subgroup_values.items() if not entry["eligible_for_fairness_gaps"]],
    }
    for metric_name, path in (
        ("binary_auroc", ("binary", "auroc")),
        ("binary_sensitivity", ("binary", "sensitivity")),
        ("binary_specificity", ("binary", "specificity")),
        ("multiclass_macro_f1", ("multiclass", "macro_f1")),
    ):
        values = [
            entry["metrics"][path[0]][path[1]]
            for entry in subgroup_values.values()
            if entry["eligible_for_fairness_gaps"] and entry["metrics"][path[0]][path[1]] is not None
        ]
        if values:
            result["fairness_gaps"][metric_name] = {
                "minimum": float(min(values)),
                "maximum": float(max(values)),
                "absolute_gap": float(max(values) - min(values)),
                "eligible_group_count": len(values),
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
    parser.add_argument("--min-group-support", type=int, default=20)
    args = parser.parse_args()
    if args.min_group_support < 1:
        raise ValueError("--min-group-support deve ser positivo")
    evaluate_subgroups(args.predictions, args.metadata, args.group_column, args.output, args.class_names, args.min_group_support)


if __name__ == "__main__":
    main()
