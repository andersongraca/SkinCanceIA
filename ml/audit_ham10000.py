from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


EXPECTED_CLASSES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]
TONE_COLUMNS = ["skin_tone", "fitzpatrick", "fitzpatrick_type", "melanin_index"]


def audit(metadata_csv: str | Path, split_dir: str | Path, output_path: str | Path) -> dict[str, Any]:
    metadata = pd.read_csv(metadata_csv)
    split_root = Path(split_dir)
    split_frames: dict[str, pd.DataFrame] = {}
    for split in ("train", "val", "test"):
        split_path = split_root / f"{split}.csv"
        if split_path.exists():
            split_frames[split] = pd.read_csv(split_path)

    class_counts: dict[str, dict[str, int]] = {}
    class_prevalence: dict[str, dict[str, float]] = {}
    for split, frame in split_frames.items():
        counts = frame["dx"].value_counts().reindex(EXPECTED_CLASSES, fill_value=0).astype(int)
        class_counts[split] = {name: int(counts[name]) for name in EXPECTED_CLASSES}
        total = max(int(counts.sum()), 1)
        class_prevalence[split] = {name: float(counts[name] / total) for name in EXPECTED_CLASSES}

    total_counts = metadata["dx"].value_counts().reindex(EXPECTED_CLASSES, fill_value=0).astype(int)
    total = max(int(total_counts.sum()), 1)
    rare_classes = [name for name in EXPECTED_CLASSES if float(total_counts[name] / total) < 0.02]
    demographic_columns = [column for column in ["age", "sex", "localization", "patient_id", *TONE_COLUMNS] if column in metadata.columns]
    missing_columns = [column for column in ["patient_id", *TONE_COLUMNS] if column not in metadata.columns]
    missing_values = {column: int(metadata[column].isna().sum()) for column in demographic_columns}
    sex_distribution = metadata["sex"].fillna("missing").value_counts(dropna=False).to_dict() if "sex" in metadata.columns else {}
    localization_distribution = metadata["localization"].fillna("missing").value_counts(dropna=False).to_dict() if "localization" in metadata.columns else {}

    report: dict[str, Any] = {
        "metadata_rows": int(len(metadata)),
        "class_counts_total": {name: int(total_counts[name]) for name in EXPECTED_CLASSES},
        "class_prevalence_total": {name: float(total_counts[name] / total) for name in EXPECTED_CLASSES},
        "rare_classes_below_2_percent": rare_classes,
        "split_class_counts": class_counts,
        "split_class_prevalence": class_prevalence,
        "available_demographic_columns": demographic_columns,
        "missing_demographic_columns": missing_columns,
        "missing_values": missing_values,
        "sex_distribution": {str(key): int(value) for key, value in sex_distribution.items()},
        "localization_distribution": {str(key): int(value) for key, value in localization_distribution.items()},
        "skin_tone_analysis": {
            "performed": False,
            "reason": "HAM10000 metadata does not provide a validated skin-tone or Fitzpatrick label; no tone group was inferred from pixels.",
            "external_validation_recommended": True,
        },
    }
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Auditoria de classes e variáveis demográficas do HAM10000")
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--split-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    audit(args.metadata, args.split_dir, args.output)


if __name__ == "__main__":
    main()
