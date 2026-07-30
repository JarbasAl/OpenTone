from os.path import abspath, dirname, join

import pytest

EXAMPLES = join(dirname(dirname(abspath(__file__))), "examples")


@pytest.fixture
def examples_dir():
    """Directory holding the bundled WAV fixtures."""
    return EXAMPLES
