import numpy as np

from ml.skin_cancer_ml.explain import _overlay, _restrict_to_lesion


def test_overlay_keeps_zero_saliency_pixels_unchanged():
    image = np.full((24, 32, 3), 127.0, dtype=np.float32)
    heatmap = np.zeros((24, 32), dtype=np.float32)
    overlay = _overlay(image, heatmap)
    assert np.array_equal(overlay, image.astype(np.uint8))


def test_lesion_gate_zeros_background_pixels():
    values = np.arange(64, dtype=np.float32).reshape(8, 8)
    lesion_mask = np.zeros((8, 8), dtype=np.float32)
    lesion_mask[2:6, 2:6] = 1.0
    restricted = _restrict_to_lesion(values, lesion_mask)
    assert float(restricted[:2].max()) == 0.0
    assert float(restricted[:, :2].max()) == 0.0
    assert float(restricted[2:6, 2:6].max()) > 0.5
