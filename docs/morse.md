# Morse / CW

`opentone.morse` encodes text as International Morse code, renders it as an
on-off-keyed sine tone, and recovers it by tracking the tone envelope. An
accessibility-friendly channel: text becomes a single steady tone keyed on and
off, readable by ear or machine.

## Text

```python
from opentone import morse

morse.text_to_morse("SOS")     # "... --- ..."
morse.morse_to_text("... --- ...")   # "SOS"
```

Letters are space-separated; words are separated by ` / `.

## Audio

```python
morse.encode_text("HELLO WORLD", "hello.wav", wpm=20, freq=700)
morse.decode("hello.wav", wpm=20, freq=700)   # "HELLO WORLD"
```

Timing follows the PARIS standard: a dot is `1200 / wpm` milliseconds, a dash
three dots, the intra-letter gap one dot, the inter-letter gap three, and the
word gap seven. Decode with the same `wpm` and tone `freq` used to encode.
