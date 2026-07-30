# OpenTone

A data-over-sound toolkit in pure Python. OpenTone carries data through an
audio channel using a family of schemes: telephone tones, modems, Morse, image
transmission, and watermarking. Each scheme is its own submodule that shares
one set of WAV, synthesis, and Goertzel primitives. The core schemes have no
dependencies.

## Install

```bash
pip install opentone            # core schemes (no dependencies)
pip install opentone[all]       # + image/DSP schemes (numpy, Pillow)
```

## Schemes

| Module | What it carries | Dependencies |
| --- | --- | --- |
| `opentone.dtmf` | Telephone-keypad DTMF tones (text or dial strings) | none |
| `opentone.morse` | Morse / CW on-off keyed tones | none |
| `opentone.fsk` | Bytes over a Bell 202 frequency-shift-keying modem | none |
| `opentone.callerid` | Bell 202 caller-ID (SDMF / MDMF) messages | none |
| `opentone.mf` | Multi-frequency (R1) 2-of-6 signalling | none |
| `opentone.fec` | Reed-Solomon error correction (shared by the modems) | none |
| `opentone.sstv` | Images over slow-scan-TV-style FM | `numpy`, `Pillow` |
| `opentone.spectrogram` | An image painted into the audio spectrogram | `numpy`, `Pillow` |
| `opentone.watermark` | Hidden data inside existing audio | `numpy` |

## Quickstart

DTMF (also re-exported at the top level for backwards compatibility):

```python
from opentone import encode_text, decode

encode_text("hello world", "message.wav")
print(decode("message.wav"))          # "hello world"
```

Morse:

```python
from opentone import morse
morse.encode_text("SOS", "sos.wav")
print(morse.decode("sos.wav"))        # "SOS"
```

FSK modem, with optional Reed-Solomon error correction:

```python
from opentone import fsk
fsk.encode(b"arbitrary bytes", "data.wav", nsym=8)
print(fsk.decode("data.wav", nsym=8))  # b"arbitrary bytes"
```

Caller-ID:

```python
from opentone import callerid
callerid.encode("call.wav", number="5551234567", name="JARBAS AI",
                timestamp="06041530", mdmf=True)
print(callerid.decode("call.wav"))
```

Image into a spectrogram, and slow-scan-TV image transmission:

```python
from opentone import spectrogram, sstv
spectrogram.encode_image("logo.png", "logo.wav")   # view the WAV's spectrogram
sstv.encode_image("photo.png", "photo.wav", width=160, height=120)
img = sstv.decode_image("photo.wav", width=160, height=120)
```

Hide data in existing audio:

```python
from opentone import watermark
watermark.embed("song.wav", "marked.wav", b"owner-id")
print(watermark.extract("marked.wav", 8))   # b"owner-id"
```

## Input audio

The tone schemes write 8 kHz mono 16-bit WAV. To decode audio from another
source, convert it first:

```bash
ffmpeg -i some_file.mp3 -acodec pcm_s16le -ac 1 -ar 8000 out.wav
```

## Documentation

- [Quickstart](docs/quickstart.md)
- DTMF: [encoding](docs/encoding.md) · [decoding](docs/decoding.md) · [reference](docs/dtmf-reference.md)
- [Morse](docs/morse.md) · [FSK modem](docs/fsk.md) · [Caller-ID](docs/callerid.md) · [MF signalling](docs/mf.md)
- [Error correction](docs/fec.md)
- [SSTV](docs/sstv.md) · [Spectrogram art](docs/spectrogram.md) · [Watermarking](docs/watermark.md)
- [API reference](docs/api-reference.md)

Runnable scripts are in [`examples/`](examples).

## License

MIT
