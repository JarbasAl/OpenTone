# Caller-ID

`opentone.callerid` builds the telephone caller-ID message formats, single-data
(SDMF) and multiple-data (MDMF), and carries them over the
[Bell 202 FSK modem](fsk.md).

SDMF carries the date, time, and number:

```python
from opentone import callerid
callerid.encode("call.wav", number="5551234567", timestamp="06041530")
callerid.decode("call.wav")
# {'format': 'SDMF', 'datetime': '06041530', 'number': '5551234567'}
```

MDMF also carries the caller name:

```python
callerid.encode("call.wav", number="5551234567", name="JARBAS AI",
                timestamp="06041530", mdmf=True)
callerid.decode("call.wav")
# {'format': 'MDMF', 'datetime': '06041530', 'number': '5551234567', 'name': 'JARBAS AI'}
```

`timestamp` is `MMDDHHMM`. A two's-complement checksum is appended on encode and
verified on decode. A tampered message raises `CallerIDError`.

`build_message` and `parse_message` expose the raw message bytes to carry them
over a different transport.

---
[← FSK modem](fsk.md) · [Home](index.md) · [MF signalling →](mf.md)
