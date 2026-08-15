from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from skin_cancer_ml.quality import validate_image


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "ml_artifacts" / "ham10000" / "quality_reference.json"
HAM_IMAGE = ROOT / "data" / "raw" / "images" / "ISIC_0027419.jpg"
CAR_IMAGE = ROOT / "test_assets" / "ood" / "public_car_picryl.jpg"
HEAD_IMAGE = ROOT / "test_assets" / "ood" / "public_head_picryl.jpg"


@pytest.mark.skipif(not REFERENCE.exists() or not HAM_IMAGE.exists(), reason="dataset HAM10000 ainda não preparado")
def test_ham10000_lesion_is_eligible() -> None:
    result = validate_image(HAM_IMAGE, REFERENCE, require_reference=True)
    assert result["accepted"] is True
    assert result["ood_score"] < result["ood_threshold"]


@pytest.mark.skipif(not REFERENCE.exists() or not CAR_IMAGE.exists(), reason="ativos OOD públicos ainda não disponíveis")
def test_car_is_rejected_as_out_of_domain() -> None:
    result = validate_image(CAR_IMAGE, REFERENCE, require_reference=True)
    assert result["accepted"] is False
    assert "outside_dermoscopy_domain" in result["reasons"]


@pytest.mark.skipif(not REFERENCE.exists() or not HEAD_IMAGE.exists(), reason="ativos OOD públicos ainda não disponíveis")
def test_head_is_rejected_as_out_of_domain() -> None:
    result = validate_image(HEAD_IMAGE, REFERENCE, require_reference=True)
    assert result["accepted"] is False
    assert "outside_dermoscopy_domain" in result["reasons"]


def test_tiny_uniform_file_is_rejected(tmp_path: Path) -> None:
    image_path = tmp_path / "tiny.png"
    Image.new("RGB", (32, 32), (255, 255, 255)).save(image_path)
    result = validate_image(image_path, REFERENCE if REFERENCE.exists() else None, require_reference=REFERENCE.exists())
    assert result["accepted"] is False
    assert "resolution_below_minimum" in result["reasons"]
