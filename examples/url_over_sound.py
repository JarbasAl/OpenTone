"""Carry a short URL over an audio channel.

DTMF is a robust way to hand a short string from one device to another over
sound. Keep the payload short — every character becomes two DTMF tones — so a
URL shortener pairs well with this in practice.
"""
import tempfile

from opentone import encode_text, decode

url = "tinyurl.com/abc123"

wav = tempfile.mktemp(suffix=".wav")
encode_text(url, wav)
print(f"encoded {url!r} -> {wav}")
print("play this WAV near another device running the decoder")

recovered = decode(wav)
print(f"decoded -> {recovered!r}")
assert recovered == url
