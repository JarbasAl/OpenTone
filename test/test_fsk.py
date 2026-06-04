import os
import random
import tempfile

import pytest

from opentone import fsk
from opentone._audio import read_wav, write_wav


@pytest.fixture
def wav_path():
    path = tempfile.mktemp(suffix=".wav")
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.mark.parametrize("data", [b"hello", b"\x00\x01\xff\xfe", bytes(range(64)),
                                  b"a longer data-over-sound message payload"])
def test_clean_roundtrip(data, wav_path):
    fsk.encode(data, wav_path)
    assert fsk.decode(wav_path) == data


def test_empty(wav_path):
    fsk.encode(b"", wav_path)
    assert fsk.decode(wav_path) == b""


def test_fec_clean_roundtrip(wav_path):
    data = b"forward error corrected payload"
    fsk.encode(data, wav_path, nsym=10)
    assert fsk.decode(wav_path, nsym=10) == data


def test_fec_recovers_from_noise(wav_path):
    data = b"error corrected payload over a noisy channel"
    fsk.encode(data, wav_path, nsym=12)
    samples, rate = read_wav(wav_path)
    rng = random.Random(7)
    for _ in range(300):
        i = rng.randrange(len(samples))
        samples[i] = max(-32767, min(32767, samples[i] + rng.randint(-10000, 10000)))
    write_wav(samples, wav_path, rate)
    assert fsk.decode(wav_path, nsym=12) == data


def test_custom_baud(wav_path):
    data = b"slow and steady"
    fsk.encode(data, wav_path, baud=200)
    assert fsk.decode(wav_path, baud=200) == data
