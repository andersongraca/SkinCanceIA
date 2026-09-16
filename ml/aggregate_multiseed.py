from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, stdev
from typing import Any


METRICS = (
    ("binary", "auroc"),
    ("binary", "auprc"),
    ("binary", "sensitivity"),
    ("binary", "specificity"),
    ("binary", "f1"),
    ("binary", "mcc"),
    ("multiclass", "macro_f1"),
    ("multiclass", "auroc_macro_ovr"),
    ("multiclass", "auprc_macro_ovr"),
    ("multiclass", "ece"),
    ("multiclass", "brier"),
)


def summarize(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"n": 0, "mean": None, "sd": None, "min": None, "max": None}
    return {
        "n": len(values),
        "mean": mean(values),
        "sd": stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def aggregate(root: str | Path, output: str | Path) -> dict[str, Any]:
    root_path = Path(root)
    reports: list[dict[str, Any]] = []
    for report_path in sorted(root_path.glob("seed-*/ensemble/test_metrics.json")):
        report = json.loads(report_path.read_text(encoding="utf-8"))
        seed_name = report_path.parents[1].name
        metrics = report.get("ensemble_test_metrics", {})
        reports.append({"seed": seed_name.removeprefix("seed-"), "report": str(report_path), "sample_count": report.get("test_sample_count"), "metrics": metrics})

    summary: dict[str, Any] = {
        "root": str(root_path),
        "seed_count": len(reports),
        "runs": reports,
        "aggregate": {},
    }
    for section, metric_name in METRICS:
        values = []
        for item in reports:
            value = item["metrics"].get(section, {}).get(metric_name)
            if isinstance(value, (int, float)):
                values.append(float(value))
        summary["aggregate"][f"{section}.{metric_name}"] = summarize(values)

    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Agrega métricas do ensemble em rodadas multi-semente")
    parser.add_argument("--root", required=True, help="Diretório com subdiretórios seed-*/ensemble")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    aggregate(args.root, args.output)


if __name__ == "__main__":
    main()
