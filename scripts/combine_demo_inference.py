from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
input_path = ROOT / "ml_artifacts/ham10000/demo_validation/inference_results.jsonl"
weights_path = ROOT / "ml_artifacts/ham10000/ensemble/weights.json"
output_path = ROOT / "ml_artifacts/ham10000/demo_validation/ensemble_result.json"

raw_lines = [line.strip() for line in input_path.read_text(encoding="utf-8").splitlines() if line.strip()]
records: list[dict[str, object]] = []
line_index = 0
while line_index < len(raw_lines):
    candidate = raw_lines[line_index]
    if line_index + 1 < len(raw_lines) and raw_lines[line_index + 1] == "}":
        candidate += "}"
        line_index += 1
    records.append(json.loads(candidate))
    line_index += 1
weights = json.loads(weights_path.read_text(encoding="utf-8"))
weight_sum = sum(float(weights[record["model"]]) for record in records)
if weight_sum <= 0:
    raise ValueError("Os pesos do ensemble devem somar um valor positivo.")

binary = {"benign": 0.0, "malignant": 0.0}
fine: dict[str, float] = {}
malignant_components: list[float] = []
tta_variances: list[float] = []
for record in records:
    result = record["result"]
    weight = float(weights[record["model"]]) / weight_sum
    for label, probability in result["probabilities"].items():
        binary[label] = binary.get(label, 0.0) + weight * float(probability)
    for label, probability in result["fineGrainedProbabilities"].items():
        fine[label] = fine.get(label, 0.0) + weight * float(probability)
    malignant_components.append(float(result["probabilities"]["malignant"]))
    tta_variances.append(float(result["uncertainty"]["ttaVariance"]))

fine_class = max(fine, key=fine.get)
malignant_probability = binary["malignant"]
mean_component = sum(malignant_components) / len(malignant_components)
model_disagreement_variance = sum((value - mean_component) ** 2 for value in malignant_components) / len(malignant_components)
probability_entropy = -sum(value * math.log(max(value, 1e-12)) for value in binary.values())
ensemble = {
    "classification": "malignant" if malignant_probability >= 0.5 else "benign",
    "confidence": round(max(binary.values()) * 100.0, 4),
    "probabilities": {key: round(value, 8) for key, value in binary.items()},
    "fineGrainedClass": fine_class,
    "fineGrainedProbabilities": {key: round(value, 8) for key, value in fine.items()},
    "uncertainty": {
        "predictiveEntropy": probability_entropy,
        "meanTtaVariance": sum(tta_variances) / len(tta_variances),
        "modelDisagreementVariance": model_disagreement_variance,
        "abstain": any(record["result"]["uncertainty"]["abstain"] for record in records),
    },
    "weights": weights,
    "source": "validation_selected_weights",
}
output_path.write_text(json.dumps(ensemble, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(ensemble, indent=2, ensure_ascii=False))
