# OpenTone — agent onboarding

DTMF tone encoding and decoding in pure Python. Render text or dial strings to
the touch-tone signals of a telephone keypad, write them to WAV, and recover
them with a Goertzel detector. Standard library only, no runtime dependencies.

**Org:** JarbasAl / **Branch:** dev (work) / master (stable)

## Key sources

| File | Purpose |
|------|---------|
| `opentone/__init__.py` | Public API: `ToneGenerator`, `ToneDecoder`, `encode_text`, `encode_dtmf`, `decode` |
| `opentone/version.py` | Version block — bumped by CI, never edit by hand |
| `docs/` | Markdown docs (index, quickstart, encoding, decoding, DTMF reference, API) |
| `examples/` | Runnable scripts + bundled WAV fixtures (`0123456789.wav`, `phonecall.wav`) |
| `test/` | Offline pytest suite using the bundled fixtures |

## How it works

- **Encode:** text is hex-encoded byte-by-byte into the `0-9A-F` DTMF alphabet,
  then each symbol is rendered as the sum of its row + column sine tones to an
  8 kHz mono 16-bit WAV. Dial strings skip the hex layer.
- **Decode:** a Goertzel detector evaluates the eight DTMF frequencies over the
  samples, run-length-collapses the detections into symbols, and (for the hex
  path) decodes them back to ASCII.

## Conventions

- Pure stdlib — do not add runtime dependencies.
- The decode hex path lowercases internally; raw symbol output is uppercase
  `0-9A-F`. Keep both paths intact when touching `decode_wave`.
- Tests are offline and must stay that way (use the bundled WAV fixtures).
- Versions bump automatically from conventional-commit prefixes — never edit
  `opentone/version.py`.
- CI is the shared `OpenVoiceOS/gh-automations` reusable workflows, referenced
  at `@dev`.

## Run

```bash
pip install -e .[test]
pytest -q
```
