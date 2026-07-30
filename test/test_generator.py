from opentone import ToneGenerator


def test_hex_encode():
    assert ToneGenerator.hex_encode("hello world") == "68656c6c6f20776f726c64"


def test_frequency_grid_complete():
    gen = ToneGenerator()
    # 16 DTMF symbols, each mapping to exactly one row + one column frequency.
    assert set(gen.FREQUENCY_MAPPINGS) == set("0123456789ABCDEF")
    for row, col in gen.FREQUENCY_MAPPINGS.values():
        assert row in ToneGenerator.frequencyR
        assert col in ToneGenerator.frequencyC


def test_generate_tone_length():
    gen = ToneGenerator(duration=100, pause=500)
    samples = gen.generate_tone(697, 1209, 100)
    # 100ms tone + 500ms pause at 8000 Hz = 800 + 4000 samples.
    assert len(samples) == int(8000 * 100 / 1000) + int(8000 * 500 / 1000)


def test_silence_is_zero():
    gen = ToneGenerator()
    silence = gen._get_silence(500)
    assert silence == [0] * int(8000 * 500 / 1000)
