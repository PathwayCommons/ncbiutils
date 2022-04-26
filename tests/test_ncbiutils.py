from ncbiutils.ncbiutils import Fetcher
from ncbiutils import __version__
import os


FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data',
)


def test_fixture(shared_datadir):
    contents = (shared_datadir / 'sample_data.txt').read_text()
    assert contents == 'Hello World!\n'


def test_Fetcher_version():
    afetcher = Fetcher()
    print(f'afetcher.name')
    assert afetcher.version == __version__


def test_Fetcher_exists():
    assert Fetcher is not None
