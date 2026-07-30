# Encoding

## Text vs. dial strings

There are two ways to encode:

- **Text**: `encode_text` (or `ToneGenerator.encode_to_wave`) hex-encodes each
  byte of the string and emits the hex digits as DTMF symbols. Any ASCII text
  round-trips, at the cost of two DTMF symbols per character.
- **Dial string**: `encode_dtmf` (or `ToneGenerator.dtmf_to_wave`) writes the
  symbols literally. The input must be in the DTMF alphabet `0-9A-F`. One symbol
  per character, no hex expansion.

```python
from opentone import encode_text, encode_dtmf

encode_text("hi", "text.wav")        # carries the bytes of "hi"
encode_dtmf("0123456789", "dial.wav")  # carries the digits themselves
```

## Tone timing

`ToneGenerator` controls how long each tone lasts and how much silence follows:

```python
from opentone import ToneGenerator

gen = ToneGenerator(duration=100, pause=500)  # milliseconds
gen.encode_to_wave("hello", "out.wav")
```

- `duration`: length of each tone. Longer tones are easier to detect but make
  the signal longer.
- `pause`: silence between tones. It lets the decoder separate adjacent
  symbols.

## Output format

Encoders write **8 kHz, mono, 16-bit PCM** WAV. The two DTMF frequencies for a
symbol are summed and scaled to the 16-bit range. See the
[DTMF reference](dtmf-reference.md) for the frequency grid.

---
[← Quickstart](quickstart.md) · [Home](index.md) · [Decoding →](decoding.md)
