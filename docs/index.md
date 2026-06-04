# OpenTone

DTMF tone encoding and decoding in pure Python. OpenTone renders text or dial
strings into dual-tone multi-frequency (DTMF) signals — the touch-tone sounds of
a telephone keypad — writes them to WAV, and recovers them again with a Goertzel
detector. It depends only on the standard library.

## What it does

- **Encode** ASCII text or a literal DTMF dial string to an 8 kHz mono WAV.
- **Decode** a WAV back to the original string.
- Carry arbitrary ASCII by hex-encoding each byte into the `0-9A-F` DTMF
  alphabet, so any text survives a round trip.

## Pages

- [Quickstart](quickstart.md) — install and a first round trip.
- [Encoding](encoding.md) — text vs. dial strings, tone timing, output format.
- [Decoding](decoding.md) — sample rate, detector tuning, noisy input.
- [DTMF reference](dtmf-reference.md) — the frequency grid and symbol alphabet.
- [API reference](api-reference.md) — classes and convenience functions.

## Uses

DTMF is a simple, robust way to move small amounts of data over an audio
channel: a short URL spoken between two devices, a code played over a phone
line, or an accessibility cue carried in sound rather than on screen.
