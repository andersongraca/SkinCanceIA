from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json


DEFAULT_CLASSES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]
# Configuração padrão conservadora; ajuste mediante validação clínica do protocolo.
DEFAULT_MALIGNANT_CLASSES = {"mel", "bcc", "akiec"}


@dataclass
class ExperimentConfig:
    data_dir: str
    metadata_csv: str
    output_dir: str = "ml_artifacts"
    image_size: int = 224
    batch_size: int = 16
    epochs: int = 20
    learning_rate: float = 3e-4
    weight_decay: float = 1e-4
    warmup_epochs: int = 2
    num_workers: int = 0
    seed: int = 42
    model_name: str = "all"
    pretrained: bool = True
    freeze_backbone: bool = False
    use_class_balanced_focal: bool = True
    balanced_sampling: bool = False
    focal_gamma: float = 2.0
    validation_fraction: float = 0.15
    test_fraction: float = 0.15
    patient_column: str = "patient_id"
    lesion_column: str = "lesion_id"
    image_column: str = "image_id"
    label_column: str = "dx"
    malignant_classes: tuple[str, ...] = tuple(sorted(DEFAULT_MALIGNANT_CLASSES))
    classes: tuple[str, ...] = tuple(DEFAULT_CLASSES)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["malignant_classes"] = list(self.malignant_classes)
        result["classes"] = list(self.classes)
        return result

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def from_json(cls, path: str | Path) -> "ExperimentConfig":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        raw["malignant_classes"] = tuple(raw.get("malignant_classes", DEFAULT_MALIGNANT_CLASSES))
        raw["classes"] = tuple(raw.get("classes", DEFAULT_CLASSES))
        return cls(**raw)
