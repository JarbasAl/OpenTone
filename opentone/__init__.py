"""OpenTone — a data-over-sound toolkit in pure Python.

A family of schemes for carrying data through an audio channel, each in its own
submodule and sharing the WAV / synthesis / Goertzel primitives in
:mod:`opentone._audio`:

- :mod:`opentone.dtmf` — telephone-keypad DTMF tones (also re-exported here for
  backwards compatibility: ``from opentone import ToneGenerator``).
- :mod:`opentone.morse` — Morse / CW on-off keying.
- :mod:`opentone.fsk` — Bell 103/202 frequency-shift-keying soft-modem.
- :mod:`opentone.callerid` — Bell 202 caller-ID (SDMF / MDMF) framing.
- :mod:`opentone.mf` — multi-frequency (MF / R1) inter-register signalling.
- :mod:`opentone.fec` — Reed-Solomon forward error correction (shared).
- :mod:`opentone.sstv` — slow-scan TV image transmission *(extra: ``image``)*.
- :mod:`opentone.spectrogram` — render an image into a spectrogram *(extra: ``dsp``)*.
- :mod:`opentone.watermark` — spread-spectrum audio watermarking *(extra: ``dsp``)*.

The pure-stdlib core (dtmf, morse, fsk, callerid, mf, fec) imports with no
dependencies. The image/DSP schemes require their optional extras.
"""
from opentone.version import __version__

# Backwards-compatible top-level DTMF API.
from opentone.dtmf import (
    ToneGenerator,
    ToneDecoder,
    encode_text,
    encode_dtmf,
    decode,
)

__all__ = [
    "ToneGenerator",
    "ToneDecoder",
    "encode_text",
    "encode_dtmf",
    "decode",
    "__version__",
]
