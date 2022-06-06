import pytest
from ncbiutils.ncbiutils import Eutil, Efetch, PubMedFetch, PubMedDownload
from ncbiutils.types import DbEnum, RetTypeEnum, RetModeEnum, DownloadPathEnum


NCBI_EUTILS_BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
NCBI_PUBMED_FTP_URL = 'https://ftp.ncbi.nlm.nih.gov/pubmed/'

# #############################
# #   Helpers
# #############################


class MockResponse:
    def __init__(self, content):
        self.content = content


# #############################
# #   Unit tests
# #############################


class TestEutilClass:
    def test_class_attributes(self):
        assert Eutil.base_url == NCBI_EUTILS_BASE_URL

    def test_set_api_key(self):
        key = 'somekey'
        eutil = Eutil(api_key=key)
        assert eutil.api_key == key

    def test_set_invalid_retmax(self):
        bigger_than_retmax_limit = Eutil.retmax_limit + 1
        with pytest.raises(Exception):
            Eutil(retmax=bigger_than_retmax_limit)


class TestEfetchClass:
    def test_class_attributes(self):
        assert Efetch.url == f'{NCBI_EUTILS_BASE_URL}efetch.fcgi'


class TestPubMedFetchClass:
    pubmed_fetch = PubMedFetch()

    @pytest.fixture
    def pubmed_data(self, shared_datadir):
        data = (shared_datadir / 'pubmed.xml').read_bytes()
        return data

    @pytest.fixture
    def fetch_response(self, pubmed_data):
        return MockResponse(pubmed_data)

    def test_attributes(self):
        assert PubMedFetch.db == DbEnum.pubmed
        assert isinstance(self.pubmed_fetch.retmode, RetModeEnum)
        assert self.pubmed_fetch.rettype is None

    def test_parse_reponse(self):
        uilist_pubmed_fetch = PubMedFetch(rettype=RetTypeEnum.uilist)
        with pytest.raises(ValueError):
            uilist_pubmed_fetch._parse_response(b'')

    def test_get_citations(self, mocker, fetch_response):
        uids = ['35196497', '33278872', '24792780', '30158200', '151222']
        mocker.patch('ncbiutils.ncbiutils.PubMedFetch.fetch', return_value=(None, fetch_response))
        chunks = self.pubmed_fetch.get_citations(uids)
        chunk = list(chunks)[0]
        assert chunk.error is None
        assert len(chunk.ids) == len(uids)
        assert len(chunk.citations) == len(uids)

    def test_get_citations_on_error(self, mocker):
        uids = ['35196497', '33890651', '33279447', '33278872', '24792780', '30158200', '151222']
        mocker.patch('ncbiutils.ncbiutils.PubMedFetch.fetch', return_value=(Exception, None))
        chunks = self.pubmed_fetch.get_citations(uids)
        error, _, ids = list(chunks)[0]
        assert error is not None
        assert len(ids) == len(uids)


class TestPubMedDownloadClass:
    def test_class_attributes(self):
        assert PubMedDownload.base_url == NCBI_PUBMED_FTP_URL
        assert PubMedDownload.updatefiles_path is not None
        assert PubMedDownload.baselinefiles_path is not None


class TestPubMedDownload:
    pubmed_download = PubMedDownload()

    @pytest.fixture
    def pubmed_data(self, shared_datadir):
        data = (shared_datadir / 'pubmed22n1115.xml.gz').read_bytes()
        return data

    @pytest.fixture
    def fetch_response(self, pubmed_data):
        return MockResponse(pubmed_data)

    def test_get_citations_updatefiles(self, mocker, fetch_response):
        first_file = 'pubmed22n1115.xml.gz'
        second_file = 'pubmed22n1313.xml.gz'
        files = [first_file, second_file]
        mocker.patch('ncbiutils.ncbiutils.PubMedDownload._request', return_value=(None, fetch_response))
        chunks = self.pubmed_download.get_citations(files, download_path=DownloadPathEnum.updatefiles)
        chunk = next(chunks)
        assert chunk.error is None
        assert chunk.ids[0] == first_file
        assert len(chunk.citations) == 3
