from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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


def parse_wrapped_jsonl(path: Path) -> list[dict[str, Any]]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    records: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        candidate = lines[index]
        if index + 1 < len(lines) and lines[index + 1] == "}":
            candidate += "}"
            index += 1
        records.append(json.loads(candidate))
        index += 1
    return records


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.contain(image.convert("RGB"), size, method=Image.Resampling.LANCZOS)


def panel(image: Image.Image, title: str, size: tuple[int, int], border: tuple[int, int, int] = (60, 64, 74)) -> Image.Image:
    canvas = Image.new("RGB", size, (20, 24, 32))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, size[0] - 1, size[1] - 1), outline=border, width=3)
    draw.text((22, 16), title, fill=(245, 247, 250), font=font(28, True))
    fitted = fit(image, (size[0] - 40, size[1] - 80))
    x = (size[0] - fitted.width) // 2
    y = 62 + (size[1] - 80 - fitted.height) // 2
    canvas.paste(fitted, (x, y))
    return canvas


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width: int, line_height: int, fill: tuple[int, int, int], text_font: ImageFont.FreeTypeFont) -> int:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), trial, font=text_font)[2] <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    y = xy[1]
    for line in lines:
        draw.text((xy[0], y), line, fill=fill, font=text_font)
        y += line_height
    return y


def create_accepted_processing(inference: dict[str, Any], ensemble: dict[str, Any], source: Path) -> Path:
    canvas = Image.new("RGB", (1800, 1100), (13, 17, 23))
    draw = ImageDraw.Draw(canvas)
    draw.text((50, 35), "Resultado do processamento — imagem dermatoscópica aceita", fill=(245, 247, 250), font=font(42, True))
    draw.text((50, 92), "Teste local com HAM10000; saída destinada à validação do protótipo, não a diagnóstico clínico.", fill=(177, 188, 202), font=font(23))
    source_panel = panel(Image.open(source), "Imagem de entrada", (760, 590), (70, 120, 210))
    canvas.paste(source_panel, (50, 160))
    box = (850, 160, 1750, 750)
    draw.rounded_rectangle(box, radius=20, fill=(27, 34, 46), outline=(70, 120, 210), width=3)
    draw.text((890, 195), "Resultado do ensemble", fill=(245, 247, 250), font=font(32, True))
    y = 260
    lines = [
        ("Classificação", ensemble["classification"].upper()),
        ("Confiança", f"{ensemble['confidence']:.2f}%"),
        ("Classe predominante", ensemble["fineGrainedClass"]),
        ("Probabilidade benigna", f"{ensemble['probabilities']['benign'] * 100:.2f}%"),
        ("Probabilidade maligna", f"{ensemble['probabilities']['malignant'] * 100:.2f}%"),
        ("Abstenção", "não" if not ensemble["uncertainty"]["abstain"] else "sim"),
        ("Entropia preditiva", f"{ensemble['uncertainty']['predictiveEntropy']:.4f}"),
    ]
    for label, value in lines:
        draw.text((890, y), f"{label}:", fill=(166, 181, 201), font=font(23, True))
        draw.text((1230, y), value, fill=(240, 244, 248), font=font(25, True))
        y += 60
    draw.text((890, 675), "Pesos selecionados na validação", fill=(166, 181, 201), font=font(21, True))
    draw.text((890, 710), "CNN 10%   |   ViT 50%   |   Híbrido 40%", fill=(126, 202, 164), font=font(24, True))
    y = 795
    draw.text((50, y), "Saídas individuais", fill=(245, 247, 250), font=font(30, True))
    x = 50
    for model in ("cnn", "vit", "hybrid"):
        result = inference[model]
        text = f"{model.upper()}: {result['classification']} — {result['confidence']:.2f}% — {result['fineGrainedClass']}"
        draw.rounded_rectangle((x, y + 55, x + 530, y + 135), radius=14, fill=(27, 34, 46), outline=(70, 80, 96), width=2)
        draw.text((x + 20, y + 80), text, fill=(236, 239, 244), font=font(20, True))
        x += 570
    output = OUT / "accepted_processing_result.jpg"
    canvas.save(output, quality=93, optimize=True)
    return output


def create_heatmaps(source: Path) -> Path:
    names = [
        ("Imagem original", source),
        ("CNN — Grad-CAM", XAI / "cnn_gradcam_gradcam.png"),
        ("ViT — atribuição de tokens", XAI / "vit_token_gradient_token_gradient.png"),
        ("Híbrido — mapa combinado", XAI / "hybrid_combined_hybrid.png"),
    ]
    canvas = Image.new("RGB", (1800, 1300), (13, 17, 23))
    draw = ImageDraw.Draw(canvas)
    draw.text((50, 35), "Heatmaps de explicabilidade — mesma imagem aceita", fill=(245, 247, 250), font=font(40, True))
    draw.text((50, 92), "Os mapas indicam regiões de saliência aproximada; não são segmentações clínicas.", fill=(177, 188, 202), font=font(23))
    positions = [(50, 160), (920, 160), (50, 760), (920, 760)]
    borders = [(70, 120, 210), (226, 93, 93), (235, 180, 70), (126, 202, 164)]
    for (title, path), position, border in zip(names, positions, borders):
        canvas.paste(panel(Image.open(path), title, (830, 520), border), position)
    output = OUT / "accepted_heatmaps.jpg"
    canvas.save(output, quality=93, optimize=True)
    return output


def create_rejection(case: str, source: Path, quality: dict[str, Any]) -> Path:
    canvas = Image.new("RGB", (1600, 950), (13, 17, 23))
    draw = ImageDraw.Draw(canvas)
    label = "carro" if case == "ood_car" else "cabeça e cabelo"
    draw.text((50, 35), f"Triagem de imagem fora do domínio — {label}", fill=(245, 247, 250), font=font(40, True))
    image_panel = panel(Image.open(source), "Imagem enviada", (760, 650), (226, 93, 93))
    canvas.paste(image_panel, (50, 150))
    box = (850, 150, 1550, 800)
    draw.rounded_rectangle(box, radius=20, fill=(50, 25, 31), outline=(226, 93, 93), width=4)
    draw.text((900, 205), "IMAGEM REJEITADA", fill=(255, 130, 130), font=font(35, True))
    y = 295
    rows = [
        ("Status", "outside_dermoscopy_domain"),
        ("Aceita", "não"),
        ("Quality score", f"{quality['quality_score']:.4f}"),
        ("OOD score", f"{quality['ood_score']:.2f}"),
        ("Limite OOD", f"{quality['ood_threshold']:.2f}"),
    ]
    for key, value in rows:
        draw.text((900, y), f"{key}:", fill=(218, 188, 194), font=font(23, True))
        draw.text((1190, y), value, fill=(255, 238, 240), font=font(25, True))
        y += 68
    draw.text((900, y + 15), "A classificação e os heatmaps", fill=(218, 188, 194), font=font(22))
    draw.text((900, y + 50), "não são executados após a rejeição.", fill=(218, 188, 194), font=font(22))
    output = OUT / f"{case}_rejection_result.jpg"
    canvas.save(output, quality=93, optimize=True)
    return output


quality_records = {record["case"]: record["result"] for record in parse_wrapped_jsonl(DEMO / "quality_results.jsonl")}
inference_records = {record["model"]: record["result"] for record in parse_wrapped_jsonl(DEMO / "inference_results.jsonl")}
ensemble = json.loads((DEMO / "ensemble_result.json").read_text(encoding="utf-8"))
source_image = ROOT / "data/raw/images/ISIC_0024339.jpg"
outputs = [
    create_accepted_processing(inference_records, ensemble, source_image),
    create_heatmaps(source_image),
    create_rejection("ood_car", ROOT / "test_assets/ood/public_car_picryl.jpg", quality_records["ood_car"]),
    create_rejection("ood_head_hair", ROOT / "test_assets/ood/public_head_picryl.jpg", quality_records["ood_head_hair"]),
]
print("\n".join(str(path) for path in outputs))
