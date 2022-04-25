from pubmedfetch import __version__
from pubmedfetch.pubmedfetch import add
import os


FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "data",
)


def test_version():
    assert __version__ == '0.1.0'


def test_fixture(shared_datadir):
    contents = (shared_datadir / "sample_data.txt").read_text()
    assert contents == "Hello World!\n"


def test_add_one():
    assert add(1, 2) == 3
