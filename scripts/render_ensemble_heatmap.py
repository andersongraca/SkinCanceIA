from __future__ import annotations

import json
from pathlib import Path

import matplotlib.cm as cm
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "ml_artifacts/ham10000/demo_validation"
XAI = DEMO / "xai"
OUT = DEMO / "jpg"
OUT.mkdir(parents=True, exist_ok=True)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD_PATH if bold else FONT_PATH, size)


def normalize(array: np.ndarray) -> np.ndarray:
    low = float(array.min())
    high = float(array.max())
    if high - low < 1e-8:
        return np.zeros_like(array, dtype=np.float32)
    return ((array - low) / (high - low)).astype(np.float32)


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.contain(image.convert("RGB"), size, method=Image.Resampling.LANCZOS)


def panel(image: Image.Image, title: str, size: tuple[int, int], border: tuple[int, int, int]) -> Image.Image:
    canvas = Image.new("RGB", size, (20, 24, 32))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, size[0] - 1, size[1] - 1), outline=border, width=4)
    draw.text((26, 18), title, fill=(245, 247, 250), font=font(30, True))
    fitted = fit(image, (size[0] - 48, size[1] - 88))
    x = (size[0] - fitted.width) // 2
    y = 70 + (size[1] - 88 - fitted.height) // 2
    canvas.paste(fitted, (x, y))
    return canvas


weights = json.loads((ROOT / "ml_artifacts/ham10000/ensemble/weights.json").read_text(encoding="utf-8"))
map_paths = {
    "cnn": XAI / "cnn_gradcam_gradcam.png",
    "vit": XAI / "vit_token_gradient_token_gradient.png",
    "hybrid": XAI / "hybrid_combined_hybrid.png",
}
weight_sum = sum(float(weights[name]) for name in map_paths)
if weight_sum <= 0:
    raise ValueError("Os pesos do ensemble devem somar um valor positivo.")

weighted_saliency = None
for name, path in map_paths.items():
    image = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    luminance = image.mean(axis=2)
    normalized = normalize(luminance)
    weight = float(weights[name]) / weight_sum
    weighted_saliency = normalized * weight if weighted_saliency is None else weighted_saliency + normalized * weight
weighted_saliency = normalize(weighted_saliency)

heatmap_rgb = (cm.turbo(weighted_saliency)[..., :3] * 255.0).astype(np.uint8)
heatmap = Image.fromarray(heatmap_rgb, mode="RGB")
original = Image.open(ROOT / "data/raw/images/ISIC_0024339.jpg").convert("RGB").resize(heatmap.size, Image.Resampling.LANCZOS)
overlay = Image.blend(original, heatmap, alpha=0.56)
raw_path = DEMO / "xai" / "ensemble_weighted_saliency.png"
heatmap.save(raw_path)

canvas = Image.new("RGB", (1800, 1050), (13, 17, 23))
draw = ImageDraw.Draw(canvas)
draw.text((50, 34), "Ensemble Learning — heatmap agregado", fill=(245, 247, 250), font=font(42, True))
draw.text((50, 94), "Média ponderada das saliências da CNN, ViT e híbrido; pesos selecionados na validação.", fill=(177, 188, 202), font=font(23))
canvas.paste(panel(original, "Imagem original", (820, 690), (70, 120, 210)), (50, 160))
canvas.paste(panel(overlay, "Ensemble — mapa agregado", (820, 690), (126, 202, 164)), (930, 160))
draw.rounded_rectangle((50, 875, 1750, 985), radius=16, fill=(27, 34, 46), outline=(70, 80, 96), width=2)
draw.text((82, 900), "Pesos: CNN 10%   |   ViT 50%   |   Híbrido 40%", fill=(126, 202, 164), font=font(25, True))
draw.text((82, 940), "Interpretação: saliência agregada aproximada; não é segmentação clínica nem prova de causalidade.", fill=(205, 214, 226), font=font(21))

jpg_path = OUT / "ensemble_learning_heatmap.jpg"
png_path = OUT / "ensemble_learning_heatmap.png"
canvas.save(jpg_path, quality=94, optimize=True)
canvas.save(png_path, optimize=True)
print(json.dumps({"jpg": str(jpg_path), "png": str(png_path), "raw_saliency": str(raw_path), "weights": weights}, ensure_ascii=False, indent=2))
