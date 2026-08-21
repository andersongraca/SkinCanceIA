"""Gera um mapa de saliência agregado para o Ensemble Learning.

O ensemble é uma combinação ponderada das saliências dos mapas CNN, ViT e híbrido,
com os mesmos pesos selecionados na validação. O resultado é uma explicação
aproximada da decisão e não uma segmentação clínica.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.cm as cm
import numpy as np
from PIL import Image


def normalize(array: np.ndarray) -> np.ndarray:
    low = float(array.min())
    high = float(array.max())
    if high - low < 1e-8:
        return np.zeros_like(array, dtype=np.float32)
    return ((array - low) / (high - low)).astype(np.float32)


def load_saliency(path: Path, size: tuple[int, int]) -> np.ndarray:
    image = Image.open(path).convert("RGB").resize(size, Image.Resampling.BILINEAR)
    rgb = np.asarray(image, dtype=np.float32) / 255.0
    return normalize(rgb.mean(axis=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera heatmap ponderado do ensemble CNN/ViT/híbrido.")
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--cnn", required=True, type=Path)
    parser.add_argument("--vit", required=True, type=Path)
    parser.add_argument("--hybrid", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--weights", required=True, type=Path)
    args = parser.parse_args()

    original = Image.open(args.image).convert("RGB")
    size = original.size
    weights_payload = json.loads(args.weights.read_text(encoding="utf-8"))
    raw_weights = [
        float(weights_payload["cnn"]),
        float(weights_payload["vit"]),
        float(weights_payload["hybrid"]),
    ]
    total = sum(raw_weights)
    if total <= 0:
        raise ValueError("Os pesos do ensemble devem somar um valor positivo.")
    weights = [weight / total for weight in raw_weights]

    component_paths = [args.cnn, args.vit, args.hybrid]
    saliency = sum(
        weight * load_saliency(component_path, size)
        for weight, component_path in zip(weights, component_paths)
    )
    saliency = normalize(saliency)
    heatmap_rgb = (cm.turbo(saliency)[..., :3] * 255.0).astype(np.uint8)
    heatmap = Image.fromarray(heatmap_rgb, mode="RGB")
    overlay = Image.blend(original, heatmap, alpha=0.56)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(args.output, format="PNG", optimize=True)
    print(json.dumps({
        "targetClass": "ensemble",
        "method": ["weighted_component_saliency", "cnn", "vit", "hybrid"],
        "path": str(args.output.resolve()),
        "weights": {"cnn": weights[0], "vit": weights[1], "hybrid": weights[2]},
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
