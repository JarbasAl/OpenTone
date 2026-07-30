import pytest

from opentone.fec import rs_encode, rs_decode, ReedSolomonError


def test_clean_roundtrip():
    msg = b"hello world, a data-over-sound payload"
    assert rs_decode(rs_encode(msg, nsym=10), nsym=10) == msg


def test_parity_length():
    code = rs_encode(b"AB", nsym=8)
    assert len(code) == 2 + 8


@pytest.mark.parametrize("nsym,errors", [(10, 5), (8, 4), (16, 8)])
def test_corrects_up_to_capacity(nsym, errors):
    msg = bytes(range(60))
    code = bytearray(rs_encode(msg, nsym=nsym))
    for pos in range(errors):
        code[pos] ^= 0xA5
    assert rs_decode(bytes(code), nsym=nsym) == msg


def test_too_many_errors_raises():
    msg = b"important payload"
    code = bytearray(rs_encode(msg, nsym=10))
    for pos in range(6):  # 6 > nsym//2 = 5
        code[pos] ^= 0xFF
    with pytest.raises(ReedSolomonError):
        rs_decode(bytes(code), nsym=10)


def test_multiblock():
    msg = bytes(range(256)) * 3  # forces several RS(255) blocks
    code = bytearray(rs_encode(msg, nsym=16))
    code[5] ^= 0x11
    code[300] ^= 0x22
    assert rs_decode(bytes(code), nsym=16) == msg


def test_empty_and_validation():
    assert rs_decode(rs_encode(b"", nsym=4), nsym=4) == b""
    with pytest.raises(ValueError):
        rs_encode(b"x", nsym=0)
