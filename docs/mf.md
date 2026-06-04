# MF signalling

`opentone.mf` implements multi-frequency (R1) inter-register signalling — the
2-of-6 tone scheme once used between telephone exchanges. Each symbol is the sum
of two of six frequencies (700, 900, 1100, 1300, 1500, 1700 Hz), including the KP
(start) and ST (end) control symbols.

```python
from opentone import mf

mf.encode(["KP", "5", "5", "5", "1", "2", "3", "4", "ST"], "mf.wav")
mf.decode("mf.wav")        # ['KP','5','5','5','1','2','3','4','ST']

mf.encode("0123456789", "digits.wav")   # a bare digit string also works
```

The symbol set (`mf.MF_SYMBOLS`) is the ten digits plus the control symbols
`KP`, `KP2`, `ST`, `ST2`, `ST3`. Decoding detects each tone with a 2-of-6
Goertzel detector and maps the strongest frequency pair back to its symbol.
