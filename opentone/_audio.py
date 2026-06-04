"""Shared audio primitives for the OpenTone data-over-sound schemes.

Pure standard library: WAV read/write, sine synthesis, and a single-frequency
Goertzel power estimate. Samples are plain Python ``int`` lists of signed 16-bit
PCM, mono.
"""
import math
import struct
import wave
from typing import List, Tuple

DEFAULT_RATE = 8000
PEAK = 32767  # signed 16-bit peak


def write_wav(samples: List[int], file_path: str, rate: int = DEFAULT_RATE) -> str:
    """Write signed 16-bit mono PCM ``samples`` to ``file_path``. Returns the path."""
    f = wave.open(file_path, "w")
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(rate)
    f.writeframes(struct.pack("<%dh" % len(samples),
                              *(_clip(s) for s in samples)))
    f.close()
    return file_path


def read_wav(file_path: str) -> Tuple[List[int], int]:
    """Read a mono 16-bit PCM WAV. Returns ``(samples, rate)``.

    Multi-channel input is downmixed to mono by taking the first channel.
    """
    f = wave.open(file_path, "r")
    try:
        rate = f.getframerate()
        channels = f.getnchannels()
        width = f.getsampwidth()
        if width != 2:
            raise ValueError("only 16-bit PCM WAV is supported")
        raw = f.readframes(f.getnframes())
    finally:
        f.close()
    all_samples = list(struct.unpack("<%dh" % (len(raw) // 2), raw))
    if channels > 1:
        all_samples = all_samples[::channels]
    return all_samples, rate


def _clip(value: int) -> int:
    if value > PEAK:
        return PEAK
    if value < -PEAK:
        return -PEAK
    return int(value)


def sine(freq: float, duration_ms: float, rate: int = DEFAULT_RATE,
         amplitude: float = 0.5) -> List[int]:
    """Return signed 16-bit samples of a sine tone."""
    n = int(rate * duration_ms / 1000)
    scale = amplitude * PEAK
    two_pi_f = 2 * math.pi * freq
    return [int(math.sin(two_pi_f * i / rate) * scale) for i in range(n)]


def sine_n(freq: float, n_samples: int, rate: int = DEFAULT_RATE,
           amplitude: float = 0.5) -> List[int]:
    """Return exactly ``n_samples`` samples of a sine tone.

    Sample-count (rather than duration) synthesis keeps a symbol an exact integer
    number of samples, which the demodulators rely on for bit alignment.
    """
    scale = amplitude * PEAK
    two_pi_f = 2 * math.pi * freq
    return [int(math.sin(two_pi_f * i / rate) * scale) for i in range(n_samples)]


def silence(duration_ms: float, rate: int = DEFAULT_RATE) -> List[int]:
    """Return ``duration_ms`` of silence."""
    return [0] * int(rate * duration_ms / 1000)


def goertzel_power(samples: List[int], freq: float, rate: int) -> float:
    """Normalised Goertzel power of ``freq`` over ``samples`` (0..~1).

    The result is the detected energy at ``freq`` divided by the block's total
    energy, so it is comparable across blocks of different amplitude.
    """
    n = len(samples)
    if n == 0:
        return 0.0
    k = 2.0 * math.cos(2.0 * math.pi * freq / rate)
    q1 = q2 = 0.0
    total = 0.0
    for s in samples:
        q0 = k * q1 - q2 + s
        q2 = q1
        q1 = q0
        total += s * s
    power = q1 * q1 + q2 * q2 - k * q1 * q2
    if total == 0:
        return 0.0
    # Normalise: Goertzel power scales with n^2, total energy with n.
    return power / (total * n)
