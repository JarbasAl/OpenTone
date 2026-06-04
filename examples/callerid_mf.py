"""Telephone signalling: a caller-ID message and an MF dial sequence."""
import tempfile

from opentone import callerid, mf

# Caller-ID (MDMF: number + name).
cid = tempfile.mktemp(suffix=".wav")
callerid.encode(cid, number="5551234567", name="JARBAS AI",
                timestamp="06041530", mdmf=True)
print("caller-id:", callerid.decode(cid))

# MF: key-pulse, digits, stop.
dial = tempfile.mktemp(suffix=".wav")
mf.encode(["KP", "5", "5", "5", "1", "2", "3", "4", "ST"], dial)
print("mf:", mf.decode(dial))
