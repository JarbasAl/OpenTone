"""Decode the bundled 8 kHz phone recordings.

The recordings are real touch-tone audio, decoded at the phone sample rate with
a smaller Goertzel window and a low consecutive-detection threshold.
"""
from os.path import dirname, join

from opentone import decode

here = dirname(__file__)

# Clean 8 kHz tones.
clean = decode(join(here, "0123456789.wav"), sample_rate=8000,
               min_consecutive=2, hex_decode=False)
print("0123456789.wav ->", clean)

# Noisier phone call; E/F map to the keypad * and # symbols.
noisy = decode(join(here, "phonecall.wav"), sample_rate=8000, goertzel_n=92,
               min_consecutive=3, hex_decode=False)
noisy = noisy.replace("E", "*").replace("F", "#")
print("phonecall.wav  ->", noisy)
