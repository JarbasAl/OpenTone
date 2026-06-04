# Quickstart

## Install

```bash
pip install opentone
```

OpenTone has no runtime dependencies.

## A first round trip

```python
from opentone import encode_text, decode

encode_text("hello world", "message.wav")
print(decode("message.wav"))   # "hello world"
```

`encode_text` hex-encodes the bytes of the string and emits them as DTMF tones,
so any ASCII text round-trips. `decode` reverses both steps.

## Dial strings

To work with keypad symbols directly, skip the hex layer:

```python
from opentone import encode_dtmf, decode

encode_dtmf("1234ABCD", "dial.wav")
print(decode("dial.wav", hex_decode=False))   # "1234ABCD"
```

## Next

- [Encoding](encoding.md) for tone timing and the output WAV format.
- [Decoding](decoding.md) for decoding audio from other sources.
