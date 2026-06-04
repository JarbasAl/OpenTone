"""Image-over-sound and watermarking — needs the image/dsp extras.

    pip install opentone[all]
"""
import tempfile

try:
    import numpy as np
    from PIL import Image
except ImportError:
    raise SystemExit("install extras first: pip install opentone[all]")

from opentone import spectrogram, sstv, watermark
from opentone._audio import write_wav

# A small grayscale test image.
img = np.kron(np.array([[0, 200], [120, 255]], dtype=np.uint8),
              np.ones((60, 80), np.uint8))
png = tempfile.mktemp(suffix=".png")
Image.fromarray(img, "L").save(png)

# SSTV: image -> audio -> image.
sw = tempfile.mktemp(suffix=".wav")
sstv.encode_image(png, sw, width=160, height=120)
sstv.decode_image(sw, width=160, height=120).save(tempfile.mktemp(suffix=".png"))
print("sstv: encoded and decoded an image")

# Spectrogram art: open spec.wav in a spectrogram viewer to see the picture.
spectrogram.encode_image(png, tempfile.mktemp(suffix=".wav"))
print("spectrogram: rendered image into audio")

# Watermark: hide bytes in a host tone.
t = np.arange(8000 * 5) / 8000
host = tempfile.mktemp(suffix=".wav")
write_wav((6000 * np.sin(2 * np.pi * 220 * t)).astype(int).tolist(), host, 8000)
marked = tempfile.mktemp(suffix=".wav")
watermark.embed(host, marked, b"owner-id")
print("watermark:", watermark.extract(marked, 8))
