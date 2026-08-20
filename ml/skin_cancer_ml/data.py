from __future__ import annotations

from pathlib import Path
from typing import Iterable
import random

import numpy as np
import pandas as pd
import torch
from PIL import Image
from sklearn.model_selection import GroupShuffleSplit
from torch.utils.data import Dataset
from torchvision import transforms

from .config import ExperimentConfig


class DermoscopyDataset(Dataset):
    def __init__(self, frame: pd.DataFrame, config: ExperimentConfig, train: bool = False):
        self.frame = frame.reset_index(drop=True).copy()
        self.config = config
        self.train = train
        self.class_to_index = {label: i for i, label in enumerate(config.classes)}
        self.transform = build_transforms(config.image_size, train=train)

    def __len__(self) -> int:
        return len(self.frame)

    def __getitem__(self, index: int) -> dict[str, object]:
        row = self.frame.iloc[index]
        image_path = Path(str(row["image_path"]))
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            tensor = self.transform(image)
        label = str(row[self.config.label_column]).lower()
        if label not in self.class_to_index:
            raise ValueError(f"Classe desconhecida: {label}")
        binary = float(label in set(self.config.malignant_classes))
        return {
            "image": tensor,
            "class_index": self.class_to_index[label],
            "binary_label": binary,
            "path": str(image_path),
            "group_id": str(row["group_id"]),
        }


def build_transforms(image_size: int, train: bool) -> transforms.Compose:
    ops: list[object] = [transforms.Resize((image_size, image_size))]
    if train:
        ops.extend(
            [
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomVerticalFlip(p=0.15),
                transforms.RandomRotation(degrees=20),
                transforms.RandomResizedCrop(image_size, scale=(0.82, 1.0), ratio=(0.9, 1.1)),
                transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.12, hue=0.03),
                transforms.RandomApply([transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 1.0))], p=0.08),
            ]
        )
    ops.extend(
        [
            transforms.ToTensor(),
            transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ]
    )
    return transforms.Compose(ops)


def discover_images(data_dir: str | Path, metadata_csv: str | Path, config: ExperimentConfig) -> pd.DataFrame:
    metadata_path = Path(metadata_csv)
    separator = "\t" if metadata_path.suffix.lower() in {".tab", ".tsv"} else ","
    metadata = pd.read_csv(metadata_path, sep=separator)
    required = {config.image_column, config.label_column}
    missing = required.difference(metadata.columns)
    if missing:
        raise ValueError(f"Colunas ausentes no metadata: {sorted(missing)}")

    root = Path(data_dir)
    image_paths: list[str] = []
    for image_id in metadata[config.image_column].astype(str):
        candidates = [root / image_id, root / f"{image_id}.jpg", root / f"{image_id}.jpeg", root / f"{image_id}.png"]
        found = next((candidate for candidate in candidates if candidate.exists()), None)
        if found is None:
            image_paths.append("")
        else:
            image_paths.append(str(found.resolve()))
    metadata = metadata.assign(image_path=image_paths)
    metadata = metadata[metadata["image_path"] != ""].copy()
    metadata[config.label_column] = metadata[config.label_column].astype(str).str.lower()
    metadata = metadata[metadata[config.label_column].isin(config.classes)].copy()

    group_candidates = [config.patient_column, config.lesion_column, config.image_column]
    group_column = next((column for column in group_candidates if column in metadata.columns), config.image_column)
    metadata["group_id"] = metadata[group_column].astype(str)
    if metadata.empty:
        raise ValueError("Nenhuma imagem válida foi associada ao metadata.")
    return metadata.reset_index(drop=True)


def split_grouped(frame: pd.DataFrame, config: ExperimentConfig) -> dict[str, pd.DataFrame]:
    if not 0 < config.validation_fraction < 1 or not 0 < config.test_fraction < 1:
        raise ValueError("validation_fraction e test_fraction devem estar entre 0 e 1")
    if config.validation_fraction + config.test_fraction >= 1:
        raise ValueError("validation_fraction + test_fraction deve ser menor que 1")

    groups = frame["group_id"].astype(str).to_numpy()
    splitter_test = GroupShuffleSplit(n_splits=1, test_size=config.test_fraction, random_state=config.seed)
    train_val_idx, test_idx = next(splitter_test.split(frame, groups=groups))
    train_val = frame.iloc[train_val_idx].copy()
    test = frame.iloc[test_idx].copy()

    relative_val = config.validation_fraction / (1.0 - config.test_fraction)
    splitter_val = GroupShuffleSplit(n_splits=1, test_size=relative_val, random_state=config.seed + 1)
    train_idx, val_idx = next(splitter_val.split(train_val, groups=train_val["group_id"].astype(str).to_numpy()))
    train = train_val.iloc[train_idx].copy()
    val = train_val.iloc[val_idx].copy()

    assert set(train.group_id).isdisjoint(set(val.group_id))
    assert set(train.group_id).isdisjoint(set(test.group_id))
    assert set(val.group_id).isdisjoint(set(test.group_id))
    return {"train": train.reset_index(drop=True), "val": val.reset_index(drop=True), "test": test.reset_index(drop=True)}


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def summarize_split(split: dict[str, pd.DataFrame], label_column: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for name, frame in split.items():
        counts = frame[label_column].value_counts().to_dict()
        for label, count in counts.items():
            rows.append({"split": name, "class": label, "count": int(count), "groups": int(frame["group_id"].nunique())})
    return pd.DataFrame(rows)
