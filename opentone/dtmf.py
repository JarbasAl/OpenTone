"""DTMF — dual-tone multi-frequency (telephone keypad) encoding and decoding.

Render text or a dial string to the DTMF tones of a telephone keypad, write them
to WAV, and recover them with a Goertzel detector. Standard library only.

Text is carried by hex-encoding each byte and emitting the hex digits as DTMF
symbols (``0-9`` plus ``A-F``), so arbitrary ASCII survives a round trip. Pass a
literal dial string instead to stay in the 16-symbol DTMF alphabet.
"""
import math
import struct
import wave
from typing import List

__all__ = [
    "ToneGenerator",
    "ToneDecoder",
    "encode_text",
    "encode_dtmf",
    "decode",
]


class ToneGenerator:
    """Render text or DTMF strings to DTMF tones in a WAV file.

    :param duration: tone length per symbol, in milliseconds.
    :param pause: silence inserted after each tone, in milliseconds.
    """

    SAMPLE_RATE = 8000  # hz
    SAMPLE_WIDTH = 2
    NUMBER_OF_CHANNELS = 1
    COMPRESSION_TYPE = "NONE"
    COMPRESSION_NAME = "Uncompressed"

    # Frequency rows & columns of the standard DTMF grid.
    frequencyR = [697, 770, 852, 941]
    frequencyC = [1209, 1336, 1477, 1633]

    FREQUENCY_MAPPINGS = {
        "0": [frequencyR[3], frequencyC[1]],
        "1": [frequencyR[0], frequencyC[0]],
        "2": [frequencyR[0], frequencyC[1]],
        "3": [frequencyR[0], frequencyC[2]],
        "4": [frequencyR[1], frequencyC[0]],
        "5": [frequencyR[1], frequencyC[1]],
        "6": [frequencyR[1], frequencyC[2]],
        "7": [frequencyR[2], frequencyC[0]],
        "8": [frequencyR[2], frequencyC[1]],
        "9": [frequencyR[2], frequencyC[2]],
        "A": [frequencyR[0], frequencyC[3]],
        "B": [frequencyR[1], frequencyC[3]],
        "C": [frequencyR[2], frequencyC[3]],
        "D": [frequencyR[3], frequencyC[3]],
        "E": [frequencyR[3], frequencyC[0]],
        "F": [frequencyR[3], frequencyC[2]],
    }

    def __init__(self, duration: int = 100, pause: int = 500):
        self.duration = duration
        self.pause = pause

    @staticmethod
    def hex_encode(text_to_encode: str) -> str:
        """Hex-encode ASCII text into the DTMF-safe ``0-9A-F`` alphabet."""
        return text_to_encode.encode(encoding="ascii").hex()

    def _generate_raw_data(self, text_to_encode: str) -> List[int]:
        data: List[int] = []
        sequence = [(s, self.duration) for s in text_to_encode.upper()]
        for key, tone_duration in sequence:
            f1, f2 = self.FREQUENCY_MAPPINGS[key]
            data += self.generate_tone(f1, f2, tone_duration)
        return data

    def _save_wave_file(self, raw_data: List[int], file_path: str) -> None:
        f = wave.open(file_path, "w")
        f.setnchannels(self.NUMBER_OF_CHANNELS)
        f.setsampwidth(self.SAMPLE_WIDTH)
        f.setframerate(self.SAMPLE_RATE)
        f.setnframes(len(raw_data))
        f.setcomptype(self.COMPRESSION_TYPE, self.COMPRESSION_NAME)
        for i in raw_data:
            f.writeframes(struct.pack("i", i))
        f.close()

    def _get_silence(self, duration_in_ms: int = None) -> List[int]:
        if duration_in_ms is None:
            duration_in_ms = self.pause
        number_of_samples = int(self.SAMPLE_RATE * duration_in_ms / 1000)
        return [0] * number_of_samples

    def generate_tone(self, f1: int, f2: int, duration_in_ms: int) -> List[int]:
        """Return the samples for a single dual-frequency tone plus trailing pause."""
        number_of_samples = int(self.SAMPLE_RATE * duration_in_ms / 1000)
        scale = 32767  # signed 16-bit peak

        result = []
        for i in range(number_of_samples):
            p = i * 1.0 / self.SAMPLE_RATE
            result.append(int((math.sin(p * f1 * math.pi * 2) +
                               math.sin(p * f2 * math.pi * 2)) / 2 * scale))
        return result + self._get_silence()

    def encode_to_wave(self, text_to_encode: str, file_path: str) -> None:
        """Hex-encode ``text_to_encode`` and write it as DTMF tones to ``file_path``."""
        hex_encoded = self.hex_encode(text_to_encode)
        raw_data = self._generate_raw_data(hex_encoded)
        self._save_wave_file(raw_data, file_path)

    def dtmf_to_wave(self, dtmf, file_path: str) -> None:
        """Write a literal DTMF dial string (``0-9A-F``) as tones to ``file_path``."""
        raw_data = self._generate_raw_data(str(dtmf))
        self._save_wave_file(raw_data, file_path)


class ToneDecoder:
    """Recover a DTMF string from a WAV file with a Goertzel detector.

    :param sample_rate: sample rate the detector assumes for the input WAV.
    :param goertzel_n: Goertzel block size (samples per evaluation window).
    :param min_consecutive: identical detections required to accept a symbol.
    :param hex_decode: when ``True``, treat the decoded symbols as hex and
        return the original ASCII text; when ``False``, return the raw symbols.
    """

    def __init__(self, sample_rate: int = 16000, goertzel_n: int = 210,
                 min_consecutive: int = 6, hex_decode: bool = True):
        self.max_bins = 8
        self.goertzel_n = goertzel_n
        self.sample_rate = sample_rate

        # The DTMF frequencies we're looking for.
        self.freqs = ToneGenerator.frequencyR + ToneGenerator.frequencyC
        self.coefs = [0] * self.max_bins

        self.reset()
        self._calc_coeffs()

        self.min_consecutive = min_consecutive
        self.decode = hex_decode

    def reset(self) -> None:
        """Clear all detector state for a fresh decode."""
        self.sample_index = 0
        self.sample_count = 0
        self.q1 = [0] * self.max_bins
        self.q2 = [0] * self.max_bins
        self.r = [0] * self.max_bins
        # characters seen so far, with the time they were seen
        self.characters = []
        self.decoded = ""

    def _postprocess(self) -> None:
        # Decide whether the current window holds a valid DTMF symbol.
        row = 0
        col = 0
        maxval = 0.0

        row_col_ascii_codes = [["1", "2", "3", "A"], ["4", "5", "6", "B"],
                               ["7", "8", "9", "C"], ["E", "0", "F", "D"]]

        # Find the largest in the row group.
        for i in range(4):
            if self.r[i] > maxval:
                maxval = self.r[i]
                row = i

        # Find the largest in the column group.
        maxval = 0
        for i in range(4, 8):
            if self.r[i] > maxval:
                maxval = self.r[i]
                col = i

        # Check for minimum energy.
        if self.r[row] >= 4.0e5 and self.r[col] >= 4.0e5:
            see_digit = True

            # Normal twist.
            if self.r[col] > self.r[row]:
                max_index = col
                if self.r[row] < (self.r[col] * 0.398):
                    see_digit = False
            # Reverse twist.
            else:
                max_index = row
                if self.r[col] < (self.r[row] * 0.158):
                    see_digit = False

            # Signal-to-noise test. AT&T states the noise must be 16dB down
            # from the signal: count signals above the threshold; only two
            # (the row and column tone) should clear it.
            if self.r[max_index] > 1.0e9:
                t = self.r[max_index] * 0.158
            else:
                t = self.r[max_index] * 0.010

            peak_count = 0
            for i in range(8):
                if self.r[i] > t:
                    peak_count += 1
            if peak_count > 2:
                see_digit = False

            if see_digit:
                self.characters.append(
                    (row_col_ascii_codes[row][col - 4],
                     float(self.sample_index) / float(self.sample_rate)))

    def _cleanup_decoded(self) -> str:
        # Collapse the run-length stream of detections into distinct symbols.
        chars = [d[0] for d in self.characters]
        decoded = ""

        count = 1
        prev = ""
        for c in chars:
            if c == prev:
                count += 1
                if count >= self.min_consecutive:
                    count = 0
                    decoded += c
                    prev = ""
            else:
                prev = c

        return decoded

    def goertzel(self, sample: int) -> None:
        """Feed one 16-bit signed sample to the Goertzel detector."""
        self.sample_count += 1
        self.sample_index += 1

        for i in range(self.max_bins):
            q0 = self.coefs[i] * self.q1[i] - self.q2[i] + sample
            self.q2[i] = self.q1[i]
            self.q1[i] = q0

        if self.sample_count == self.goertzel_n:
            for i in range(self.max_bins):
                self.r[i] = ((self.q1[i] * self.q1[i]) +
                             (self.q2[i] * self.q2[i]) -
                             (self.coefs[i] * self.q1[i] * self.q2[i]))
                self.q1[i] = 0
                self.q2[i] = 0
            self._postprocess()
            self.sample_count = 0

    def _calc_coeffs(self) -> None:
        for n in range(self.max_bins):
            self.coefs[n] = 2.0 * math.cos(
                2.0 * math.pi * self.freqs[n] / self.sample_rate)

    def decode_wave(self, filename: str) -> str:
        """Decode the DTMF content of a WAV file and return the recovered string."""
        self.reset()

        wave_file = wave.open(filename)
        n_frames = wave_file.getnframes()

        count = 0
        while n_frames != count:
            raw = wave_file.readframes(1)
            (sample,) = struct.unpack("h", raw)
            self.goertzel(sample)
            count += 1

        wave_file.close()

        symbols = self._cleanup_decoded()
        if self.decode:
            return self.hex_decode(symbols.lower())
        return symbols

    @staticmethod
    def hex_decode(hex_encoded: str) -> str:
        """Decode a hex string back into ASCII text."""
        return bytes.fromhex(hex_encoded).decode("ascii")


def encode_text(text: str, file_path: str, duration: int = 100,
                pause: int = 500) -> str:
    """Encode ASCII ``text`` to DTMF tones in ``file_path``; return ``file_path``."""
    ToneGenerator(duration=duration, pause=pause).encode_to_wave(text, file_path)
    return file_path


def encode_dtmf(dtmf: str, file_path: str, duration: int = 100,
                pause: int = 500) -> str:
    """Encode a literal DTMF dial string to ``file_path``; return ``file_path``."""
    ToneGenerator(duration=duration, pause=pause).dtmf_to_wave(dtmf, file_path)
    return file_path


def decode(file_path: str, sample_rate: int = 16000, goertzel_n: int = 210,
           min_consecutive: int = 6, hex_decode: bool = True) -> str:
    """Decode the DTMF content of ``file_path`` and return the recovered string."""
    return ToneDecoder(sample_rate=sample_rate, goertzel_n=goertzel_n,
                       min_consecutive=min_consecutive,
                       hex_decode=hex_decode).decode_wave(file_path)
