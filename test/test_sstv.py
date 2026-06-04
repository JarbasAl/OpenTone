import os
import tempfile

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("PIL")
from PIL import Image  # noqa: E402

from opentone import sstv  # noqa: E402


@pytest.fixture
def cleanup():
    paths = []
    yield paths
    for p in paths:
        if os.path.exists(p):
            os.remove(p)


def test_grayscale_image_roundtrips(cleanup):
    # Blocky grayscale pattern (low spatial frequency -> clean FM).
    blocks = np.kron(
        np.array([[0, 128, 255], [64, 192, 32], [255, 0, 160]], dtype=np.uint8),
        np.ones((40, 53), np.uint8))
    png = tempfile.mktemp(suffix=".png")
    wav = tempfile.mktemp(suffix=".wav")
    cleanup.extend([png, wav])
    Image.fromarray(blocks, "L").resize((160, 120)).save(png)

    sstv.encode_image(png, wav, width=160, height=120)
    decoded = sstv.decode_image(wav, width=160, height=120)

    original = np.asarray(Image.open(png).convert("L").resize((160, 120)), float)
    mae = np.abs(np.asarray(decoded, float) - original).mean()
    assert mae < 20  # close reconstruction


def test_decoded_dimensions(cleanup):
    png = tempfile.mktemp(suffix=".png")
    wav = tempfile.mktemp(suffix=".wav")
    cleanup.extend([png, wav])
    Image.fromarray((np.random.rand(40, 40) * 255).astype(np.uint8), "L").save(png)
    sstv.encode_image(png, wav, width=80, height=60)
    decoded = sstv.decode_image(wav, width=80, height=60)
    assert decoded.size == (80, 60)
