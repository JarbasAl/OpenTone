"""FSK — a Bell 202 style frequency-shift-keying soft-modem.

Carry arbitrary bytes over an audio channel: a ``1`` bit is the mark tone, a
``0`` bit the space tone, one bit per baud period. A mark preamble lets the
receiver find the carrier, a single space start-bit marks the first data bit, and
a two-byte length header delimits the payload. Optional Reed-Solomon FEC
(:mod:`opentone.fec`) lets the frame survive a noisy channel.

    from opentone import fsk

    fsk.encode(b"hello", "msg.wav")
    fsk.decode("msg.wav")                 # b"hello"
    fsk.encode(b"hello", "msg.wav", nsym=8)   # with error correction
    fsk.decode("msg.wav", nsym=8)

Defaults (mark 1200 Hz, space 2200 Hz, 300 baud, 8 kHz) round-trip cleanly and,
with ``nsym`` parity, tolerate byte errors.
"""
from typing import List

from opentone._audio import (DEFAULT_RATE, goertzel_power, read_wav, sine_n,
                             write_wav)
from opentone.fec import rs_decode, rs_encode

__all__ = ["encode", "decode", "MARK_FREQ", "SPACE_FREQ", "DEFAULT_BAUD"]

MARK_FREQ = 1200.0
SPACE_FREQ = 2200.0
DEFAULT_BAUD = 300
_PREAMBLE_BITS = 32  # leading mark bits for carrier detect


def _bytes_to_bits(data: bytes) -> List[int]:
    bits = []
    for byte in data:
        for i in range(8):  # LSB first
            bits.append((byte >> i) & 1)
    return bits


def _bits_to_bytes(bits: List[int]) -> bytes:
    out = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte |= bits[i + j] << j
        out.append(byte)
    return bytes(out)


def encode(data: bytes, file_path: str, baud: int = DEFAULT_BAUD,
           mark: float = MARK_FREQ, space: float = SPACE_FREQ,
           rate: int = DEFAULT_RATE, nsym: int = 0) -> str:
    """Encode ``data`` as FSK audio to ``file_path``; return ``file_path``.

    With ``nsym > 0`` the payload is Reed-Solomon protected with ``nsym`` parity
    bytes per block.
    """
    payload = rs_encode(data, nsym=nsym) if nsym else data
    header = len(payload).to_bytes(2, "big")
    frame_bits = ([1] * _PREAMBLE_BITS + [0]  # preamble + start bit
                  + _bytes_to_bits(header + payload))

    spb = _samples_per_bit(rate, baud)
    samples: List[int] = []
    for bit in frame_bits:
        samples += sine_n(mark if bit else space, spb, rate)
    write_wav(samples, file_path, rate)
    return file_path


def _samples_per_bit(rate: int, baud: int) -> int:
    spb = round(rate / baud)
    if spb < 2:
        raise ValueError("baud too high for this sample rate")
    return spb


def decode(file_path: str, baud: int = DEFAULT_BAUD, mark: float = MARK_FREQ,
           space: float = SPACE_FREQ, nsym: int = 0) -> bytes:
    """Decode an FSK ``encode`` WAV back to bytes. ``nsym`` must match the encoder."""
    samples, rate = read_wav(file_path)
    spb = _samples_per_bit(rate, baud)

    n_bits = len(samples) // spb
    bits = []
    for k in range(n_bits):
        block = samples[k * spb:(k + 1) * spb]
        bits.append(1 if goertzel_power(block, mark, rate)
                    >= goertzel_power(block, space, rate) else 0)

    # Find the start bit: the first space (0) after the mark preamble.
    start = None
    for i, b in enumerate(bits):
        if b == 0:
            start = i
            break
    if start is None:
        return b""

    data_bits = bits[start + 1:]
    if len(data_bits) < 16:
        return b""
    length = (_bits_to_bytes(data_bits[:16]))
    n = int.from_bytes(length, "big")
    payload_bits = data_bits[16:16 + n * 8]
    payload = _bits_to_bytes(payload_bits)[:n]
    if nsym:
        return rs_decode(payload, nsym=nsym)
    return payload
