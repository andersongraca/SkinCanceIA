from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse

import cv2
import numpy as np
import torch
from PIL import Image

from .data import build_transforms
from .infer import load_model
from .models import CNNModel, HybridModel, ViTModel


def _normalize(values: np.ndarray) -> np.ndarray:
    values = np.maximum(values, 0.0)
    low, high = float(values.min()), float(values.max())
    if high - low < 1e-8:
        return np.zeros_like(values, dtype=np.float32)
    return ((values - low) / (high - low)).astype(np.float32)


def _resize_map(values: np.ndarray, height: int, width: int) -> np.ndarray:
    return cv2.resize(_normalize(values), (width, height), interpolation=cv2.INTER_CUBIC)


def _gradcam(feature_map: torch.Tensor) -> np.ndarray:
    if feature_map.grad is None:
        raise RuntimeError("Gradiente do mapa convolucional não disponível")
    gradients = feature_map.grad.detach()
    activations = feature_map.detach()
    weights = gradients.mean(dim=(2, 3), keepdim=True)
    heatmap = torch.relu((weights * activations).sum(dim=1))[0].cpu().numpy()
    return _normalize(heatmap)


def _token_attribution(tokens: torch.Tensor, image_size: int) -> np.ndarray:
    if tokens.grad is None:
        raise RuntimeError("Gradiente dos tokens não disponível")
    token_values = tokens.detach()[:, 1:]
    token_gradients = tokens.grad.detach()[:, 1:]
    attribution = (token_values * token_gradients).sum(dim=-1).abs()[0]
    grid = int(np.sqrt(attribution.numel()))
    if grid * grid != attribution.numel():
        raise RuntimeError("Número de tokens incompatível com um mapa quadrado")
    return _resize_map(attribution.reshape(grid, grid).cpu().numpy(), image_size, image_size)


def _attention_rollout(attentions: list[torch.Tensor], image_size: int) -> np.ndarray:
    if not attentions:
        return np.zeros((image_size, image_size), dtype=np.float32)
    result: torch.Tensor | None = None
    for attention in attentions:
        matrix = attention.detach().mean(dim=1)[0]
        identity = torch.eye(matrix.shape[-1], device=matrix.device)
        matrix = matrix + identity
        matrix = matrix / matrix.sum(dim=-1, keepdim=True).clamp_min(1e-8)
        result = matrix if result is None else matrix @ result
    assert result is not None
    cls_to_patch = result[0, 1:]
    grid = int(np.sqrt(cls_to_patch.numel()))
    return _resize_map(cls_to_patch.reshape(grid, grid).cpu().numpy(), image_size, image_size)


def _overlay(image: np.ndarray, heatmap: np.ndarray) -> np.ndarray:
    heatmap_uint8 = np.uint8(np.clip(heatmap, 0.0, 1.0) * 255)
    colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    colored = cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)
    return np.uint8(np.clip(0.55 * image + 0.45 * colored, 0, 255))


def generate_heatmap(checkpoint_path: str | Path, image_path: str | Path, output_path: str | Path, target: int | None = None) -> dict[str, Any]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, config, _ = load_model(checkpoint_path, device)
    with Image.open(image_path) as source:
        source = source.convert("RGB")
        original = np.asarray(source.resize((config.image_size, config.image_size)), dtype=np.float32)
        tensor = build_transforms(config.image_size, train=False)(source).unsqueeze(0).to(device)
    output = model(tensor)
    if target is None:
        target = int(output.class_logits.argmax(dim=1).item())
    score = output.class_logits[:, target].sum()
    model.zero_grad(set_to_none=True)
    if isinstance(model, CNNModel):
        assert model.last_feature_map is not None
        model.last_feature_map.retain_grad()
    if isinstance(model, ViTModel):
        assert model.last_tokens is not None
        model.last_tokens.retain_grad()
    if isinstance(model, HybridModel):
        assert model.last_feature_map is not None and model.last_tokens is not None
        model.last_feature_map.retain_grad()
        model.last_tokens.retain_grad()
    score.backward()

    maps: dict[str, np.ndarray] = {}
    if isinstance(model, CNNModel):
        maps["gradcam"] = _resize_map(_gradcam(model.last_feature_map), config.image_size, config.image_size)
    elif isinstance(model, ViTModel):
        maps["token_gradient"] = _token_attribution(model.last_tokens, config.image_size)
    elif isinstance(model, HybridModel):
        cnn_map = _resize_map(_gradcam(model.last_feature_map), config.image_size, config.image_size)
        token_map = _token_attribution(model.last_tokens, config.image_size)
        attention_map = _attention_rollout(model.last_attentions, config.image_size)
        gate = float(output.aux["gate"].detach().mean().cpu())
        maps["cnn_gradcam"] = cnn_map
        maps["vit_token_gradient"] = token_map
        maps["attention_rollout"] = attention_map
        maps["hybrid"] = _normalize(gate * cnn_map + (1.0 - gate) * 0.5 * (token_map + attention_map))
    else:
        raise TypeError(f"Modelo sem suporte a XAI: {type(model).__name__}")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    for name, heatmap in maps.items():
        path = output_path.with_name(f"{output_path.stem}_{name}.png")
        Image.fromarray(_overlay(original, heatmap)).save(path)
        written[name] = str(path)
    return {"targetClass": config.classes[target], "method": list(maps), "paths": written}


def main() -> None:
    parser = argparse.ArgumentParser(description="Geração de mapas de explicabilidade")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--target", type=int)
    args = parser.parse_args()
    import json
    print(json.dumps(generate_heatmap(args.checkpoint, args.image, args.output, args.target), ensure_ascii=False))


if __name__ == "__main__":
    main()
