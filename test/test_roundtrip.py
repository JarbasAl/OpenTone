import os
import tempfile

import pytest

from opentone import ToneGenerator, ToneDecoder, encode_text, encode_dtmf, decode


@pytest.fixture
def wav_path():
    path = tempfile.mktemp(suffix=".wav")
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.mark.parametrize("text", ["hello world", "OpenTone", "a", "12345"])
def test_text_roundtrip(text, wav_path):
    encode_text(text, wav_path)
    assert decode(wav_path) == text


def test_class_text_roundtrip(wav_path):
    ToneGenerator().encode_to_wave("hello world", wav_path)
    assert ToneDecoder().decode_wave(wav_path) == "hello world"


@pytest.mark.parametrize("dial", ["0123456789", "1234ABCD", "0"])
def test_dtmf_roundtrip(dial, wav_path):
    encode_dtmf(dial, wav_path)
    assert decode(wav_path, hex_decode=False) == dial


def test_convenience_returns_path(wav_path):
    assert encode_text("hi", wav_path) == wav_path
    assert encode_dtmf("12", wav_path) == wav_path


def test_encode_writes_8khz_mono_16bit(wav_path):
    import wave

    encode_text("hi", wav_path)
    with wave.open(wav_path) as w:
        assert w.getframerate() == 8000
        assert w.getnchannels() == 1
        assert w.getsampwidth() == 2
