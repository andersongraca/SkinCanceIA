from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from skin_cancer_ml.config import ExperimentConfig
from skin_cancer_ml.data import discover_images, split_grouped, summarize_split


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Preparar HAM10000 para experimento reproduzível")
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--metadata-csv", required=True)
    parser.add_argument("--output-dir", default="ml_artifacts/ham10000")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--validation-fraction", type=float, default=0.15)
    parser.add_argument("--test-fraction", type=float, default=0.15)
    args = parser.parse_args()

    config = ExperimentConfig(
        data_dir=args.data_dir,
        metadata_csv=args.metadata_csv,
        output_dir=args.output_dir,
        seed=args.seed,
        validation_fraction=args.validation_fraction,
        test_fraction=args.test_fraction,
    )
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    frame = discover_images(args.data_dir, args.metadata_csv, config)
    splits = split_grouped(frame, config)
    summary = summarize_split(splits, config.label_column)
    summary.to_csv(out / "split_summary.csv", index=False)
    frame.to_csv(out / "manifest.csv", index=False)
    for name, split in splits.items():
        split.to_csv(out / f"{name}.csv", index=False)

    class_counts = {
        name: split[config.label_column].value_counts().sort_index().to_dict()
        for name, split in splits.items()
    }
    group_counts = {name: int(split["group_id"].nunique()) for name, split in splits.items()}
    missing_images = int(len(pd.read_csv(args.metadata_csv)) - len(frame))
    metadata_path = Path(args.metadata_csv)
    manifest = {
        "dataset": "HAM10000",
        "source_doi": "10.7910/DVN/DBW86T",
        "source_url": "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T",
        "version": "4.0",
        "license": "CC BY-NC 4.0",
        "academic_noncommercial_use_confirmed": True,
        "seed": args.seed,
        "image_count": int(len(frame)),
        "metadata_row_count": int(len(pd.read_csv(args.metadata_csv))),
        "missing_image_count": missing_images,
        "unique_lesion_groups": int(frame["group_id"].nunique()),
        "classes": list(config.classes),
        "malignant_classes": list(config.malignant_classes),
        "class_counts": class_counts,
        "group_counts": group_counts,
        "split_fractions": {"validation": args.validation_fraction, "test": args.test_fraction},
        "metadata_sha256": sha256_file(metadata_path),
    }
    (out / "dataset_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    config.save(out / "config.json")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
