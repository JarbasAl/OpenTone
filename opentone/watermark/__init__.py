"""Audio watermarking — hide data inside an existing audio file.

A spread-spectrum watermark: the host audio is split into one segment per payload
bit, and a key-seeded pseudo-random sequence is added (or subtracted) to each
segment to carry that bit. Extraction correlates each segment against the same
sequence, so the payload is recovered without the original host. Requires the
``dsp`` (numpy) extra.

    from opentone import watermark

    watermark.embed("song.wav", "marked.wav", b"owner-id")
    watermark.extract("marked.wav", 8)        # b"owner-id"

The watermark is robust to mild noise but is not a strong cryptographic mark; use
a secret ``key`` to make the sequence unpredictable.
"""
from opentone._audio import read_wav, write_wav

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

__all__ = ["embed", "extract", "WatermarkError"]


class WatermarkError(Exception):
    """Raised when the host audio is too short for the payload."""


def _require():
    if np is None:
        raise ImportError("watermark needs numpy: pip install opentone[dsp]")


def _bits(data: bytes):
    return [(byte >> i) & 1 for byte in data for i in range(8)]


def _unbits(bits) -> bytes:
    out = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte |= int(bits[i + j]) << j
        out.append(byte)
    return bytes(out)


def _sequence(key: int, index: int, length: int):
    rng = np.random.default_rng((key << 20) ^ index)
    return rng.standard_normal(length)


def embed(host_path: str, out_path: str, data: bytes, key: int = 12345,
          alpha: float = 0.05) -> str:
    """Embed ``data`` into ``host_path`` and write to ``out_path``; return the path."""
    _require()
    samples, rate = read_wav(host_path)
    x = np.asarray(samples, dtype=float)
    bits = _bits(data)
    if not bits:
        write_wav(samples, out_path, rate)
        return out_path
    seg = len(x) // len(bits)
    if seg < 16:
        raise WatermarkError("host audio too short for this payload")

    strength = alpha * (np.std(x) or 1.0)
    for i, bit in enumerate(bits):
        s = i * seg
        sign = 1.0 if bit else -1.0
        x[s:s + seg] += sign * strength * _sequence(key, i, seg)

    np.clip(x, -32767, 32767, out=x)
    write_wav(x.astype(int).tolist(), out_path, rate)
    return out_path


def extract(file_path: str, n_bytes: int, key: int = 12345) -> bytes:
    """Recover ``n_bytes`` of payload from a watermarked file."""
    _require()
    samples, _ = read_wav(file_path)
    x = np.asarray(samples, dtype=float)
    n_bits = n_bytes * 8
    if n_bits == 0:
        return b""
    seg = len(x) // n_bits
    bits = []
    for i in range(n_bits):
        s = i * seg
        # Difference both signals first: this high-pass suppresses the (mostly
        # low-frequency) host energy while preserving the white PN sequence,
        # lifting the correlator SNR well above raw correlation.
        d_seg = np.diff(x[s:s + seg])
        d_pn = np.diff(_sequence(key, i, seg))
        corr = float(np.dot(d_seg, d_pn))
        bits.append(1 if corr > 0 else 0)
    return _unbits(bits)
