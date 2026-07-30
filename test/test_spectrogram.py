import os
import tempfile

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("PIL")
from PIL import Image  # noqa: E402

from opentone import spectrogram  # noqa: E402


@pytest.fixture
def cleanup():
    paths = []
    yield paths
    for p in paths:
        if os.path.exists(p):
            os.remove(p)


def test_bright_band_appears_in_spectrogram(cleanup):
    # Top half of the image white -> high-frequency band should dominate.
    img = np.zeros((128, 200), dtype=np.uint8)
    img[:64, :] = 255
    png = tempfile.mktemp(suffix=".png")
    wav = tempfile.mktemp(suffix=".wav")
    cleanup.extend([png, wav])
    Image.fromarray(img, "L").save(png)

    spectrogram.encode_image(png, wav, height=128, width=200)
    mag = spectrogram.spectrogram(wav)

    half = mag.shape[0] // 2
    low_energy = mag[:half].mean()
    high_energy = mag[half:].mean()
    assert high_energy > low_energy * 2


def test_spectrogram_shape(cleanup):
    png = tempfile.mktemp(suffix=".png")
    wav = tempfile.mktemp(suffix=".wav")
    cleanup.extend([png, wav])
    Image.fromarray((np.random.rand(64, 100) * 255).astype(np.uint8), "L").save(png)
    spectrogram.encode_image(png, wav, height=64, width=100, duration=2.0)
    mag = spectrogram.spectrogram(wav, n_fft=512, hop=256)
    assert mag.shape[0] == 512 // 2 + 1
    assert mag.shape[1] > 0
