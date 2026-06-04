# OpenTone — agent onboarding

A data-over-sound toolkit in pure Python: a family of schemes that carry data
through an audio channel, each in its own submodule, sharing the WAV / synthesis
/ Goertzel primitives in `opentone/_audio.py`. The core schemes are stdlib-only;
the image/DSP schemes use optional extras.

**Org:** JarbasAl / **Branch:** dev (work) / master (stable)

## Layout

| Path | Purpose |
|------|---------|
| `opentone/_audio.py` | Shared WAV read/write, sine synthesis, Goertzel power |
| `opentone/dtmf.py` | DTMF tones; re-exported at top level (`from opentone import ToneGenerator`) |
| `opentone/morse/` | Morse / CW on-off keying |
| `opentone/fsk/` | Bell 202 FSK soft-modem (bytes; optional Reed-Solomon) |
| `opentone/callerid/` | Bell 202 caller-ID (SDMF/MDMF) over the FSK modem |
| `opentone/mf/` | Multi-frequency (R1) 2-of-6 signalling |
| `opentone/fec/` | Reed-Solomon GF(256) — shared error correction |
| `opentone/sstv/` | Slow-scan-TV grayscale FM image transmission (`image`,`dsp` extras) |
| `opentone/spectrogram/` | Image painted into the spectrogram (`image`,`dsp` extras) |
| `opentone/watermark/` | Spread-spectrum audio watermarking (`dsp` extra) |
| `opentone/version.py` | Version block — bumped by CI, never edit by hand |
| `docs/` | One markdown page per scheme |
| `examples/` | Runnable scripts + bundled WAV fixtures |
| `test/` | Offline pytest suite (one `test_<scheme>.py` per module) |

## Conventions

- The core schemes (dtmf, morse, fsk, callerid, mf, fec) must stay dependency
  free. numpy / Pillow only inside sstv, spectrogram, watermark, behind the
  `dsp` / `image` extras and an informative ImportError.
- New tone schemes should build on `opentone/_audio.py` (use `sine_n` for
  sample-accurate symbols — bit/symbol alignment depends on it).
- Tests are offline and deterministic. Image/DSP tests `pytest.importorskip`
  their extras.
- Versions bump automatically from conventional-commit prefixes — never edit
  `opentone/version.py`.
- CI is the shared `OpenVoiceOS/gh-automations` reusable workflows, at `@dev`.

## Run

```bash
pip install -e .[test]
pytest -q
```
