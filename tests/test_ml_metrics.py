import numpy as np

from ml.skin_cancer_ml.metrics import classification_metrics


def test_per_class_metrics_report_support_and_rare_class():
    labels = np.array([0, 0, 1, 2, 2, 2])
    probabilities = np.array([
        [0.90, 0.08, 0.02],
        [0.60, 0.30, 0.10],
        [0.10, 0.80, 0.10],
        [0.10, 0.20, 0.70],
        [0.20, 0.50, 0.30],
        [0.10, 0.20, 0.70],
    ])
    binary_labels = np.array([0, 0, 1, 1, 1, 1])
    binary_probability = np.array([0.1, 0.2, 0.7, 0.8, 0.6, 0.9])

    result = classification_metrics(
        labels,
        probabilities,
        binary_labels,
        binary_probability,
        class_names=["akiec", "bcc", "df"],
    )

    per_class = result["multiclass"]["per_class"]
    assert per_class["akiec"]["support"] == 2
    assert per_class["bcc"]["support"] == 1
    assert per_class["df"]["support"] == 3
    assert all("f1" in per_class[name] for name in ("akiec", "bcc", "df"))
    assert result["binary"]["ece"] <= 1.0
