from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
metrics_path = ROOT / "ml_artifacts" / "ham10000" / "ensemble" / "test_metrics.json"
out_path = ROOT / "docs" / "experiments" / "model_comparison_test_metrics.png"

with metrics_path.open(encoding="utf-8") as handle:
    payload = json.load(handle)

models = ["CNN ResNet-50", "ViT", "Híbrido CNN–ViT", "Ensemble"]
keys = ["auroc", "sensitivity", "specificity", "f1"]
labels = ["AUROC", "Sensibilidade", "Especificidade", "Macro-F1"]
colors = ["#2563eb", "#059669", "#d97706", "#7c3aed"]
values = []
for model in ["cnn", "vit", "hybrid"]:
    binary = payload["component_test_metrics"][model]["binary"]
    multiclass = payload["component_test_metrics"][model]["multiclass"]
    values.append([binary["auroc"], binary["sensitivity"], binary["specificity"], multiclass["macro_f1"]])
ensemble_binary = payload["ensemble_test_metrics"]["binary"]
ensemble_multiclass = payload["ensemble_test_metrics"]["multiclass"]
values.append([ensemble_binary["auroc"], ensemble_binary["sensitivity"], ensemble_binary["specificity"], ensemble_multiclass["macro_f1"]])

values = np.asarray(values) * 100
x = np.arange(len(labels))
width = 0.19
fig, ax = plt.subplots(figsize=(11, 6.5), dpi=180)
for index, (model, color) in enumerate(zip(models, colors)):
    offset = (index - 1.5) * width
    bars = ax.bar(x + offset, values[index], width, label=model, color=color, alpha=0.9)
    ax.bar_label(bars, fmt="%.1f", padding=2, fontsize=7, rotation=90)

ax.set_ylim(0, 100)
ax.set_ylabel("Percentual")
ax.set_title("Comparação no conjunto de teste congelado (n=1.527)", pad=14, weight="bold")
ax.set_xticks(x, labels)
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False)
fig.text(0.01, 0.01, "AUROC/sensibilidade/especificidade: tarefa binária; Macro-F1: tarefa multiclasses.", fontsize=8, color="#475569")
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(out_path, bbox_inches="tight")
print(out_path)
