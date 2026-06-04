import re

import opentone


def test_version_exposed():
    assert isinstance(opentone.__version__, str)
    assert re.match(r"^\d+\.\d+\.\d+(a\d+)?$", opentone.__version__)


def test_public_api():
    for name in ("ToneGenerator", "ToneDecoder", "encode_text",
                 "encode_dtmf", "decode"):
        assert name in opentone.__all__
        assert hasattr(opentone, name)
