from __future__ import annotations

import numpy as np

from ml.evaluate_external import binary_metrics


def test_binary_metrics_reports_confusion_calibration_and_abstention() -> None:
    report = binary_metrics(
        y_true=[0, 0, 1, 1],
        probabilities=[0.10, 0.40, 0.60, 0.90],
        abstain=[False, True, False, False],
    )

    assert report["support"] == 4
    assert report["confusion_matrix"] == {"tn": 2, "fp": 0, "fn": 0, "tp": 2}
    assert report["accuracy"] == 1.0
    assert report["specificity"] == 1.0
    assert report["recall_sensitivity"] == 1.0
    assert report["abstention_rate"] == 0.25
    assert report["auroc"] == 1.0


def test_binary_metrics_does_not_invent_auroc_for_single_class() -> None:
    report = binary_metrics(y_true=[1, 1], probabilities=[0.51, 0.80])

    assert report["support"] == 2
    assert report["auroc"] is None
    assert report["auprc"] is None
    assert report["status"] == "single_class"


def test_ece_is_bounded() -> None:
    report = binary_metrics(y_true=[0, 1, 0, 1], probabilities=[0.1, 0.9, 0.2, 0.8])

    assert 0.0 <= report["ece"] <= 1.0
    assert np.isfinite(report["ece"])
