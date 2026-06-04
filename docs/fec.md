# Error correction

`opentone.fec` is a small, dependency-free Reed-Solomon coder over GF(256), used
by the modem schemes to survive a noisy audio channel.

```python
from opentone.fec import rs_encode, rs_decode

code = rs_encode(b"hello world", nsym=10)   # payload + 10 parity bytes
rs_decode(code, nsym=10)                     # b"hello world"
```

`nsym` parity bytes per block correct up to `nsym // 2` byte errors. Messages
longer than `255 - nsym` bytes are split into RS(255) blocks transparently. A
block with more errors than the parity can correct raises `ReedSolomonError`.

The [FSK modem](fsk.md) wires this in directly via its `nsym` argument, so most
callers never use `opentone.fec` on its own.
