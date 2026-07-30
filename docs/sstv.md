# SSTV

`opentone.sstv` transmits a grayscale image over audio in a slow-scan-TV style.
Each line starts with a sync pulse, then every pixel is sent as a tone whose
frequency encodes its brightness (black 1500 Hz to white 2300 Hz). Encoding uses
continuous-phase FM. Decoding recovers brightness with an analytic-signal FM
demodulator.

Requires the `image` (Pillow) and `dsp` (numpy) extras.

```python
from opentone import sstv

sstv.encode_image("photo.png", "photo.wav", width=160, height=120)
img = sstv.decode_image("photo.wav", width=160, height=120)   # PIL Image
img.save("recovered.png")
```

`width`, `height`, `pixel_ms`, and `sync_ms` must match between encode and
decode. This is a self-consistent grayscale mode. It round-trips with this
decoder but is not wire-compatible with standard SSTV hardware modes.

---
[← Error correction](fec.md) · [Home](index.md) · [Spectrogram art →](spectrogram.md)
