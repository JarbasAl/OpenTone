# DTMF reference

DTMF (dual-tone multi-frequency) represents each keypad symbol as the sum of one
**row** frequency and one **column** frequency. A receiver that detects exactly
one row tone and one column tone reads off the symbol at their intersection.

## Frequency grid

|            | 1209 Hz | 1336 Hz | 1477 Hz | 1633 Hz |
|------------|:-------:|:-------:|:-------:|:-------:|
| **697 Hz** |   1     |   2     |   3     |   A     |
| **770 Hz** |   4     |   5     |   6     |   B     |
| **852 Hz** |   7     |   8     |   9     |   C     |
| **941 Hz** |   E     |   0     |   F     |   D     |

The four column frequencies are the rows `frequencyR = [697, 770, 852, 941]` and
columns `frequencyC = [1209, 1336, 1477, 1633]` in `ToneGenerator`.

## Symbol alphabet

OpenTone uses the 16 symbols `0-9` and `A-F`. This matches hexadecimal, which is
why text encoding works: each byte becomes two hex digits, and each hex digit is
one DTMF symbol.

On a physical telephone keypad the bottom row is `*` `0` `#`, plus the `A-D`
column used for signalling. OpenTone maps the keypad `*` and `#` positions to
`E` and `F` so the full alphabet stays within `0-9A-F`. See
[Decoding](decoding.md#telephone-e-and-f) for converting them back.
