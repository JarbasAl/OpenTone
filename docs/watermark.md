# Watermarking

`opentone.watermark` hides a payload inside an existing audio file with a
spread-spectrum watermark. The host audio is split into one segment per payload
bit, and a key-seeded pseudo-random sequence is added to (bit `1`) or subtracted
from (bit `0`) each segment. Extraction differences each segment to suppress the
host, then correlates against the same sequence, so the payload comes back
without the original host.

Requires the `dsp` (numpy) extra.

```python
from opentone import watermark

watermark.embed("song.wav", "marked.wav", b"owner-id", key=12345)
watermark.extract("marked.wav", 8, key=12345)   # b"owner-id"
```

`alpha` sets the watermark strength relative to the host (default keeps it
roughly 20 dB below the signal, so it stays subtle). A larger payload needs a
longer host, since each bit needs its own segment, and `embed` raises
`WatermarkError` if the host is too short. The watermark survives mild noise but
is not a strong cryptographic mark. Keep `key` secret to make the sequence
unpredictable.

---
[← Spectrogram art](spectrogram.md) · [Home](index.md) · [API reference →](api-reference.md)
