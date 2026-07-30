# FSK modem

`opentone.fsk` is a Bell 202 style frequency-shift-keying soft-modem. A `1` bit
is the mark tone (1200 Hz), a `0` bit the space tone (2200 Hz), one bit per baud
period. Arbitrary bytes go in and come back out.

```python
from opentone import fsk

fsk.encode(b"arbitrary bytes \x00\xff", "data.wav")
fsk.decode("data.wav")          # b"arbitrary bytes \x00\xff"
```

## Frame

A leading run of mark bits lets the receiver find the carrier. A single space
start-bit marks the first data bit, and a two-byte big-endian length header
delimits the payload, so the decoder needs no manual framing.

## Error correction

Pass `nsym > 0` to protect the payload with Reed-Solomon (`opentone.fec`). The
decoder must use the same `nsym`:

```python
fsk.encode(b"resilient payload", "data.wav", nsym=12)
fsk.decode("data.wav", nsym=12)   # survives byte errors from a noisy channel
```

With `nsym` parity bytes, each Reed-Solomon block tolerates up to `nsym // 2`
byte errors. See [error correction](fec.md).

## Tuning

`baud` trades speed against noise tolerance. `mark` and `space` set the tones,
and `rate` sets the sample rate. Lower baud means more samples per bit and a
more forgiving decode.

---
[← Morse](morse.md) · [Home](index.md) · [Caller-ID →](callerid.md)
