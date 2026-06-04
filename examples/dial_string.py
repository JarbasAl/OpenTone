"""Encode a literal DTMF dial string (no hex layer) and decode it back."""
import tempfile

from opentone import encode_dtmf, decode

dial = "0123456789"

wav = tempfile.mktemp(suffix=".wav")
encode_dtmf(dial, wav)
print(f"encoded dial string {dial!r} -> {wav}")

recovered = decode(wav, hex_decode=False)
print(f"decoded -> {recovered!r}")
assert recovered == dial
