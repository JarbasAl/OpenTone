"""Caller-ID — Bell 202 SDMF / MDMF message encoding and decoding.

Builds the telephone caller-ID message formats (single- and multiple-data
message format) — type byte, length, parameter body, and the two's-complement
checksum — and carries them over the :mod:`opentone.fsk` Bell 202 modem.

    from opentone import callerid

    callerid.encode("phone.wav", number="5551234567", timestamp="06041530")
    callerid.decode("phone.wav")
    # {'format': 'SDMF', 'datetime': '06041530', 'number': '5551234567'}

Use ``mdmf=True`` (or pass ``name=``) for the multi-parameter MDMF format that
also carries the caller name.
"""
from typing import Dict, Optional

from opentone import fsk

__all__ = ["encode", "decode", "build_message", "parse_message", "CallerIDError"]

SDMF_TYPE = 0x04
MDMF_TYPE = 0x80
# MDMF parameter types.
P_DATETIME = 0x01
P_NUMBER = 0x02
P_NAME = 0x07


class CallerIDError(Exception):
    """Raised on a malformed or checksum-failing caller-ID message."""


def _checksum(body: bytes) -> int:
    return (256 - (sum(body) % 256)) % 256


def build_message(number: Optional[str] = None, name: Optional[str] = None,
                  timestamp: str = "01010000", mdmf: bool = False) -> bytes:
    """Build a caller-ID message (with checksum). MDMF if ``mdmf`` or ``name`` set."""
    if len(timestamp) != 8 or not timestamp.isdigit():
        raise ValueError("timestamp must be 8 digits MMDDHHMM")
    if mdmf or name is not None:
        body = bytearray()
        body += bytes([P_DATETIME, 8]) + timestamp.encode("ascii")
        if number is not None:
            body += bytes([P_NUMBER, len(number)]) + number.encode("ascii")
        if name is not None:
            body += bytes([P_NAME, len(name)]) + name.encode("ascii")
        head = bytes([MDMF_TYPE, len(body)])
    else:
        data = (timestamp + (number or "")).encode("ascii")
        body = bytearray(data)
        head = bytes([SDMF_TYPE, len(body)])
    msg = head + bytes(body)
    return msg + bytes([_checksum(msg)])


def parse_message(msg: bytes) -> Dict[str, str]:
    """Parse and checksum-validate a caller-ID message into a dict."""
    if len(msg) < 3:
        raise CallerIDError("message too short")
    if (sum(msg) % 256) != 0:
        raise CallerIDError("checksum mismatch")
    mtype, length = msg[0], msg[1]
    body = msg[2:2 + length]
    if mtype == SDMF_TYPE:
        text = body.decode("ascii", "replace")
        return {"format": "SDMF", "datetime": text[:8], "number": text[8:]}
    if mtype == MDMF_TYPE:
        out = {"format": "MDMF"}
        i = 0
        while i + 1 < len(body):
            ptype, plen = body[i], body[i + 1]
            data = body[i + 2:i + 2 + plen].decode("ascii", "replace")
            if ptype == P_DATETIME:
                out["datetime"] = data
            elif ptype == P_NUMBER:
                out["number"] = data
            elif ptype == P_NAME:
                out["name"] = data
            i += 2 + plen
        return out
    raise CallerIDError("unknown message type 0x%02x" % mtype)


def encode(file_path: str, number: Optional[str] = None, name: Optional[str] = None,
           timestamp: str = "01010000", mdmf: bool = False, **fsk_kwargs) -> str:
    """Build a caller-ID message and transmit it as Bell 202 FSK to ``file_path``."""
    msg = build_message(number=number, name=name, timestamp=timestamp, mdmf=mdmf)
    return fsk.encode(msg, file_path, **fsk_kwargs)


def decode(file_path: str, **fsk_kwargs) -> Dict[str, str]:
    """Decode and parse a caller-ID FSK WAV into a dict."""
    return parse_message(fsk.decode(file_path, **fsk_kwargs))
