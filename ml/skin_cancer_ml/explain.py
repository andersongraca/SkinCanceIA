from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import os
import sys

import cv2
import numpy as np
import torch
from PIL import Image

from .data import build_transforms
from .infer import load_model
from .lesion_segmentation import predict_lesion_mask, segmentation_sensitivity_config
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


def _input_gradient(tensor: torch.Tensor, image_size: int) -> np.ndarray:
    if tensor.grad is None:
        raise RuntimeError("Gradiente da entrada não disponível")
    gradients = tensor.grad.detach().abs().mean(dim=1)[0].cpu().numpy()
    return _resize_map(gradients, image_size, image_size)


def _non_uniform_or_input_gradient(
    token_map: np.ndarray,
    tensor: torch.Tensor,
    image_size: int,
) -> np.ndarray:
    if float(token_map.std()) < 1e-4:
        return _input_gradient(tensor, image_size)
    return token_map


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


def _load_lesion_gate(image: Image.Image, image_size: int, device: torch.device) -> tuple[np.ndarray | None, dict[str, Any]]:
    configured = os.environ.get("ML_LESION_SEGMENTER_CHECKPOINT")
    root = Path(os.environ.get("ML_PROJECT_ROOT", "."))
    checkpoint = Path(configured) if configured else root / "ml_artifacts" / "isic2016_segmentation" / "lesion_segmentation.pt"
    if not checkpoint.exists():
        return None, {"available": False, "reason": "lesion_segmenter_checkpoint_missing"}
    try:
        sensitivity = segmentation_sensitivity_config()
        mask, metadata = predict_lesion_mask(image, checkpoint, device, float(sensitivity["threshold"]))
        mask = cv2.resize(mask, (image_size, image_size), interpolation=cv2.INTER_NEAREST)
        components, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
        if components > 1:
            largest_label = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
            mask = (labels == largest_label).astype(np.float32)
        mask_uint8 = (mask * 255).astype(np.uint8)
        kernel = int(sensitivity["kernel"])
        mask_uint8 = cv2.morphologyEx(mask_uint8, cv2.MORPH_CLOSE, np.ones((kernel, kernel), dtype=np.uint8))
        mask = (mask_uint8 > 127).astype(np.float32)
        area = float(mask.mean())
        if area < float(sensitivity["minArea"]) or area > float(sensitivity["maxArea"]):
            return None, {"available": False, "reason": "lesion_mask_area_invalid", **metadata, "sensitivity": sensitivity}
        return mask, {"available": True, **metadata, "sensitivity": sensitivity, "postprocessedAreaFraction": area}
    except Exception as error:
        return None, {"available": False, "reason": f"lesion_segmenter_failed:{type(error).__name__}"}


def _restrict_to_lesion(values: np.ndarray, lesion_mask: np.ndarray | None) -> np.ndarray:
    if lesion_mask is None:
        return values
    restricted = values * np.where(lesion_mask > 0.5, 1.0, 0.03)
    return _normalize(restricted)


def generate_heatmap(checkpoint_path: str | Path, image_path: str | Path, output_path: str | Path, target: int | None = None) -> dict[str, Any]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, config, _ = load_model(checkpoint_path, device)
    with Image.open(image_path) as source:
        source = source.convert("RGB")
        original = np.asarray(source.resize((config.image_size, config.image_size)), dtype=np.float32)
        tensor = build_transforms(config.image_size, train=False)(source).unsqueeze(0).to(device)
        tensor.requires_grad_(True)
    output = model(tensor)
    binary_logit = output.binary_logits.reshape(-1)[:1]
    if target is None:
        target = int(output.class_logits.argmax(dim=1).item())
    # Explain the same binary decision shown by infer.py, rather than the
    # auxiliary seven-class head.  Flip the score for benign predictions so
    # positive attribution always means evidence for the displayed decision.
    binary_target = "malignant" if float(binary_logit.item()) >= 0.0 else "benign"
    score = binary_logit if binary_target == "malignant" else -binary_logit
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

    lesion_mask, segmentation = _load_lesion_gate(source, config.image_size, device)
    sensitivity = segmentation.get("sensitivity", {})
    print(
        "[XAI:segmentation] "
        f"available={segmentation.get('available', False)} "
        f"mode={sensitivity.get('mode', 'n/a')} "
        f"threshold={sensitivity.get('threshold', 'n/a')} "
        f"kernel={sensitivity.get('kernel', 'n/a')}x{sensitivity.get('kernel', 'n/a')} "
        f"area={segmentation.get('postprocessedAreaFraction', segmentation.get('areaFraction', 'n/a'))}",
        file=sys.stderr,
        flush=True,
    )
    maps: dict[str, np.ndarray] = {}
    if isinstance(model, CNNModel):
        maps["gradcam"] = _restrict_to_lesion(
            _resize_map(_gradcam(model.last_feature_map), config.image_size, config.image_size), lesion_mask
        )
    elif isinstance(model, ViTModel):
        maps["token_gradient"] = _restrict_to_lesion(
            _non_uniform_or_input_gradient(_token_attribution(model.last_tokens, config.image_size), tensor, config.image_size),
            lesion_mask,
        )
    elif isinstance(model, HybridModel):
        cnn_map = _resize_map(_gradcam(model.last_feature_map), config.image_size, config.image_size)
        token_map = _non_uniform_or_input_gradient(
            _token_attribution(model.last_tokens, config.image_size), tensor, config.image_size
        )
        attention_map = _attention_rollout(model.last_attentions, config.image_size)
        gate = float(output.aux["gate"].detach().mean().cpu())
        maps["cnn_gradcam"] = _restrict_to_lesion(cnn_map, lesion_mask)
        maps["vit_token_gradient"] = _restrict_to_lesion(token_map, lesion_mask)
        maps["attention_rollout"] = _restrict_to_lesion(attention_map, lesion_mask)
        maps["hybrid"] = _restrict_to_lesion(
            _normalize(gate * cnn_map + (1.0 - gate) * 0.5 * (token_map + attention_map)), lesion_mask
        )
    else:
        raise TypeError(f"Modelo sem suporte a XAI: {type(model).__name__}")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    for name, heatmap in maps.items():
        saliency_path = output_path.with_name(f"{output_path.stem}_{name}_saliency.png")
        overlay_path = output_path.with_name(f"{output_path.stem}_{name}.png")
        Image.fromarray(np.uint8(np.clip(heatmap, 0.0, 1.0) * 255)).save(saliency_path)
        Image.fromarray(_overlay(original, heatmap)).save(overlay_path)
        written[name] = str(overlay_path)
        written[f"{name}_saliency"] = str(saliency_path)
    return {
        "targetClass": binary_target,
        "fineGrainedTargetClass": config.classes[target],
        "method": list(maps),
        "paths": written,
        "segmentation": segmentation,
    }


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
