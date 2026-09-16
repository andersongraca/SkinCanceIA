from __future__ import annotations

from pathlib import Path
from typing import Any
import os

import numpy as np
import torch
from PIL import Image
from torch import nn
from torchvision.transforms import functional as TF


class _Block(nn.Module):
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class LesionSegmenter(nn.Module):
    def __init__(self):
        super().__init__()
        self.enc1 = _Block(3, 16)
        self.enc2 = _Block(16, 32)
        self.enc3 = _Block(32, 64)
        self.bottleneck = _Block(64, 96)
        self.pool = nn.MaxPool2d(2)
        self.up3 = nn.ConvTranspose2d(96, 64, 2, stride=2)
        self.dec3 = _Block(128, 64)
        self.up2 = nn.ConvTranspose2d(64, 32, 2, stride=2)
        self.dec2 = _Block(64, 32)
        self.up1 = nn.ConvTranspose2d(32, 16, 2, stride=2)
        self.dec1 = _Block(32, 16)
        self.out = nn.Conv2d(16, 1, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        b = self.bottleneck(self.pool(e3))
        d3 = self.dec3(torch.cat([self.up3(b), e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))
        return self.out(d1)


def load_segmenter(checkpoint_path: str | Path, device: torch.device) -> tuple[LesionSegmenter, int]:
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model = LesionSegmenter().to(device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    return model, int(checkpoint.get("image_size", 160))


def predict_lesion_mask(
    image: Image.Image,
    checkpoint_path: str | Path,
    device: torch.device,
    threshold: float = 0.5,
) -> tuple[np.ndarray, dict[str, Any]]:
    model, image_size = load_segmenter(checkpoint_path, device)
    image_rgb = image.convert("RGB")
    tensor = TF.to_tensor(TF.resize(image_rgb, [image_size, image_size], antialias=True)).unsqueeze(0).to(device)
    with torch.inference_mode():
        probability = torch.sigmoid(model(tensor))[0, 0].cpu().numpy()
    threshold = float(min(max(threshold, 0.05), 0.95))
    mask = (probability >= threshold).astype(np.float32)
    area = float(mask.mean())
    confidence = float(max(probability.mean(), 1.0 - probability.mean()))
    return mask, {
        "areaFraction": area,
        "meanProbability": float(probability.mean()),
        "confidence": confidence,
        "imageSize": image_size,
        "threshold": threshold,
    }


def segmentation_sensitivity_config() -> dict[str, float | str]:
    mode = os.environ.get("ML_LESION_GATE_MODE", "balanced").strip().lower()
    presets: dict[str, tuple[float, int, float, float]] = {
        "strict": (0.65, 3, 0.02, 0.80),
        "balanced": (0.50, 5, 0.01, 0.90),
        "permissive": (0.35, 7, 0.005, 0.95),
    }
    threshold, kernel, min_area, max_area = presets.get(mode, presets["balanced"])
    try:
        threshold = float(os.environ.get("ML_LESION_MASK_THRESHOLD", threshold))
        kernel = int(os.environ.get("ML_LESION_MORPH_KERNEL", kernel))
        min_area = float(os.environ.get("ML_LESION_MASK_MIN_AREA", min_area))
        max_area = float(os.environ.get("ML_LESION_MASK_MAX_AREA", max_area))
    except ValueError:
        pass
    kernel = max(1, min(kernel, 15))
    if kernel % 2 == 0:
        kernel += 1
    return {
        "mode": mode if mode in presets else "balanced",
        "threshold": min(max(threshold, 0.05), 0.95),
        "kernel": kernel,
        "minArea": min_area,
        "maxArea": max_area,
    }
