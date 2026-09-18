from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path('/home/ubuntu/work/SkinCanceIA/docs/chapter-system/screenshots')
out = root.parent / 'painel_testes_sistema.png'
items = [
    ('A. Upload', root / '02_upload_preview_ham10000.png'),
    ('B. Resultado', root / '04_result_full.png'),
    ('C. Métricas', root / '08_metrics_dashboard.png'),
    ('D. Rejeição OOD', root / '09_ood_rejection.png'),
]
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font = ImageFont.truetype(font_path, 30)
small = ImageFont.truetype(font_path, 22)
cell_w, cell_h = 900, 620
canvas = Image.new('RGB', (cell_w * 2, cell_h * 2), '#e5e7eb')
draw = ImageDraw.Draw(canvas)
for index, (label, path) in enumerate(items):
    image = Image.open(path).convert('RGB')
    image.thumbnail((cell_w - 36, cell_h - 92))
    x = (index % 2) * cell_w
    y = (index // 2) * cell_h
    draw.rounded_rectangle((x + 12, y + 12, x + cell_w - 12, y + cell_h - 12), radius=14, fill='white', outline='#cbd5e1', width=3)
    draw.text((x + 32, y + 28), label, fill='#0f172a', font=font)
    px = x + (cell_w - image.width) // 2
    py = y + 78 + (cell_h - 92 - image.height) // 2
    canvas.paste(image, (px, py))
canvas.save(out, quality=95)
print(out)
