import os
import tempfile

import pytest

from opentone import callerid
from opentone.callerid import build_message, parse_message, CallerIDError


@pytest.fixture
def wav_path():
    path = tempfile.mktemp(suffix=".wav")
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_sdmf_message_roundtrip():
    msg = build_message(number="5551234567", timestamp="06041530")
    parsed = parse_message(msg)
    assert parsed == {"format": "SDMF", "datetime": "06041530",
                      "number": "5551234567"}


def test_mdmf_message_roundtrip():
    msg = build_message(number="5551234567", name="JARBAS AI",
                        timestamp="06041530", mdmf=True)
    parsed = parse_message(msg)
    assert parsed["format"] == "MDMF"
    assert parsed["number"] == "5551234567"
    assert parsed["name"] == "JARBAS AI"
    assert parsed["datetime"] == "06041530"


def test_checksum_detects_tampering():
    msg = bytearray(build_message(number="123", timestamp="01020304"))
    msg[3] ^= 0x01
    with pytest.raises(CallerIDError):
        parse_message(bytes(msg))


def test_audio_roundtrip_sdmf(wav_path):
    callerid.encode(wav_path, number="5551234567", timestamp="06041530")
    assert callerid.decode(wav_path)["number"] == "5551234567"


def test_audio_roundtrip_mdmf(wav_path):
    callerid.encode(wav_path, number="5550001111", name="TEST CALLER",
                    timestamp="12250900", mdmf=True)
    parsed = callerid.decode(wav_path)
    assert parsed["name"] == "TEST CALLER"
    assert parsed["number"] == "5550001111"


def test_bad_timestamp():
    with pytest.raises(ValueError):
        build_message(number="1", timestamp="bad")
