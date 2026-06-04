from os.path import join

from opentone import ToneDecoder, decode


def test_hex_decode():
    assert ToneDecoder.hex_decode("68656c6c6f20776f726c64") == "hello world"


def test_decode_clean_phone_fixture(examples_dir):
    result = decode(join(examples_dir, "0123456789.wav"),
                    sample_rate=8000, min_consecutive=2, hex_decode=False)
    assert result == "0123456789"


def test_decode_noisy_phone_fixture(examples_dir):
    result = decode(join(examples_dir, "phonecall.wav"),
                    sample_rate=8000, goertzel_n=92, min_consecutive=3,
                    hex_decode=False)
    assert result == "05464273316"


def test_reset_clears_state(examples_dir):
    dec = ToneDecoder(sample_rate=8000, min_consecutive=2, hex_decode=False)
    first = dec.decode_wave(join(examples_dir, "0123456789.wav"))
    # decode_wave resets internally, so a second call gives the same answer.
    second = dec.decode_wave(join(examples_dir, "0123456789.wav"))
    assert first == second == "0123456789"
