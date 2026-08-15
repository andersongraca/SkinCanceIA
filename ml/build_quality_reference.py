from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from skin_cancer_ml.config import ExperimentConfig
from skin_cancer_ml.data import discover_images, split_grouped
from skin_cancer_ml.quality import build_reference, image_features
from PIL import Image


def collect(frame: pd.DataFrame) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for index, image_path in enumerate(frame["image_path"].astype(str), start=1):
        with Image.open(image_path) as image:
            rows.append(image_features(image))
        if index % 1000 == 0:
            print(f"processed={index}", flush=True)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrar referência de qualidade/OOD HAM10000")
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--metadata-csv", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    config = ExperimentConfig(data_dir=args.data_dir, metadata_csv=args.metadata_csv, seed=args.seed)
    frame = discover_images(args.data_dir, args.metadata_csv, config)
    splits = split_grouped(frame, config)
    train_rows = collect(splits["train"])
    val_rows = collect(splits["val"])
    reference = build_reference(train_rows, val_rows)
    reference["seed"] = args.seed
    reference["train_group_count"] = int(splits["train"]["group_id"].nunique())
    reference["validation_group_count"] = int(splits["val"]["group_id"].nunique())
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(reference, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(reference, ensure_ascii=False))


if __name__ == "__main__":
    main()
