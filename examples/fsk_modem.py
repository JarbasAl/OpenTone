"""Send arbitrary bytes over the FSK modem, with Reed-Solomon error correction."""
import tempfile

from opentone import fsk

payload = b"arbitrary bytes \x00\x01\xff over sound"
wav = tempfile.mktemp(suffix=".wav")

fsk.encode(payload, wav, nsym=8)        # 8 parity bytes per block
recovered = fsk.decode(wav, nsym=8)
print("recovered:", recovered)
assert recovered == payload
