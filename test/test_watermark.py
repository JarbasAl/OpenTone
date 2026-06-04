import os
import tempfile

import pytest

np = pytest.importorskip("numpy")

from opentone import watermark  # noqa: E402
from opentone._audio import read_wav, write_wav  # noqa: E402


def _host(seconds=6, rate=8000):
    t = np.arange(rate * seconds) / rate
    sig = 6000 * (np.sin(2 * np.pi * 220 * t) + 0.5 * np.sin(2 * np.pi * 440 * t)
                  + 0.3 * np.sin(2 * np.pi * 110 * t))
    path = tempfile.mktemp(suffix=".wav")
    write_wav(sig.astype(int).tolist(), path, rate)
    return path


@pytest.fixture
def host():
    path = _host()
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.mark.parametrize("payload", [b"TGTG", b"owner-id", b"\x00\xff\xa5"])
def test_embed_extract_roundtrip(payload, host):
    marked = tempfile.mktemp(suffix=".wav")
    watermark.embed(host, marked, payload, alpha=0.08)
    assert watermark.extract(marked, len(payload)) == payload
    os.remove(marked)


def test_wrong_key_does_not_recover(host):
    marked = tempfile.mktemp(suffix=".wav")
    watermark.embed(host, marked, b"secret!!", key=111, alpha=0.08)
    assert watermark.extract(marked, 8, key=999) != b"secret!!"
    os.remove(marked)


def test_watermark_is_quiet(host):
    marked = tempfile.mktemp(suffix=".wav")
    watermark.embed(host, marked, b"TGTG", alpha=0.06)
    a, _ = read_wav(host)
    b, _ = read_wav(marked)
    diff = np.asarray(b, float) - np.asarray(a, float)
    host_rms = np.sqrt((np.asarray(a, float) ** 2).mean())
    mark_rms = np.sqrt((diff ** 2).mean())
    assert mark_rms < host_rms / 10  # at least ~20 dB below the host
    os.remove(marked)


def test_survives_mild_noise(host):
    marked = tempfile.mktemp(suffix=".wav")
    watermark.embed(host, marked, b"TGTG", alpha=0.08)
    samples, rate = read_wav(marked)
    rng = np.random.default_rng(3)
    noisy = (np.asarray(samples, float) + rng.normal(0, 300, len(samples)))
    write_wav(noisy.astype(int).tolist(), marked, rate)
    assert watermark.extract(marked, 4) == b"TGTG"
    os.remove(marked)


def test_host_too_short():
    short = tempfile.mktemp(suffix=".wav")
    write_wav([0] * 100, short, 8000)
    with pytest.raises(watermark.WatermarkError):
        watermark.embed(short, tempfile.mktemp(suffix=".wav"), b"toolong" * 4)
    os.remove(short)
