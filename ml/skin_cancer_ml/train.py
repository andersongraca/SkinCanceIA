from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json
import math

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, WeightedRandomSampler

from .config import ExperimentConfig
from .data import DermoscopyDataset, discover_images, seed_everything, split_grouped, summarize_split
from .losses import BinaryFocalLoss, FocalLoss, effective_number_weights
from .metrics import classification_metrics, fit_temperature
from .models import ModelOutput, build_model


def _device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _set_backbone_trainability(model: nn.Module, freeze: bool) -> None:
    """Controla o backbone para treinamento de transferência reprodutível."""
    for attribute in ("backbone", "cnn_backbone"):
        module = getattr(model, attribute, None)
        if module is None:
            continue
        for parameter in module.parameters():
            parameter.requires_grad = not freeze
        if freeze:
            module.eval()


def _collate(batch: list[dict[str, object]]) -> dict[str, object]:
    return {
        "image": torch.stack([item["image"] for item in batch]),
        "class_index": torch.tensor([item["class_index"] for item in batch], dtype=torch.long),
        "binary_label": torch.tensor([item["binary_label"] for item in batch], dtype=torch.float32),
        "path": [item["path"] for item in batch],
        "group_id": [item["group_id"] for item in batch],
    }


def _build_model_with_fallback(name: str, config: ExperimentConfig) -> tuple[nn.Module, bool]:
    try:
        return build_model(name, len(config.classes), config.pretrained, config.image_size), config.pretrained
    except Exception as error:
        if not config.pretrained:
            raise
        print(f"Aviso: pesos pré-treinados indisponíveis ({error}); usando inicialização sem pesos.")
        return build_model(name, len(config.classes), False, config.image_size), False


def _forward_loss(
    output: ModelOutput,
    batch: dict[str, object],
    class_loss: nn.Module,
    binary_loss: nn.Module,
    device: torch.device,
) -> torch.Tensor:
    class_target = batch["class_index"].to(device)
    binary_target = batch["binary_label"].to(device)
    return class_loss(output.class_logits, class_target) + 0.75 * binary_loss(output.binary_logits, binary_target)


def _run_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer | None,
    class_loss: nn.Module,
    binary_loss: nn.Module,
    device: torch.device,
    scaler: torch.cuda.amp.GradScaler | None,
    class_names: list[str] | None = None,
) -> tuple[float, dict[str, Any], dict[str, np.ndarray]]:
    training = optimizer is not None
    model.train(training)
    if getattr(model, "freeze_backbone", False):
        _set_backbone_trainability(model, freeze=True)
    total_loss = 0.0
    count = 0
    all_classes: list[np.ndarray] = []
    all_class_logits: list[np.ndarray] = []
    all_binary_labels: list[np.ndarray] = []
    all_binary_logits: list[np.ndarray] = []
    for batch in loader:
        images = batch["image"].to(device)
        if training:
            optimizer.zero_grad(set_to_none=True)
        autocast_enabled = device.type == "cuda"
        with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=autocast_enabled):
            output = model(images)
            loss = _forward_loss(output, batch, class_loss, binary_loss, device)
        if training:
            if scaler is not None and autocast_enabled:
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer)
                scaler.update()
            else:
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
        batch_size = images.shape[0]
        total_loss += float(loss.detach().cpu()) * batch_size
        count += batch_size
        all_classes.append(batch["class_index"].numpy())
        all_class_logits.append(output.class_logits.detach().float().cpu().numpy())
        all_binary_labels.append(batch["binary_label"].numpy().astype(int))
        all_binary_logits.append(output.binary_logits.detach().float().cpu().numpy())
    class_logits = np.concatenate(all_class_logits)
    binary_logits = np.concatenate(all_binary_logits)
    class_probabilities = torch.softmax(torch.tensor(class_logits), dim=1).numpy()
    binary_probabilities = torch.sigmoid(torch.tensor(binary_logits)).numpy()
    labels = np.concatenate(all_classes)
    binary_labels = np.concatenate(all_binary_labels)
    metrics = classification_metrics(labels, class_probabilities, binary_labels, binary_probabilities, class_names=class_names)
    raw = {
        "labels": labels,
        "class_logits": class_logits,
        "binary_labels": binary_labels,
        "binary_logits": binary_logits,
    }
    return total_loss / max(count, 1), metrics, raw


def train_one(model_name: str, config: ExperimentConfig) -> dict[str, Any]:
    seed_everything(config.seed)
    device = _device()
    output_dir = Path(config.output_dir) / model_name
    output_dir.mkdir(parents=True, exist_ok=True)
    config.save(output_dir / "config.json")

    frame = discover_images(config.data_dir, config.metadata_csv, config)
    splits = split_grouped(frame, config)
    summarize_split(splits, config.label_column).to_csv(output_dir / "split_summary.csv", index=False)
    for name, split in splits.items():
        split.to_csv(output_dir / f"{name}.csv", index=False)

    train_dataset = DermoscopyDataset(splits["train"], config, train=True)
    labels = [int(config.classes.index(str(label))) for label in splits["train"][config.label_column]]
    train_sampler = None
    sampling_strategy = "shuffle"
    if config.balanced_sampling:
        counts = np.bincount(labels, minlength=len(config.classes))
        sample_weights = np.asarray([1.0 / math.sqrt(max(counts[label], 1)) for label in labels], dtype=np.float64)
        train_sampler = WeightedRandomSampler(torch.as_tensor(sample_weights, dtype=torch.double), num_samples=len(sample_weights), replacement=True)
        sampling_strategy = "sqrt_inverse_frequency_with_replacement"
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=train_sampler is None,
        sampler=train_sampler,
        num_workers=config.num_workers,
        collate_fn=_collate,
    )
    val_loader = DataLoader(
        DermoscopyDataset(splits["val"], config, train=False),
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        collate_fn=_collate,
    )
    model, used_pretrained = _build_model_with_fallback(model_name, config)
    model.freeze_backbone = bool(getattr(config, "freeze_backbone", False))
    _set_backbone_trainability(model, freeze=model.freeze_backbone)
    model.to(device)
    class_weights = effective_number_weights(labels, len(config.classes)).to(device)
    class_loss = FocalLoss(class_weights if config.use_class_balanced_focal else None, config.focal_gamma)
    positive = max(float(sum(splits["train"][config.label_column].isin(config.malignant_classes))), 1.0)
    negative = max(float(len(splits["train"]) - positive), 1.0)
    binary_loss = BinaryFocalLoss(config.focal_gamma, negative / positive)
    trainable_parameters = [parameter for parameter in model.parameters() if parameter.requires_grad]
    if not trainable_parameters:
        raise RuntimeError("Nenhum parâmetro treinável foi encontrado.")
    optimizer = torch.optim.AdamW(trainable_parameters, lr=config.learning_rate, weight_decay=config.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(config.epochs, 1))
    scaler = torch.cuda.amp.GradScaler(enabled=device.type == "cuda")
    best_score = -math.inf
    best_epoch = -1
    history: list[dict[str, Any]] = []
    for epoch in range(config.epochs):
        train_loss, train_metrics, _ = _run_epoch(model, train_loader, optimizer, class_loss, binary_loss, device, scaler, list(config.classes))
        with torch.no_grad():
            val_loss, val_metrics, val_raw = _run_epoch(model, val_loader, None, class_loss, binary_loss, device, None, list(config.classes))
        scheduler.step()
        score = val_metrics["binary"]["auroc"] if val_metrics["binary"]["auroc"] is not None else val_metrics["multiclass"]["macro_f1"]
        history.append({"epoch": epoch + 1, "train_loss": train_loss, "val_loss": val_loss, "train": train_metrics, "val": val_metrics, "lr": optimizer.param_groups[0]["lr"]})
        print(json.dumps(history[-1], ensure_ascii=False))
        if score > best_score:
            best_score = score
            best_epoch = epoch + 1
            torch.save({"model_name": model_name, "model_state": model.state_dict(), "classes": list(config.classes), "config": config.to_dict(), "used_pretrained": used_pretrained}, output_dir / "best.pt")
            np.savez(output_dir / "best_validation_logits.npz", **val_raw)
    best = json.loads(json.dumps(history[-1], default=float)) if history else {}
    if (output_dir / "best_validation_logits.npz").exists():
        raw = np.load(output_dir / "best_validation_logits.npz")
        temperatures = fit_temperature(raw["class_logits"], raw["labels"], raw["binary_logits"], raw["binary_labels"])
    else:
        temperatures = {"multiclass": 1.0, "binary": 1.0}
    (output_dir / "calibration.json").write_text(json.dumps(temperatures, indent=2), encoding="utf-8")
    (output_dir / "history.json").write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = {"model": model_name, "device": str(device), "best_epoch": best_epoch, "best_validation_score": best_score, "used_pretrained": used_pretrained, "freeze_backbone": bool(config.freeze_backbone), "balanced_sampling": bool(config.balanced_sampling), "sampling_strategy": sampling_strategy, "trainable_parameter_count": int(sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)), "calibration": temperatures, "last_epoch": best}
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Treinamento reproduzível de modelos dermatoscópicos")
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--metadata-csv", required=True)
    parser.add_argument("--output-dir", default="ml_artifacts")
    parser.add_argument("--model", choices=["cnn", "vit", "hybrid", "all"], default="all")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--no-pretrained", action="store_true")
    parser.add_argument("--freeze-backbone", action="store_true", help="Congela o backbone e treina somente as cabeças/transformer")
    parser.add_argument("--balanced-sampler", action="store_true", help="Usa amostragem com raiz inversa da frequência somente no treino")
    args = parser.parse_args()
    config = ExperimentConfig(
        data_dir=args.data_dir,
        metadata_csv=args.metadata_csv,
        output_dir=args.output_dir,
        model_name=args.model,
        epochs=args.epochs,
        batch_size=args.batch_size,
        image_size=args.image_size,
        pretrained=not args.no_pretrained,
        freeze_backbone=args.freeze_backbone,
        balanced_sampling=args.balanced_sampler,
    )
    names = ["cnn", "vit", "hybrid"] if args.model == "all" else [args.model]
    for name in names:
        train_one(name, config)


if __name__ == "__main__":
    main()
