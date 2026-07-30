"""Encode text as Morse audio and decode it back."""
import tempfile

from opentone import morse

text = "SOS HELLO WORLD"
wav = tempfile.mktemp(suffix=".wav")
morse.encode_text(text, wav, wpm=20)
print("morse:", morse.text_to_morse(text))
print("decoded:", morse.decode(wav, wpm=20))
