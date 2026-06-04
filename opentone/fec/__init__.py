"""Reed-Solomon forward error correction over GF(256).

A small, dependency-free RS(255, 255 - nsym) coder used by the modem schemes to
survive a noisy audio channel. ``nsym`` parity bytes per block correct up to
``nsym // 2`` byte errors. Messages longer than ``255 - nsym`` bytes are split
into blocks transparently.

    from opentone.fec import rs_encode, rs_decode

    payload = b"hello world"
    block = rs_encode(payload, nsym=10)   # payload + 10 parity bytes
    recovered = rs_decode(block, nsym=10) # corrects up to 5 byte errors
"""
from typing import List, Tuple

__all__ = ["rs_encode", "rs_decode", "ReedSolomonError", "RS_PRIM"]

RS_PRIM = 0x11d  # primitive polynomial x^8 + x^4 + x^3 + x^2 + 1
_MAX_BLOCK = 255


class ReedSolomonError(Exception):
    """Raised when a block has more errors than the parity can correct."""


# --- GF(256) arithmetic --------------------------------------------------------

_exp = [0] * 512
_log = [0] * 256


def _init_tables(prim: int = RS_PRIM) -> None:
    x = 1
    for i in range(255):
        _exp[i] = x
        _log[x] = i
        x <<= 1
        if x & 0x100:
            x ^= prim
    for i in range(255, 512):
        _exp[i] = _exp[i - 255]


_init_tables()


def _mul(x: int, y: int) -> int:
    if x == 0 or y == 0:
        return 0
    return _exp[_log[x] + _log[y]]


def _div(x: int, y: int) -> int:
    if y == 0:
        raise ZeroDivisionError("GF division by zero")
    if x == 0:
        return 0
    return _exp[(_log[x] + 255 - _log[y]) % 255]


def _pow(x: int, power: int) -> int:
    return _exp[(_log[x] * power) % 255]


def _inverse(x: int) -> int:
    return _exp[255 - _log[x]]


def _poly_scale(p: List[int], x: int) -> List[int]:
    return [_mul(c, x) for c in p]


def _poly_add(p: List[int], q: List[int]) -> List[int]:
    r = [0] * max(len(p), len(q))
    for i in range(len(p)):
        r[i + len(r) - len(p)] = p[i]
    for i in range(len(q)):
        r[i + len(r) - len(q)] ^= q[i]
    return r


def _poly_mul(p: List[int], q: List[int]) -> List[int]:
    r = [0] * (len(p) + len(q) - 1)
    for i, pi in enumerate(p):
        if pi == 0:
            continue
        lp = _log[pi]
        for j, qj in enumerate(q):
            if qj:
                r[i + j] ^= _exp[lp + _log[qj]]
    return r


def _poly_eval(poly: List[int], x: int) -> int:
    y = poly[0]
    for coef in poly[1:]:
        y = _mul(y, x) ^ coef
    return y


def _poly_div(dividend: List[int], divisor: List[int]) -> Tuple[List[int], List[int]]:
    out = list(dividend)
    for i in range(len(dividend) - (len(divisor) - 1)):
        coef = out[i]
        if coef != 0:
            for j in range(1, len(divisor)):
                if divisor[j] != 0:
                    out[i + j] ^= _mul(divisor[j], coef)
    sep = -(len(divisor) - 1)
    return out[:sep], out[sep:]


def _generator_poly(nsym: int) -> List[int]:
    g = [1]
    for i in range(nsym):
        g = _poly_mul(g, [1, _pow(2, i)])
    return g


# --- encode / decode (canonical RS-for-coders) ---------------------------------

def _encode_block(msg: bytes, nsym: int) -> bytes:
    gen = _generator_poly(nsym)
    out = list(msg) + [0] * (len(gen) - 1)
    for i in range(len(msg)):
        coef = out[i]
        if coef != 0:
            lc = _log[coef]
            for j in range(1, len(gen)):
                out[i + j] ^= _exp[lc + _log[gen[j]]]
    return bytes(list(msg) + out[len(msg):])


def _calc_syndromes(msg: List[int], nsym: int) -> List[int]:
    return [0] + [_poly_eval(msg, _pow(2, i)) for i in range(nsym)]


def _error_locator(synd: List[int], nsym: int) -> List[int]:
    err_loc = [1]
    old_loc = [1]
    synd_shift = len(synd) - nsym
    for i in range(nsym):
        k = i + synd_shift
        delta = synd[k]
        for j in range(1, len(err_loc)):
            delta ^= _mul(err_loc[-(j + 1)], synd[k - j])
        old_loc = old_loc + [0]
        if delta != 0:
            if len(old_loc) > len(err_loc):
                new_loc = _poly_scale(old_loc, delta)
                old_loc = _poly_scale(err_loc, _inverse(delta))
                err_loc = new_loc
            err_loc = _poly_add(err_loc, _poly_scale(old_loc, delta))
    while len(err_loc) and err_loc[0] == 0:
        del err_loc[0]
    errs = len(err_loc) - 1
    if errs * 2 > nsym:
        raise ReedSolomonError("too many errors to correct")
    return err_loc


def _find_errors(err_loc: List[int], nmess: int) -> List[int]:
    errs = len(err_loc) - 1
    positions = []
    for i in range(nmess):
        if _poly_eval(err_loc, _pow(2, i)) == 0:
            positions.append(nmess - 1 - i)
    if len(positions) != errs:
        raise ReedSolomonError("could not locate all errors")
    return positions


def _errata_locator(coef_pos: List[int]) -> List[int]:
    e_loc = [1]
    for i in coef_pos:
        e_loc = _poly_mul(e_loc, _poly_add([1], [_pow(2, i), 0]))
    return e_loc


def _error_evaluator(synd: List[int], err_loc: List[int], nsym: int) -> List[int]:
    _, remainder = _poly_div(_poly_mul(synd, err_loc), [1] + [0] * (nsym + 1))
    return remainder


def _correct_errata(msg: List[int], synd: List[int], err_pos: List[int]) -> List[int]:
    coef_pos = [len(msg) - 1 - p for p in err_pos]
    err_loc = _errata_locator(coef_pos)
    err_eval = _error_evaluator(synd[::-1], err_loc, len(err_loc) - 1)[::-1]

    x = [_pow(2, -(255 - p) % 255) for p in coef_pos]
    e = [0] * len(msg)
    for i, xi in enumerate(x):
        xi_inv = _inverse(xi)
        prime_tmp = 1
        for j in range(len(x)):
            if j != i:
                prime_tmp = _mul(prime_tmp, 1 ^ _mul(xi_inv, x[j]))
        if prime_tmp == 0:
            raise ReedSolomonError("could not find error magnitude")
        y = _poly_eval(err_eval[::-1], xi_inv)
        y = _mul(_pow(xi, 1), y)
        e[err_pos[i]] = _div(y, prime_tmp)
    return _poly_add(msg, e)


def _decode_block(block: bytes, nsym: int) -> bytes:
    msg = list(block)
    synd = _calc_syndromes(msg, nsym)
    if max(synd) == 0:
        return bytes(msg[:-nsym])
    err_loc = _error_locator(synd, nsym)[::-1]
    positions = _find_errors(err_loc, len(msg))
    msg = _correct_errata(msg, synd, positions)
    if max(_calc_syndromes(msg, nsym)) != 0:
        raise ReedSolomonError("decode failed to converge")
    return bytes(msg[:-nsym])


# --- public chunked API --------------------------------------------------------

def rs_encode(data: bytes, nsym: int = 10) -> bytes:
    """Encode ``data`` with ``nsym`` parity bytes per block; return the codeword."""
    if not 0 < nsym < _MAX_BLOCK:
        raise ValueError("nsym must be in 1..254")
    chunk = _MAX_BLOCK - nsym
    out = bytearray()
    for i in range(0, len(data), chunk):
        out += _encode_block(bytes(data[i:i + chunk]), nsym)
    return bytes(out)


def rs_decode(code: bytes, nsym: int = 10) -> bytes:
    """Decode an ``rs_encode`` codeword, correcting up to ``nsym // 2`` errors per block."""
    if not 0 < nsym < _MAX_BLOCK:
        raise ValueError("nsym must be in 1..254")
    out = bytearray()
    for i in range(0, len(code), _MAX_BLOCK):
        out += _decode_block(code[i:i + _MAX_BLOCK], nsym)
    return bytes(out)
