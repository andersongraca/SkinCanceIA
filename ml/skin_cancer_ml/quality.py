from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

import numpy as np
from PIL import Image, UnidentifiedImageError


FEATURE_NAMES = (
    "aspect_ratio",
    "mean_red",
    "mean_green",
    "mean_blue",
    "std_red",
    "std_green",
    "std_blue",
    "mean_luma",
    "std_luma",
    "sharpness",
    "edge_strength",
    "dark_fraction",
    "bright_fraction",
    "center_luma",
    "center_std",
)


@dataclass(frozen=True)
class QualityConfig:
    min_width: int = 128
    min_height: int = 128
    max_width: int = 8192
    max_height: int = 8192
    max_aspect_ratio: float = 4.0
    min_quality_score: float = 0.50


def _percentile_bounds(values: np.ndarray, low: float = 1.0, high: float = 99.0) -> tuple[float, float]:
    return float(np.percentile(values, low)), float(np.percentile(values, high))


def image_features(image: Image.Image) -> dict[str, float]:
    rgb = np.asarray(image.convert("RGB").resize((256, 256)), dtype=np.float32) / 255.0
    luma = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    gx = np.diff(luma, axis=1)
    gy = np.diff(luma, axis=0)
    gradient = np.sqrt(np.pad(gx, ((0, 0), (0, 1))) ** 2 + np.pad(gy, ((0, 1), (0, 0))) ** 2)
    center = luma[64:192, 64:192]
    values = {
        "aspect_ratio": float(image.width / max(image.height, 1)),
        "mean_red": float(rgb[..., 0].mean()),
        "mean_green": float(rgb[..., 1].mean()),
        "mean_blue": float(rgb[..., 2].mean()),
        "std_red": float(rgb[..., 0].std()),
        "std_green": float(rgb[..., 1].std()),
        "std_blue": float(rgb[..., 2].std()),
        "mean_luma": float(luma.mean()),
        "std_luma": float(luma.std()),
        "sharpness": float((gx.var() + gy.var()) / 2.0),
        "edge_strength": float(gradient.mean()),
        "dark_fraction": float((luma < 0.08).mean()),
        "bright_fraction": float((luma > 0.95).mean()),
        "center_luma": float(center.mean()),
        "center_std": float(center.std()),
    }
    return values


def feature_vector(features: dict[str, float]) -> np.ndarray:
    return np.asarray([features[name] for name in FEATURE_NAMES], dtype=np.float64)


def _robust_distance(vector: np.ndarray, center: np.ndarray, scale: np.ndarray) -> float:
    z = (vector - center) / np.maximum(scale, 1e-6)
    return float(np.sqrt(np.mean(np.square(z))))


def quality_score_from_features(features: dict[str, float]) -> float:
    components = [
        min(features["edge_strength"] / 0.08, 1.0),
        min(features["std_luma"] / 0.25, 1.0),
        1.0 - min(abs(features["mean_luma"] - 0.5) / 0.5, 1.0),
    ]
    return float(np.clip(np.mean(components), 0.0, 1.0))


def build_reference(feature_rows: list[dict[str, float]], validation_rows: list[dict[str, float]]) -> dict[str, Any]:
    train_matrix = np.stack([feature_vector(row) for row in feature_rows])
    validation_matrix = np.stack([feature_vector(row) for row in validation_rows])
    center = np.median(train_matrix, axis=0)
    scale = np.maximum(np.subtract(*np.percentile(train_matrix, [75, 25], axis=0)) / 1.349, 1e-4)
    validation_distances = np.asarray([_robust_distance(row, center, scale) for row in validation_matrix])
    train_quality_scores = np.asarray([quality_score_from_features(row) for row in feature_rows])
    bounds = {
        name: list(_percentile_bounds(train_matrix[:, index], 1.0, 99.0))
        for index, name in enumerate(FEATURE_NAMES)
    }
    return {
        "dataset": "HAM10000",
        "feature_names": list(FEATURE_NAMES),
        "center": center.tolist(),
        "scale": scale.tolist(),
        "ood_threshold": float(np.percentile(validation_distances, 99.5)),
        "quality_threshold": float(np.percentile(train_quality_scores, 1.0)),
        "quality_score_summary": {
            "p01": float(np.percentile(train_quality_scores, 1)),
            "p50": float(np.percentile(train_quality_scores, 50)),
            "p99": float(np.percentile(train_quality_scores, 99)),
        },
        "validation_distance_summary": {
            "p50": float(np.percentile(validation_distances, 50)),
            "p95": float(np.percentile(validation_distances, 95)),
            "p99": float(np.percentile(validation_distances, 99)),
            "max": float(validation_distances.max()),
        },
        "quality_bounds": bounds,
        "validation_sample_count": int(len(validation_rows)),
    }


def load_reference(path: str | Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    reference_path = Path(path)
    if not reference_path.exists():
        return None
    return json.loads(reference_path.read_text(encoding="utf-8"))


def validate_image(
    image_path: str | Path,
    reference_path: str | Path | None = None,
    config: QualityConfig | None = None,
    require_reference: bool = False,
) -> dict[str, Any]:
    config = config or QualityConfig()
    path = Path(image_path)
    reasons: list[str] = []
    warnings: list[str] = []
    if not path.exists() or not path.is_file():
        return {"accepted": False, "status": "rejected", "reasons": ["file_not_found"], "warnings": []}
    try:
        with Image.open(path) as image:
            image.load()
            width, height = image.size
            features = image_features(image)
    except (UnidentifiedImageError, OSError, ValueError):
        return {"accepted": False, "status": "rejected", "reasons": ["invalid_or_corrupt_image"], "warnings": []}

    if width < config.min_width or height < config.min_height:
        reasons.append("resolution_below_minimum")
    if width > config.max_width or height > config.max_height:
        reasons.append("resolution_above_maximum")
    if features["aspect_ratio"] > config.max_aspect_ratio or features["aspect_ratio"] < 1.0 / config.max_aspect_ratio:
        reasons.append("extreme_aspect_ratio")
    if features["sharpness"] <= 0.0 or features["edge_strength"] <= 0.002:
        reasons.append("insufficient_visual_detail")
    if features["mean_luma"] < 0.03:
        reasons.append("underexposed")
    if features["mean_luma"] > 0.97:
        reasons.append("overexposed")
    if features["std_luma"] < 0.015:
        reasons.append("near_uniform_image")

    reference = load_reference(reference_path)
    ood_score: float | None = None
    ood_threshold: float | None = None
    if reference is not None:
        vector = feature_vector(features)
        center = np.asarray(reference["center"], dtype=np.float64)
        scale = np.asarray(reference["scale"], dtype=np.float64)
        ood_score = _robust_distance(vector, center, scale)
        ood_threshold = float(reference["ood_threshold"])
        if ood_score > ood_threshold:
            reasons.append("outside_dermoscopy_domain")
        for name, bounds in reference.get("quality_bounds", {}).items():
            value = features.get(name)
            if value is None:
                continue
            if value < float(bounds[0]) or value > float(bounds[1]):
                warnings.append(f"feature_outside_reference:{name}")
    else:
        if require_reference:
            reasons.append("domain_reference_missing")
        else:
            warnings.append("domain_reference_not_configured")

    quality_score = quality_score_from_features(features)
    quality_threshold = float(reference.get("quality_threshold", config.min_quality_score)) if reference is not None else config.min_quality_score
    if quality_score < quality_threshold:
        reasons.append("quality_score_below_minimum")
    accepted = not reasons
    return {
        "accepted": accepted,
        "status": "accepted" if accepted else "rejected",
        "reasons": sorted(set(reasons)),
        "warnings": sorted(set(warnings)),
        "width": width,
        "height": height,
        "quality_score": round(quality_score, 6),
        "ood_score": None if ood_score is None else round(ood_score, 6),
        "ood_threshold": ood_threshold,
        "features": {key: round(float(value), 8) for key, value in features.items()},
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Triagem de qualidade e domínio de imagem")
    parser.add_argument("--image", required=True)
    parser.add_argument("--reference")
    parser.add_argument("--require-reference", action="store_true")
    args = parser.parse_args()
    print(json.dumps(validate_image(args.image, args.reference, require_reference=args.require_reference), ensure_ascii=False))


if __name__ == "__main__":
    main()
