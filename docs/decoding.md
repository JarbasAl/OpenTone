# Decoding

`decode` (or `ToneDecoder.decode_wave`) runs a Goertzel detector over a WAV file
and returns the recovered string.

```python
from opentone import decode

decode("message.wav")                    # hex layer on → original text
decode("dial.wav", hex_decode=False)     # raw DTMF symbols
```

## Sample rate

The decoder must be told the sample rate of the input. OpenTone's own encoder
writes 8 kHz, but the default decoder assumes 16 kHz to suit higher-rate
recordings, so match the rate to your source:

```python
decode("out.wav", sample_rate=8000)
```

To decode audio captured elsewhere, convert it to mono 16-bit PCM first:

```bash
ffmpeg -i some_file.mp3 -acodec pcm_s16le -ac 1 -ar 8000 out.wav
```

## Tuning for noisy input

Three parameters trade sensitivity against false positives:

- `sample_rate`: must match the WAV.
- `goertzel_n`: Goertzel block size. Smaller windows react faster to short
  tones, useful for tight phone recordings. Larger windows are more selective.
- `min_consecutive`: how many identical detections in a row are required before
  a symbol is accepted. Lower it for short tones, raise it to reject noise.

```python
from opentone import ToneDecoder

# tighter, noisier phone-rate recording
dec = ToneDecoder(sample_rate=8000, goertzel_n=92,
                  min_consecutive=3, hex_decode=False)
print(dec.decode_wave("phonecall.wav"))
```

Real-world phone audio can decode imperfectly. Clean, encoder-generated WAV
round-trips exactly.

## Telephone E and F

On a physical keypad the symbols that OpenTone calls `E` and `F` correspond to
`*` and `#`. When decoding phone recordings you may want to map them back:

```python
text = decode("phonecall.wav", sample_rate=8000, goertzel_n=92,
              min_consecutive=3, hex_decode=False)
text = text.replace("E", "*").replace("F", "#")
```

---
[← Encoding](encoding.md) · [Home](index.md) · [DTMF reference →](dtmf-reference.md)
