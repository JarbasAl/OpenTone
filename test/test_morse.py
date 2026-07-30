import os
import tempfile

import pytest

from opentone import morse


@pytest.fixture
def wav_path():
    path = tempfile.mktemp(suffix=".wav")
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_text_to_morse():
    assert morse.text_to_morse("SOS") == "... --- ..."
    assert morse.text_to_morse("HI THERE") == ".... .. / - .... . .-. ."


def test_morse_to_text():
    assert morse.morse_to_text("... --- ...") == "SOS"
    assert morse.morse_to_text(".... .. / - .... . .-. .") == "HI THERE"


def test_text_morse_roundtrip():
    for text in ["HELLO", "ABCDEFG", "THE QUICK BROWN FOX", "0123456789"]:
        assert morse.morse_to_text(morse.text_to_morse(text)) == text


@pytest.mark.parametrize("text", ["HELLO", "SOS", "HELLO WORLD", "CQ DE TG",
                                  "TEST 123"])
def test_audio_roundtrip(text, wav_path):
    morse.encode_text(text, wav_path, wpm=20)
    assert morse.decode(wav_path, wpm=20) == text


def test_audio_roundtrip_other_wpm(wav_path):
    morse.encode_text("FAST", wav_path, wpm=30, freq=800)
    assert morse.decode(wav_path, wpm=30, freq=800) == "FAST"
