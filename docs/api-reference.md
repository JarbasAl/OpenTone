# API reference

## Convenience functions

```python
encode_text(text, file_path, duration=100, pause=500) -> str
```
Hex-encode `text` and write it as DTMF tones to `file_path`. Returns `file_path`.

```python
encode_dtmf(dtmf, file_path, duration=100, pause=500) -> str
```
Write a literal DTMF dial string (`0-9A-F`) as tones to `file_path`. Returns
`file_path`.

```python
decode(file_path, sample_rate=16000, goertzel_n=210,
       min_consecutive=6, hex_decode=True) -> str
```
Decode the DTMF content of `file_path`. With `hex_decode=True` the symbols are
treated as hex and the original ASCII text is returned; with `hex_decode=False`
the raw symbols are returned.

## `ToneGenerator(duration=100, pause=500)`

Render text or DTMF strings to tones.

- `hex_encode(text) -> str` *(static)* — hex-encode ASCII into `0-9A-F`.
- `generate_tone(f1, f2, duration_in_ms) -> list[int]` — samples for one
  dual-frequency tone plus trailing pause.
- `encode_to_wave(text, file_path)` — hex-encode `text` and write tones.
- `dtmf_to_wave(dtmf, file_path)` — write a literal dial string as tones.

Class attributes: `SAMPLE_RATE` (8000), `SAMPLE_WIDTH`, `NUMBER_OF_CHANNELS`,
`frequencyR`, `frequencyC`, `FREQUENCY_MAPPINGS`.

## `ToneDecoder(sample_rate=16000, goertzel_n=210, min_consecutive=6, hex_decode=True)`

Recover a DTMF string from a WAV file.

- `decode_wave(filename) -> str` — decode and return the recovered string.
- `hex_decode(hex_encoded) -> str` *(static)* — decode hex back to ASCII.
- `reset()` — clear detector state for a fresh decode.
- `goertzel(sample)` — feed one 16-bit signed sample to the detector.

See [Decoding](decoding.md) for parameter tuning.
