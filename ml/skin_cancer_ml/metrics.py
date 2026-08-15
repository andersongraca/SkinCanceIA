from __future__ import annotations

from typing import Any
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    precision_recall_fscore_support,
    roc_auc_score,
)


def expected_calibration_error(probabilities: np.ndarray, labels: np.ndarray, bins: int = 15) -> float:
    probabilities = np.asarray(probabilities, dtype=float)
    labels = np.asarray(labels, dtype=int)
    if probabilities.ndim == 2:
        confidence = probabilities.max(axis=1)
        prediction = probabilities.argmax(axis=1)
        correctness = (prediction == labels).astype(float)
    else:
        prediction = (probabilities >= 0.5).astype(int)
        confidence = np.where(prediction == 1, probabilities, 1.0 - probabilities)
        correctness = (prediction == labels).astype(float)
    edges = np.linspace(0.0, 1.0, bins + 1)
    ece = 0.0
    for left, right in zip(edges[:-1], edges[1:]):
        mask = (confidence > left) & (confidence <= right)
        if mask.any():
            ece += mask.mean() * abs(confidence[mask].mean() - correctness[mask].mean())
    return float(ece)


def brier_score(probabilities: np.ndarray, labels: np.ndarray) -> float:
    probabilities = np.asarray(probabilities, dtype=float)
    labels = np.asarray(labels, dtype=int)
    if probabilities.ndim == 2:
        one_hot = np.eye(probabilities.shape[1])[labels]
        return float(np.mean(np.sum((probabilities - one_hot) ** 2, axis=1)))
    return float(np.mean((probabilities - labels) ** 2))


def _safe_auc(labels: np.ndarray, scores: np.ndarray, multi_class: str | None = None) -> float | None:
    try:
        if multi_class:
            return float(roc_auc_score(labels, scores, multi_class=multi_class, average="macro"))
        return float(roc_auc_score(labels, scores))
    except ValueError:
        return None


def _safe_average_precision(labels: np.ndarray, scores: np.ndarray) -> float | None:
    try:
        if scores.ndim == 2:
            one_hot = np.eye(scores.shape[1])[labels]
            return float(average_precision_score(one_hot, scores, average="macro"))
        return float(average_precision_score(labels, scores))
    except ValueError:
        return None


def classification_metrics(
    labels: np.ndarray,
    class_probabilities: np.ndarray,
    binary_labels: np.ndarray,
    binary_probability: np.ndarray,
    class_names: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    labels = np.asarray(labels, dtype=int)
    class_probabilities = np.asarray(class_probabilities, dtype=float)
    binary_labels = np.asarray(binary_labels, dtype=int)
    binary_probability = np.asarray(binary_probability, dtype=float)
    class_predictions = class_probabilities.argmax(axis=1)
    binary_predictions = (binary_probability >= 0.5).astype(int)
    multiclass_cm = confusion_matrix(labels, class_predictions, labels=np.arange(class_probabilities.shape[1]))
    binary_cm = confusion_matrix(binary_labels, binary_predictions, labels=[0, 1])
    tn, fp, fn, tp = binary_cm.ravel()
    names = list(class_names) if class_names is not None else [f"class_{index}" for index in range(class_probabilities.shape[1])]
    if len(names) != class_probabilities.shape[1]:
        raise ValueError("class_names deve possuir um nome para cada coluna de probabilidade")
    per_class: dict[str, dict[str, Any]] = {}
    for index, name in enumerate(names):
        true_class = (labels == index).astype(int)
        predicted_class = (class_predictions == index).astype(int)
        precision, recall, f1, _ = precision_recall_fscore_support(
            true_class,
            predicted_class,
            average="binary",
            zero_division=0,
        )
        per_class[name] = {
            "support": int(true_class.sum()),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "auroc_ovr": _safe_auc(true_class, class_probabilities[:, index]),
            "auprc_ovr": _safe_average_precision(true_class, class_probabilities[:, index]),
        }
    return {
        "multiclass": {
            "accuracy": float(accuracy_score(labels, class_predictions)),
            "balanced_accuracy": float(balanced_accuracy_score(labels, class_predictions)),
            "macro_f1": float(f1_score(labels, class_predictions, average="macro", zero_division=0)),
            "weighted_f1": float(f1_score(labels, class_predictions, average="weighted", zero_division=0)),
            "macro_precision": float(precision_score(labels, class_predictions, average="macro", zero_division=0)),
            "macro_recall": float(recall_score(labels, class_predictions, average="macro", zero_division=0)),
            "auroc_macro_ovr": _safe_auc(labels, class_probabilities, multi_class="ovr"),
            "auprc_macro_ovr": _safe_average_precision(labels, class_probabilities),
            "ece": expected_calibration_error(class_probabilities, labels),
            "brier": brier_score(class_probabilities, labels),
            "confusion_matrix": multiclass_cm.tolist(),
            "per_class": per_class,
        },
        "binary": {
            "accuracy": float(accuracy_score(binary_labels, binary_predictions)),
            "balanced_accuracy": float(balanced_accuracy_score(binary_labels, binary_predictions)),
            "sensitivity": float(tp / max(tp + fn, 1)),
            "specificity": float(tn / max(tn + fp, 1)),
            "precision": float(precision_score(binary_labels, binary_predictions, zero_division=0)),
            "f1": float(f1_score(binary_labels, binary_predictions, zero_division=0)),
            "mcc": float(matthews_corrcoef(binary_labels, binary_predictions)) if len(np.unique(binary_labels)) > 1 else 0.0,
            "auroc": _safe_auc(binary_labels, binary_probability),
            "auprc": _safe_average_precision(binary_labels, binary_probability),
            "ece": expected_calibration_error(binary_probability, binary_labels),
            "brier": brier_score(binary_probability, binary_labels),
            "confusion_matrix": binary_cm.tolist(),
        },
    }


def fit_temperature(logits: np.ndarray, labels: np.ndarray, binary_logits: np.ndarray | None = None, binary_labels: np.ndarray | None = None) -> dict[str, float]:
    """Busca temperatura em validação; o teste nunca deve ser usado nesta etapa."""
    import torch
    from torch import nn

    result: dict[str, float] = {"multiclass": 1.0}
    tensor_logits = torch.tensor(logits, dtype=torch.float32)
    tensor_labels = torch.tensor(labels, dtype=torch.long)
    temperature = nn.Parameter(torch.ones(1))
    optimizer = torch.optim.LBFGS([temperature], lr=0.05, max_iter=50)

    def closure() -> torch.Tensor:
        optimizer.zero_grad()
        loss = nn.functional.cross_entropy(tensor_logits / temperature.clamp_min(0.05), tensor_labels)
        loss.backward()
        return loss

    optimizer.step(closure)
    result["multiclass"] = float(temperature.detach().clamp_min(0.05).item())
    if binary_logits is not None and binary_labels is not None:
        tensor_binary_logits = torch.tensor(binary_logits, dtype=torch.float32)
        tensor_binary_labels = torch.tensor(binary_labels, dtype=torch.float32)
        binary_temperature = nn.Parameter(torch.ones(1))
        binary_optimizer = torch.optim.LBFGS([binary_temperature], lr=0.05, max_iter=50)

        def binary_closure() -> torch.Tensor:
            binary_optimizer.zero_grad()
            loss = nn.functional.binary_cross_entropy_with_logits(
                tensor_binary_logits / binary_temperature.clamp_min(0.05), tensor_binary_labels
            )
            loss.backward()
            return loss

        binary_optimizer.step(binary_closure)
        result["binary"] = float(binary_temperature.detach().clamp_min(0.05).item())
    return result
