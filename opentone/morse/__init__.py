"""Morse / CW — on-off-keyed tone encoding and decoding.

Encode text as International Morse code, render it as an on-off-keyed sine tone
to WAV, and recover it by tracking the tone envelope. Pure standard library.

An accessibility-friendly audio channel: text becomes a single steady tone keyed
on and off, decodable by ear or by machine.

    from opentone import morse

    morse.encode_text("HELLO", "hello.wav")
    morse.decode("hello.wav")            # "HELLO"
    morse.text_to_morse("SOS")           # "... --- ..."
"""
from typing import List

from opentone._audio import (DEFAULT_RATE, goertzel_power, read_wav, silence,
                             sine, write_wav)

__all__ = [
    "MORSE_CODE",
    "text_to_morse",
    "morse_to_text",
    "encode_text",
    "decode",
]

# International Morse code.
MORSE_CODE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
    ".": ".-.-.-", ",": "--..--", "?": "..--..", "'": ".----.", "!": "-.-.--",
    "/": "-..-.", "(": "-.--.", ")": "-.--.-", "&": ".-...", ":": "---...",
    ";": "-.-.-.", "=": "-...-", "+": ".-.-.", "-": "-....-", "_": "..--.-",
    '"': ".-..-.", "$": "...-..-", "@": ".--.-.",
}
_REVERSE = {v: k for k, v in MORSE_CODE.items()}


def text_to_morse(text: str) -> str:
    """Encode ``text`` to Morse. Letters are space-separated, words by ``/``."""
    words = []
    for word in text.upper().split():
        symbols = [MORSE_CODE[c] for c in word if c in MORSE_CODE]
        if symbols:
            words.append(" ".join(symbols))
    return " / ".join(words)


def morse_to_text(morse: str) -> str:
    """Decode a Morse string (``/`` between words) back to text."""
    out = []
    for word in morse.strip().split(" / "):
        letters = [_REVERSE.get(sym, "") for sym in word.split() if sym]
        out.append("".join(letters))
    return " ".join(out).strip()


def encode_text(text: str, file_path: str, wpm: int = 20, freq: float = 700.0,
                rate: int = DEFAULT_RATE) -> str:
    """Render ``text`` as on-off-keyed Morse tone to ``file_path``.

    Timing follows the PARIS standard: a dot is ``1200 / wpm`` ms, a dash three
    dots, intra-letter gap one dot, inter-letter gap three dots, word gap seven.
    """
    dot_ms = 1200.0 / wpm
    samples: List[int] = []
    morse = text_to_morse(text)
    words = morse.split(" / ")
    for w, word in enumerate(words):
        if w:
            samples += silence(dot_ms * 7, rate)
        letters = word.split(" ")
        for li, letter in enumerate(letters):
            if li:
                samples += silence(dot_ms * 3, rate)
            for si, sym in enumerate(letter):
                if si:
                    samples += silence(dot_ms, rate)
                samples += sine(freq, dot_ms * (3 if sym == "-" else 1), rate)
    write_wav(samples, file_path, rate)
    return file_path


def decode(file_path: str, freq: float = 700.0, wpm: int = 20) -> str:
    """Decode an on-off-keyed Morse WAV at ``freq`` back to text.

    ``wpm`` sets the expected dot length; tone/gap runs are quantised against it.
    """
    samples, rate = read_wav(file_path)
    dot_samples = max(1, int(rate * (1200.0 / wpm) / 1000))
    win = max(1, dot_samples // 4)

    # Tone-presence envelope over short windows.
    present: List[bool] = []
    for i in range(0, len(samples) - win, win):
        block = samples[i:i + win]
        present.append(goertzel_power(block, freq, rate) > 0.02)

    # Run-length encode the envelope into (is_tone, length_in_windows).
    runs = []
    for p in present:
        if runs and runs[-1][0] == p:
            runs[-1][1] += 1
        else:
            runs.append([p, 1])

    windows_per_dot = max(1, dot_samples // win)
    morse = ""
    for is_tone, length in runs:
        units = length / windows_per_dot
        if is_tone:
            morse += "-" if units >= 2 else "."
        else:
            if units >= 5:
                morse += " / "
            elif units >= 2:
                morse += " "
            # shorter gap = intra-letter, no separator
    return morse_to_text(morse)
