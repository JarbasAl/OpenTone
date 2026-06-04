"""SSTV — slow-scan-TV-style image transmission over audio.

A grayscale, Martin-style FM mode: each line starts with a sync pulse, then every
pixel is sent as a tone whose frequency encodes its brightness (black 1500 Hz to
white 2300 Hz). Encoding uses continuous-phase FM; decoding recovers brightness
with an analytic-signal FM demodulator. Requires the ``dsp`` (numpy) and
``image`` (Pillow) extras.

    from opentone import sstv

    sstv.encode_image("cat.png", "cat.wav", width=160, height=120)
    img = sstv.decode_image("cat.wav", width=160, height=120)  # PIL Image

This is a self-consistent grayscale mode (round-trips with this decoder); it is
not wire-compatible with standard SSTV hardware modes.
"""
import math

from opentone._audio import read_wav, write_wav

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

__all__ = ["encode_image", "decode_image", "SYNC_FREQ", "BLACK_FREQ", "WHITE_FREQ"]

SYNC_FREQ = 1200.0
BLACK_FREQ = 1500.0
WHITE_FREQ = 2300.0
DEFAULT_RATE = 16000


def _require():
    if np is None:
        raise ImportError("sstv needs numpy: pip install opentone[dsp]")
    if Image is None:
        raise ImportError("sstv needs Pillow: pip install opentone[image]")


def _lum_to_freq(lum: float) -> float:
    return BLACK_FREQ + (lum / 255.0) * (WHITE_FREQ - BLACK_FREQ)


def _freq_to_lum(freq: float) -> float:
    lum = (freq - BLACK_FREQ) / (WHITE_FREQ - BLACK_FREQ) * 255.0
    return max(0.0, min(255.0, lum))


def encode_image(image_path: str, file_path: str, width: int = 160,
                 height: int = 120, pixel_ms: float = 4.0, sync_ms: float = 5.0,
                 rate: int = DEFAULT_RATE) -> str:
    """Encode ``image_path`` as an SSTV-style FM signal to ``file_path``."""
    _require()
    img = Image.open(image_path).convert("L").resize((width, height))
    arr = np.asarray(img, dtype=float)

    px = max(1, int(rate * pixel_ms / 1000))
    sy = max(1, int(rate * sync_ms / 1000))

    # Per-sample frequency track, rendered with continuous phase.
    freqs = []
    for row in range(height):
        freqs.extend([SYNC_FREQ] * sy)
        for col in range(width):
            freqs.extend([_lum_to_freq(arr[row, col])] * px)

    phase = 0.0
    two_pi = 2 * math.pi
    out = []
    for f in freqs:
        phase += two_pi * f / rate
        out.append(int(math.sin(phase) * 32000))
    write_wav(out, file_path, rate)
    return file_path


def _instantaneous_freq(x, rate: int):
    # Analytic signal via FFT, then phase derivative.
    n = len(x)
    spectrum = np.fft.fft(x)
    h = np.zeros(n)
    if n % 2 == 0:
        h[0] = h[n // 2] = 1
        h[1:n // 2] = 2
    else:
        h[0] = 1
        h[1:(n + 1) // 2] = 2
    analytic = np.fft.ifft(spectrum * h)
    phase = np.unwrap(np.angle(analytic))
    inst = np.diff(phase) / (2 * np.pi) * rate
    return np.concatenate([inst[:1], inst])  # pad to length n


def decode_image(file_path: str, width: int = 160, height: int = 120,
                 pixel_ms: float = 4.0, sync_ms: float = 5.0,
                 rate: int = DEFAULT_RATE):
    """Decode an SSTV-style FM WAV back to a grayscale PIL Image."""
    _require()
    samples, file_rate = read_wav(file_path)
    rate = file_rate or rate
    x = np.asarray(samples, dtype=float)
    inst = _instantaneous_freq(x, rate)

    px = max(1, int(rate * pixel_ms / 1000))
    sy = max(1, int(rate * sync_ms / 1000))
    line_len = sy + width * px

    out = np.zeros((height, width), dtype=np.uint8)
    for row in range(height):
        base = row * line_len + sy
        for col in range(width):
            start = base + col * px
            block = inst[start:start + px]
            if len(block) == 0:
                continue
            # Trim transient edges of the pixel window before averaging.
            trim = max(1, len(block) // 4)
            core = block[trim:-trim] if len(block) > 2 * trim else block
            out[row, col] = int(round(_freq_to_lum(float(np.median(core)))))
    return Image.fromarray(out, mode="L")
