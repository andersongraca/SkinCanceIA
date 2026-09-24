from __future__ import annotations

"""Avaliação externa estratificada para imagens dermatológicas.

O módulo aceita um manifesto fornecido pelo pesquisador e não infere tom de pele
pelos pixels. Os rótulos de fototipo, cor da pele e localização devem vir de
metadados autorizados e documentados na fonte do dataset.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import torch
from PIL import Image
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

try:
    from skin_cancer_ml.data import build_transforms
    from skin_cancer_ml.infer import load_model
except ModuleNotFoundError:  # Importação usada pelos testes a partir da raiz do projeto.
    from ml.skin_cancer_ml.data import build_transforms
    from ml.skin_cancer_ml.infer import load_model

DEFAULT_MALIGNANT_CLASSES = {"akiec", "bcc", "mel"}
DEFAULT_SUBGROUP_COLUMNS = (
    "fitzpatrick",
    "fitzpatrick_type",
    "skin_tone",
    "skin_type",
    "localization",
    "anatomical_site",
    "body_site",
    "sex",
    "age_group",
)


def _json_value(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if pd.isna(value):
        return None
    return value


def _ece(y_true: np.ndarray, probabilities: np.ndarray, bins: int = 10) -> float | None:
    if len(y_true) == 0:
        return None
    edges = np.linspace(0.0, 1.0, bins + 1)
    total = float(len(y_true))
    value = 0.0
    for lower, upper in zip(edges[:-1], edges[1:]):
        mask = (probabilities >= lower) & (probabilities <= upper if upper == 1 else probabilities < upper)
        if not np.any(mask):
            continue
        confidence = float(probabilities[mask].mean())
        accuracy = float(y_true[mask].mean())
        value += float(mask.sum()) / total * abs(accuracy - confidence)
    return value


def binary_metrics(y_true: Iterable[int], probabilities: Iterable[float], abstain: Iterable[bool] | None = None) -> dict[str, Any]:
    y = np.asarray(list(y_true), dtype=np.int64)
    p = np.asarray(list(probabilities), dtype=np.float64)
    if len(y) != len(p):
        raise ValueError("y_true e probabilities precisam ter o mesmo tamanho")
    if len(y) == 0:
        return {"support": 0, "status": "no_samples"}
    predictions = (p >= 0.5).astype(np.int64)
    tn, fp, fn, tp = confusion_matrix(y, predictions, labels=[0, 1]).ravel()
    result: dict[str, Any] = {
        "support": int(len(y)),
        "positive_support": int(y.sum()),
        "negative_support": int((1 - y).sum()),
        "accuracy": float(accuracy_score(y, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(y, predictions)) if len(np.unique(y)) > 1 else None,
        "precision": float(precision_score(y, predictions, zero_division=0)),
        "recall_sensitivity": float(recall_score(y, predictions, zero_division=0)),
        "specificity": float(tn / max(tn + fp, 1)),
        "f1": float(f1_score(y, predictions, zero_division=0)),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "ece": _ece(y, p),
        "abstention_rate": float(np.mean(np.asarray(list(abstain), dtype=bool))) if abstain is not None else None,
    }
    if len(np.unique(y)) > 1:
        result["auroc"] = float(roc_auc_score(y, p))
        result["auprc"] = float(average_precision_score(y, p))
    else:
        result["auroc"] = None
        result["auprc"] = None
        result["status"] = "single_class"
    return result


def _resolve_image_path(row: pd.Series, image_dir: Path | None) -> Path:
    for column in ("image_path", "image", "filepath", "file_path"):
        if column in row and pd.notna(row[column]):
            path = Path(str(row[column]))
            return path if path.is_absolute() or image_dir is None else image_dir / path
    for column in ("image_id", "isic_id", "lesion_id"):
        if column in row and pd.notna(row[column]) and image_dir is not None:
            image_id = str(row[column])
            for suffix in (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"):
                candidate = image_dir / f"{image_id}{suffix}"
                if candidate.exists():
                    return candidate
    raise ValueError("O manifesto precisa de image_path/image ou image_id com --image-dir")


def _binary_label(row: pd.Series, label_column: str, malignant_classes: set[str]) -> int:
    if label_column not in row or pd.isna(row[label_column]):
        raise ValueError(f"Coluna de rótulo ausente: {label_column}")
    value = row[label_column]
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "malignant", "maligno", "positive", "cancer"}:
            return 1
        if normalized in {"0", "false", "benign", "benigno", "negative", "non-cancer"}:
            return 0
        return int(normalized in malignant_classes)
    return int(float(value) >= 0.5)


def _load_calibration(checkpoint_path: Path) -> dict[str, float]:
    path = checkpoint_path.with_name("calibration.json")
    if not path.exists():
        return {"multiclass": 1.0, "binary": 1.0}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {"multiclass": float(raw.get("multiclass", 1.0)), "binary": float(raw.get("binary", 1.0))}


def _predict_loaded(model: torch.nn.Module, config: Any, checkpoint: dict[str, Any], calibration: dict[str, float], image_path: Path, device: torch.device, tta: bool) -> tuple[float, bool]:
    with Image.open(image_path) as source:
        image = source.convert("RGB")
        transform = build_transforms(config.image_size, train=False)
        images = [image]
        if tta:
            images.extend([
                image.transpose(Image.Transpose.FLIP_LEFT_RIGHT),
                image.transpose(Image.Transpose.FLIP_TOP_BOTTOM),
            ])
        batch = torch.stack([transform(item) for item in images]).to(device)
    with torch.no_grad():
        output = model(batch)
        class_logits = output.class_logits.detach().cpu()
        binary_logits = output.binary_logits.detach().cpu()
    class_probs = torch.softmax(class_logits / max(calibration["multiclass"], 0.05), dim=1).numpy()
    binary_probs = torch.sigmoid(binary_logits / max(calibration["binary"], 0.05)).numpy().reshape(-1)
    probability = float(binary_probs.mean())
    class_mean = class_probs.mean(axis=0)
    entropy = float(-(class_mean * np.log(np.clip(class_mean, 1e-8, 1.0))).sum() / np.log(len(config.classes)))
    variance = float(binary_probs.var())
    entropy_threshold = float(os.getenv("ML_ENTROPY_THRESHOLD", "0.75"))
    variance_threshold = float(os.getenv("ML_TTA_VARIANCE_THRESHOLD", "0.03"))
    return probability, bool(entropy > entropy_threshold or variance > variance_threshold)


def evaluate_manifest(
    manifest_path: str | Path,
    checkpoint_paths: list[str | Path],
    output_path: str | Path,
    image_dir: str | Path | None = None,
    label_column: str = "binary_label",
    subgroup_columns: Iterable[str] = DEFAULT_SUBGROUP_COLUMNS,
    split: str | None = None,
    tta: bool = True,
    weights: list[float] | None = None,
    malignant_classes: Iterable[str] = DEFAULT_MALIGNANT_CLASSES,
) -> dict[str, Any]:
    manifest = pd.read_csv(manifest_path)
    if split and "split" in manifest.columns:
        manifest = manifest[manifest["split"].astype(str).str.lower() == split.lower()].copy()
    if manifest.empty:
        raise ValueError("O manifesto não contém linhas após o filtro de split")
    malignant = {str(item).strip().lower() for item in malignant_classes}
    checkpoints = [Path(item) for item in checkpoint_paths]
    if not checkpoints:
        raise ValueError("Informe pelo menos um checkpoint")
    if weights is None:
        weights = [1.0 / len(checkpoints)] * len(checkpoints)
    if len(weights) != len(checkpoints) or sum(weights) <= 0:
        raise ValueError("A quantidade de pesos deve coincidir com a quantidade de checkpoints")
    weights_array = np.asarray(weights, dtype=np.float64)
    weights_array /= weights_array.sum()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    loaded = []
    for checkpoint_path in checkpoints:
        model, config, checkpoint = load_model(checkpoint_path, device)
        loaded.append((model, config, checkpoint, _load_calibration(checkpoint_path)))

    rows: list[dict[str, Any]] = []
    for _, row in manifest.iterrows():
        path = _resolve_image_path(row, Path(image_dir) if image_dir else None)
        if not path.exists():
            raise FileNotFoundError(path)
        predictions = []
        abstentions = []
        for model, config, checkpoint, calibration in loaded:
            probability, abstain = _predict_loaded(model, config, checkpoint, calibration, path, device, tta)
            predictions.append(probability)
            abstentions.append(abstain)
        aggregate = float(np.dot(weights_array, np.asarray(predictions, dtype=np.float64)))
        result = {
            "image_path": str(path),
            "y_true": _binary_label(row, label_column, malignant) if label_column in manifest.columns else _binary_label(row, "dx", malignant),
            "probability_malignant": aggregate,
            "abstain": bool(any(abstentions)),
        }
        for column in subgroup_columns:
            if column in manifest.columns:
                result[column] = _json_value(row[column])
        if "patient_id" in manifest.columns:
            result["patient_id"] = _json_value(row["patient_id"])
        if "lesion_id" in manifest.columns:
            result["lesion_id"] = _json_value(row["lesion_id"])
        rows.append(result)

    predictions = pd.DataFrame(rows)
    report: dict[str, Any] = {
        "protocol": {
            "manifest": str(manifest_path),
            "checkpoints": [str(item) for item in checkpoints],
            "weights": [float(item) for item in weights_array],
            "split": split,
            "tta": bool(tta),
            "label_column": label_column if label_column in manifest.columns else "dx",
            "malignant_classes": sorted(malignant),
            "device": str(device),
            "skin_tone_was_inferred_from_pixels": False,
        },
        "support": int(len(predictions)),
        "overall": binary_metrics(predictions["y_true"], predictions["probability_malignant"], predictions["abstain"]),
        "subgroups": {},
        "patient_and_lesion_checks": {
            "patient_column_present": "patient_id" in manifest.columns,
            "lesion_column_present": "lesion_id" in manifest.columns,
            "duplicate_patient_rows": int(manifest["patient_id"].duplicated().sum()) if "patient_id" in manifest.columns else None,
            "duplicate_lesion_rows": int(manifest["lesion_id"].duplicated().sum()) if "lesion_id" in manifest.columns else None,
        },
        "available_metadata_columns": [str(column) for column in manifest.columns],
        "predictions": rows,
    }
    for column in subgroup_columns:
        if column not in predictions.columns:
            continue
        column_report: dict[str, Any] = {}
        for value, group in predictions.groupby(column, dropna=False):
            key = "missing" if pd.isna(value) else str(value)
            column_report[key] = binary_metrics(group["y_true"], group["probability_malignant"], group["abstain"])
        report["subgroups"][column] = column_report
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=_json_value), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Avaliação externa estratificada por fototipo e metadados clínicos")
    parser.add_argument("--manifest", required=True, help="CSV autorizado com caminhos e rótulos das imagens")
    parser.add_argument("--checkpoint", action="append", required=True, help="Checkpoint; repita para combinar modelos")
    parser.add_argument("--weights", nargs="+", type=float)
    parser.add_argument("--image-dir")
    parser.add_argument("--label-column", default="binary_label")
    parser.add_argument("--split")
    parser.add_argument("--output", required=True)
    parser.add_argument("--no-tta", action="store_true")
    parser.add_argument("--malignant-class", action="append", default=sorted(DEFAULT_MALIGNANT_CLASSES))
    args = parser.parse_args()
    report = evaluate_manifest(
        manifest_path=args.manifest,
        checkpoint_paths=args.checkpoint,
        output_path=args.output,
        image_dir=args.image_dir,
        label_column=args.label_column,
        split=args.split,
        tta=not args.no_tta,
        weights=args.weights,
        malignant_classes=args.malignant_class,
    )
    print(json.dumps({"support": report["support"], "overall": report["overall"], "subgroups": list(report["subgroups"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()

__all__ = ["binary_metrics", "evaluate_manifest"]

# Example manifest schema (real data only; do not infer skin tone from pixels):
# image_path,dx,patient_id,lesion_id,fitzpatrick,localization,split
# img-001.jpg,mel,p-001,l-001,VI,plantar,test
# img-002,nv,p-002,l-002,II,back,test
#
# Example:
# PYTHONPATH=ml python3 ml/evaluate_external.py \
#   --manifest data/external/PAD_UFES20_manifest.csv \
#   --image-dir data/external/PAD_UFES20/images \
#   --label-column dx \
#   --checkpoint ml_artifacts/ham10000/cnn/best.pt \
#   --checkpoint ml_artifacts/ham10000/vit/best.pt \
#   --checkpoint ml_artifacts/ham10000/hybrid/best.pt \
#   --weights 0.10 0.55 0.35 \
#   --output ml_artifacts/external/pad_ufes20_baseline.json

# Sources for the protocol:
# PAD-UFES-20: https://doi.org/10.1016/j.dib.2020.106221
# DDI: https://doi.org/10.1126/sciadv.abq6147
# Fitzpatrick17k: https://doi.org/10.1109/CVPRW53098.2021.00201
# Skin type diversity review: https://doi.org/10.1007/s13671-024-00440-0
# Brazilian acral melanoma cohort: https://doi.org/10.1016/j.abd.2024.03.006
# HAM10000: https://doi.org/10.1038/sdata.2018.161

# Implementation note:
# The evaluator performs external assessment only. It does not modify checkpoints,
# select hyperparameters, or silently fine-tune on external data.
