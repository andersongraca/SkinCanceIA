from __future__ import annotations

import torch
from torch import Tensor, nn
import torch.nn.functional as F


class FocalLoss(nn.Module):
    def __init__(self, class_weights: Tensor | None = None, gamma: float = 2.0):
        super().__init__()
        self.register_buffer("class_weights", class_weights if class_weights is not None else torch.empty(0))
        self.gamma = gamma

    def forward(self, logits: Tensor, target: Tensor) -> Tensor:
        log_prob = F.log_softmax(logits, dim=1)
        prob = log_prob.exp()
        target_log_prob = log_prob.gather(1, target.unsqueeze(1)).squeeze(1)
        target_prob = prob.gather(1, target.unsqueeze(1)).squeeze(1)
        loss = -((1.0 - target_prob).clamp_min(1e-6) ** self.gamma) * target_log_prob
        if self.class_weights.numel():
            loss = loss * self.class_weights[target]
        return loss.mean()


class BinaryFocalLoss(nn.Module):
    def __init__(self, gamma: float = 2.0, positive_weight: float | None = None):
        super().__init__()
        self.gamma = gamma
        self.positive_weight = positive_weight

    def forward(self, logits: Tensor, target: Tensor) -> Tensor:
        target = target.float()
        bce = F.binary_cross_entropy_with_logits(logits, target, reduction="none")
        probability = torch.sigmoid(logits)
        p_t = probability * target + (1.0 - probability) * (1.0 - target)
        loss = ((1.0 - p_t).clamp_min(1e-6) ** self.gamma) * bce
        if self.positive_weight is not None:
            loss = loss * torch.where(target > 0.5, self.positive_weight, 1.0)
        return loss.mean()


def effective_number_weights(labels: list[int] | Tensor, num_classes: int, beta: float = 0.9999) -> Tensor:
    if isinstance(labels, Tensor):
        labels = labels.detach().cpu().tolist()
    counts = torch.bincount(torch.tensor(labels, dtype=torch.long), minlength=num_classes).float()
    effective = (1.0 - beta ** counts.clamp_min(1.0)) / (1.0 - beta)
    weights = 1.0 / effective
    weights = weights / weights.mean().clamp_min(1e-8)
    return weights
