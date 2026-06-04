import os
import tempfile

import pytest

from opentone import mf


@pytest.fixture
def wav_path():
    path = tempfile.mktemp(suffix=".wav")
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_digit_string_roundtrip(wav_path):
    mf.encode("0123456789", wav_path)
    assert mf.decode(wav_path) == list("0123456789")


def test_control_symbols_roundtrip(wav_path):
    seq = ["KP", "5", "5", "5", "1", "2", "3", "4", "ST"]
    mf.encode(seq, wav_path)
    assert mf.decode(wav_path) == seq


def test_all_symbols_roundtrip(wav_path):
    seq = mf.MF_SYMBOLS
    mf.encode(seq, wav_path)
    assert mf.decode(wav_path) == seq


def test_unknown_symbol_raises(wav_path):
    with pytest.raises(ValueError):
        mf.encode(["KP", "Z"], wav_path)
