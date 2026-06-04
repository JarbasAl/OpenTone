# OpenTone

DTMF tone encoding and decoding in pure Python — turn text or dial strings into
the touch-tone sounds of a telephone keypad, write them to WAV, and recover them
again. Standard library only, no dependencies.

## Install

```bash
pip install opentone
```

## Quickstart

Encode text and decode it back:

```python
from opentone import encode_text, decode

encode_text("hello world", "message.wav")
print(decode("message.wav"))   # "hello world"
```

Arbitrary ASCII is carried by hex-encoding each byte, so any text round-trips.

Encode a literal DTMF dial string instead (the 16-symbol keypad alphabet
`0-9A-F`):

```python
from opentone import encode_dtmf, decode

encode_dtmf("0123456789", "dial.wav")
print(decode("dial.wav", hex_decode=False))   # "0123456789"
```

The class API (`ToneGenerator`, `ToneDecoder`) is available for finer control
over tone duration, pause, sample rate, and detector tuning.

## Input audio

Encoders write 8 kHz mono 16-bit WAV. To decode audio from another source,
convert it first:

```bash
ffmpeg -i some_file.mp3 -acodec pcm_s16le -ac 1 -ar 8000 out.wav
```

then point the decoder at the right sample rate:

```python
decode("out.wav", sample_rate=8000, min_consecutive=2, hex_decode=False)
```

## Documentation

- [Quickstart](docs/quickstart.md)
- [Encoding](docs/encoding.md)
- [Decoding](docs/decoding.md)
- [DTMF reference](docs/dtmf-reference.md)
- [API reference](docs/api-reference.md)

See [`examples/`](examples) for runnable scripts.

## License

MIT
