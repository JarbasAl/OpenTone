"""Spectrogram art — paint an image into the spectrogram of an audio file.

Each image column becomes a short time slice and each row a frequency band:
pixel brightness sets the amplitude of an additive sine at that frequency. Play
the result through a spectrogram view (or :func:`spectrogram`) and the picture
appears. Requires the ``dsp`` (numpy) and ``image`` (Pillow) extras.

    from opentone import spectrogram

    spectrogram.encode_image("logo.png", "logo.wav")
    mag = spectrogram.spectrogram("logo.wav")   # 2D numpy magnitude array
"""
from opentone._audio import DEFAULT_RATE, read_wav, write_wav

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

__all__ = ["encode_image", "spectrogram"]


def _require():
    if np is None:
        raise ImportError("spectrogram needs numpy: pip install opentone[dsp]")
    if Image is None:
        raise ImportError("spectrogram needs Pillow: pip install opentone[image]")


def encode_image(image_path: str, file_path: str, duration: float = 4.0,
                 height: int = 128, width: int = 200, f_min: float = 500.0,
                 f_max: float = 3500.0, rate: int = DEFAULT_RATE) -> str:
    """Render ``image_path`` into the spectrogram of ``file_path``; return the path."""
    _require()
    img = Image.open(image_path).convert("L").resize((width, height))
    arr = np.asarray(img, dtype=float) / 255.0
    arr = arr[::-1]  # row 0 -> lowest frequency (spectrograms put low freq at bottom)

    n = int(duration * rate)
    col_len = max(1, n // width)
    freqs = np.linspace(f_min, f_max, height)
    rng = np.random.default_rng(0)
    phases = rng.uniform(0, 2 * np.pi, height)  # avoid coherent peaks
    t = np.arange(col_len) / rate

    out = np.zeros(width * col_len)
    basis = np.sin(2 * np.pi * np.outer(freqs, t) + phases[:, None])  # (height, col_len)
    for c in range(width):
        out[c * col_len:(c + 1) * col_len] = arr[:, c] @ basis

    peak = np.max(np.abs(out)) or 1.0
    samples = (out / peak * 32000).astype(int).tolist()
    write_wav(samples, file_path, rate)
    return file_path


def spectrogram(file_path: str, n_fft: int = 512, hop: int = 256):
    """Return the magnitude spectrogram of ``file_path`` as a 2D numpy array
    (rows = frequency low→high, columns = time)."""
    _require()
    samples, rate = read_wav(file_path)
    x = np.asarray(samples, dtype=float)
    window = np.hanning(n_fft)
    cols = []
    for start in range(0, len(x) - n_fft, hop):
        frame = x[start:start + n_fft] * window
        cols.append(np.abs(np.fft.rfft(frame)))
    if not cols:
        return np.zeros((n_fft // 2 + 1, 0))
    return np.array(cols).T
