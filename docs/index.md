# OpenTone

A data-over-sound toolkit in pure Python. OpenTone carries data through an audio
channel using a family of schemes, each in its own submodule and sharing the WAV
/ synthesis / Goertzel primitives in `opentone._audio`. The core schemes have no
dependencies; the image and DSP schemes use their optional extras.

## Schemes

- [DTMF](encoding.md) — telephone-keypad tones. See also [decoding](decoding.md)
  and the [DTMF reference](dtmf-reference.md).
- [Morse](morse.md) — CW on-off keying.
- [FSK modem](fsk.md) — bytes over Bell 202 frequency-shift keying.
- [Caller-ID](callerid.md) — Bell 202 SDMF / MDMF messages.
- [MF signalling](mf.md) — multi-frequency 2-of-6 (R1).
- [Error correction](fec.md) — Reed-Solomon, shared by the modems.
- [SSTV](sstv.md) — slow-scan-TV image transmission *(extra: `image`, `dsp`)*.
- [Spectrogram art](spectrogram.md) — paint an image into the spectrogram
  *(extra: `image`, `dsp`)*.
- [Watermarking](watermark.md) — hide data in existing audio *(extra: `dsp`)*.

## Install

```bash
pip install opentone        # core, no dependencies
pip install opentone[all]   # + numpy, Pillow for the image/DSP schemes
```

## Uses

DTMF, Morse, FSK and MF are robust ways to move small amounts of data — or a
short URL or code — over an audio channel between devices, or as an accessibility
cue carried in sound. SSTV and spectrogram art carry images; watermarking hides a
payload inside other audio.
