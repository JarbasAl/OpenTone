"""Encode ASCII text to DTMF tones and decode it back."""
import tempfile

from opentone import encode_text, decode

message = "hello world"

wav = tempfile.mktemp(suffix=".wav")
encode_text(message, wav)
print(f"encoded {message!r} -> {wav}")

recovered = decode(wav)
print(f"decoded -> {recovered!r}")
assert recovered == message
