from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch
from torch import Tensor, nn
import torch.nn.functional as F
import timm


@dataclass
class ModelOutput:
    class_logits: Tensor
    binary_logits: Tensor
    aux: dict[str, Any]


class MultiTaskHead(nn.Module):
    def __init__(self, input_dim: int, num_classes: int, dropout: float = 0.25):
        super().__init__()
        hidden = max(128, input_dim // 2)
        self.norm = nn.LayerNorm(input_dim)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(input_dim, num_classes)
        self.binary = nn.Linear(input_dim, 1)
        self.auxiliary = nn.Sequential(
            nn.Linear(input_dim, hidden),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, input_dim),
        )

    def forward(self, representation: Tensor) -> tuple[Tensor, Tensor]:
        representation = self.norm(representation)
        representation = representation + 0.1 * self.auxiliary(representation)
        representation = self.dropout(representation)
        return self.classifier(representation), self.binary(representation).squeeze(-1)


class CNNModel(nn.Module):
    model_id = "cnn"

    def __init__(self, num_classes: int = 7, pretrained: bool = True):
        super().__init__()
        self.backbone = timm.create_model("resnet50", pretrained=pretrained, num_classes=0, global_pool="")
        self.feature_dim = int(self.backbone.num_features)
        self.head = MultiTaskHead(self.feature_dim, num_classes)
        self.last_feature_map: Tensor | None = None

    def forward(self, x: Tensor) -> ModelOutput:
        feature_map = self.backbone.forward_features(x)
        if feature_map.ndim != 4:
            raise RuntimeError(f"CNN esperava mapa 4D, recebeu {tuple(feature_map.shape)}")
        self.last_feature_map = feature_map
        representation = F.adaptive_avg_pool2d(feature_map, 1).flatten(1)
        class_logits, binary_logits = self.head(representation)
        return ModelOutput(class_logits, binary_logits, {"feature_map": feature_map, "representation": representation})


class ViTModel(nn.Module):
    model_id = "vit"

    def __init__(self, num_classes: int = 7, pretrained: bool = True, image_size: int = 224):
        super().__init__()
        self.backbone = timm.create_model("vit_small_patch16_224", pretrained=pretrained, num_classes=0, img_size=image_size)
        self.feature_dim = int(self.backbone.num_features)
        self.head = MultiTaskHead(self.feature_dim, num_classes)
        self.last_tokens: Tensor | None = None

    def forward(self, x: Tensor) -> ModelOutput:
        tokens = self.backbone.forward_features(x)
        if tokens.ndim != 3:
            raise RuntimeError(f"ViT esperava tokens 3D, recebeu {tuple(tokens.shape)}")
        self.last_tokens = tokens
        representation = tokens[:, 0]
        class_logits, binary_logits = self.head(representation)
        return ModelOutput(class_logits, binary_logits, {"tokens": tokens, "representation": representation})


class AttentionBlock(nn.Module):
    def __init__(self, embed_dim: int, heads: int, dropout: float = 0.1):
        super().__init__()
        self.norm1 = nn.LayerNorm(embed_dim)
        self.attention = nn.MultiheadAttention(embed_dim, heads, dropout=dropout, batch_first=True)
        self.norm2 = nn.LayerNorm(embed_dim)
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim * 4, embed_dim),
            nn.Dropout(dropout),
        )

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
        normalized = self.norm1(x)
        attended, weights = self.attention(
            normalized,
            normalized,
            normalized,
            need_weights=True,
            average_attn_weights=False,
        )
        x = x + attended
        x = x + self.mlp(self.norm2(x))
        return x, weights


class HybridModel(nn.Module):
    model_id = "hybrid"

    def __init__(self, num_classes: int = 7, pretrained: bool = True, image_size: int = 224):
        super().__init__()
        self.cnn_backbone = timm.create_model(
            "resnet50",
            pretrained=pretrained,
            num_classes=0,
            global_pool="",
        )
        self.cnn_dim = int(self.cnn_backbone.num_features)
        self.embed_dim = 192
        self.token_grid = image_size // 16
        self.token_count = self.token_grid * self.token_grid
        self.token_projection = nn.Conv2d(self.cnn_dim, self.embed_dim, kernel_size=1)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, self.embed_dim))
        self.position = nn.Parameter(torch.zeros(1, self.token_count + 1, self.embed_dim))
        self.blocks = nn.ModuleList([AttentionBlock(self.embed_dim, heads=3) for _ in range(2)])
        self.final_norm = nn.LayerNorm(self.embed_dim)
        self.cnn_projection = nn.Sequential(
            nn.LayerNorm(self.cnn_dim),
            nn.Linear(self.cnn_dim, self.embed_dim),
            nn.GELU(),
        )
        self.gate = nn.Sequential(
            nn.LayerNorm(self.embed_dim * 2),
            nn.Linear(self.embed_dim * 2, self.embed_dim),
            nn.GELU(),
            nn.Linear(self.embed_dim, 1),
            nn.Sigmoid(),
        )
        self.head = MultiTaskHead(self.embed_dim, num_classes)
        self.last_feature_map: Tensor | None = None
        self.last_tokens: Tensor | None = None
        self.last_attentions: list[Tensor] = []
        nn.init.trunc_normal_(self.cls_token, std=0.02)
        nn.init.trunc_normal_(self.position, std=0.02)

    def forward(self, x: Tensor) -> ModelOutput:
        feature_map = self.cnn_backbone.forward_features(x)
        if feature_map.ndim != 4:
            raise RuntimeError(f"Híbrido esperava mapa 4D, recebeu {tuple(feature_map.shape)}")
        self.last_feature_map = feature_map
        pooled_map = F.adaptive_avg_pool2d(feature_map, (self.token_grid, self.token_grid))
        tokens = self.token_projection(pooled_map).flatten(2).transpose(1, 2)
        cls = self.cls_token.expand(x.shape[0], -1, -1)
        tokens = torch.cat((cls, tokens), dim=1) + self.position
        self.last_attentions = []
        for block in self.blocks:
            tokens, attention = block(tokens)
            self.last_attentions.append(attention)
        tokens = self.final_norm(tokens)
        vit_representation = tokens[:, 0]
        cnn_representation = self.cnn_projection(F.adaptive_avg_pool2d(feature_map, 1).flatten(1))
        gate = self.gate(torch.cat((cnn_representation, vit_representation), dim=1))
        representation = gate * cnn_representation + (1.0 - gate) * vit_representation
        class_logits, binary_logits = self.head(representation)
        self.last_tokens = tokens
        return ModelOutput(
            class_logits,
            binary_logits,
            {
                "feature_map": feature_map,
                "tokens": tokens,
                "attentions": self.last_attentions,
                "gate": gate,
                "representation": representation,
            },
        )


class EnsembleModel(nn.Module):
    model_id = "ensemble"

    def __init__(self, models: dict[str, nn.Module], weights: dict[str, float] | None = None):
        super().__init__()
        self.models = nn.ModuleDict(models)
        self.weights = weights or {name: 1.0 / len(models) for name in models}

    def forward(self, x: Tensor) -> ModelOutput:
        outputs = {name: model(x) for name, model in self.models.items()}
        normalized_weights = torch.tensor(
            [self.weights[name] for name in outputs], device=x.device, dtype=x.dtype
        )
        normalized_weights = normalized_weights / normalized_weights.sum().clamp_min(1e-8)
        class_logits = sum(output.class_logits * normalized_weights[i] for i, output in enumerate(outputs.values()))
        binary_logits = sum(output.binary_logits * normalized_weights[i] for i, output in enumerate(outputs.values()))
        return ModelOutput(class_logits, binary_logits, {"members": outputs, "weights": self.weights})


def build_model(name: str, num_classes: int = 7, pretrained: bool = True, image_size: int = 224) -> nn.Module:
    name = name.lower()
    if name == "cnn":
        return CNNModel(num_classes=num_classes, pretrained=pretrained)
    if name == "vit":
        return ViTModel(num_classes=num_classes, pretrained=pretrained, image_size=image_size)
    if name == "hybrid":
        return HybridModel(num_classes=num_classes, pretrained=pretrained, image_size=image_size)
    raise ValueError(f"Modelo desconhecido: {name}")
