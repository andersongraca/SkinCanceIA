from __future__ import annotations

import torch
from skin_cancer_ml.models import build_model


def main() -> None:
    x = torch.randn(2, 3, 160, 160)
    for name in ("cnn", "vit", "hybrid"):
        model = build_model(name, num_classes=7, pretrained=False, image_size=160)
        with torch.no_grad():
            output = model(x)
        print(name, tuple(output.class_logits.shape), tuple(output.binary_logits.shape))


if __name__ == "__main__":
    main()
