# Spectrogram art

`opentone.spectrogram` paints an image into the spectrogram of an audio file.
Each image column becomes a short time slice and each row a frequency band: pixel
brightness sets the amplitude of an additive sine at that frequency. Open the
result in any spectrogram view and the picture appears.

Requires the `image` (Pillow) and `dsp` (numpy) extras.

```python
from opentone import spectrogram

spectrogram.encode_image("logo.png", "logo.wav",
                         duration=4.0, f_min=500, f_max=3500)

# Inspect what a spectrogram view would show:
mag = spectrogram.spectrogram("logo.wav")   # 2D numpy magnitude array
```

`height` sets the number of frequency bands, `width` the number of time columns,
and `f_min` / `f_max` the band the image occupies. This is a one-way visual
encoding. The image is meant to be *seen* in the spectrogram, not byte-exactly
recovered.

---
[← SSTV](sstv.md) · [Home](index.md) · [Watermarking →](watermark.md)
