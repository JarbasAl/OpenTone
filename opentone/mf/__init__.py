"""MF — multi-frequency (R1) inter-register signalling.

The 2-of-6 tone scheme once used between telephone exchanges: each symbol is the
sum of two of six frequencies (700, 900, 1100, 1300, 1500, 1700 Hz), including the
KP (start) and ST (end) control symbols. Encode a symbol sequence to tones and
recover it with a 2-of-6 Goertzel detector. Pure standard library.

    from opentone import mf

    mf.encode(["KP", "5", "5", "5", "1", "2", "3", "4", "ST"], "mf.wav")
    mf.decode("mf.wav")          # ['KP','5','5','5','1','2','3','4','ST']
    mf.encode("0123456789", "digits.wav")   # a bare digit string also works
"""
from typing import Dict, FrozenSet, List, Sequence, Union

from opentone._audio import (DEFAULT_RATE, goertzel_power, read_wav, silence,
                             sine_n, write_wav)

__all__ = ["encode", "decode", "FREQUENCIES", "MF_SYMBOLS"]

FREQUENCIES = [700, 900, 1100, 1300, 1500, 1700]

# symbol -> the two frequency indices that compose it (all 15 2-of-6 combos).
_PAIRS = {
    "1": (0, 1), "2": (0, 2), "3": (1, 2), "4": (0, 3), "5": (1, 3),
    "6": (2, 3), "7": (0, 4), "8": (1, 4), "9": (2, 4), "0": (3, 4),
    "ST3": (0, 5), "ST2": (1, 5), "KP": (2, 5), "KP2": (3, 5), "ST": (4, 5),
}
MF_SYMBOLS = list(_PAIRS)
_BY_PAIR: Dict[FrozenSet[int], str] = {frozenset(v): k for k, v in _PAIRS.items()}


def encode(symbols: Union[str, Sequence[str]], file_path: str, tone_ms: float = 68,
           gap_ms: float = 68, rate: int = DEFAULT_RATE) -> str:
    """Encode ``symbols`` to MF tones. A plain string is treated as digits."""
    seq = list(symbols) if isinstance(symbols, str) else list(symbols)
    n_tone = int(rate * tone_ms / 1000)
    out: List[int] = []
    for sym in seq:
        if sym not in _PAIRS:
            raise ValueError("unknown MF symbol %r" % sym)
        a, b = _PAIRS[sym]
        tone_a = sine_n(FREQUENCIES[a], n_tone, rate, amplitude=0.4)
        tone_b = sine_n(FREQUENCIES[b], n_tone, rate, amplitude=0.4)
        out += [x + y for x, y in zip(tone_a, tone_b)]
        out += silence(gap_ms, rate)
    write_wav(out, file_path, rate)
    return file_path


def _rms(block: List[int]) -> float:
    if not block:
        return 0.0
    return (sum(s * s for s in block) / len(block)) ** 0.5


def decode(file_path: str, tone_ms: float = 68) -> List[str]:
    """Decode an MF WAV into its symbol sequence."""
    samples, rate = read_wav(file_path)
    win = max(1, int(rate * tone_ms / 1000) // 4)

    # Envelope: which windows carry a tone.
    windows = [samples[i:i + win] for i in range(0, len(samples) - win + 1, win)]
    if not windows:
        return []
    rms = [_rms(w) for w in windows]
    threshold = 0.2 * max(rms)

    # Group consecutive above-threshold windows into tone runs.
    runs = []
    cur = []
    for idx, level in enumerate(rms):
        if level > threshold:
            cur.append(idx)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)

    out = []
    for run in runs:
        mid = run[len(run) // 2]
        block = windows[mid]
        powers = [goertzel_power(block, f, rate) for f in FREQUENCIES]
        top2 = frozenset(sorted(range(6), key=lambda i: powers[i])[-2:])
        sym = _BY_PAIR.get(top2)
        if sym:
            out.append(sym)
    return out
