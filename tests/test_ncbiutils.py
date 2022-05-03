import pytest
from ncbiutils.ncbiutils import Eutil, Efetch, PubMedFetch
from ncbiutils.types import DbEnum, RetTypeEnum, RetModeEnum


NCBI_EUTILS_BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'


# #############################
# #   Helpers
# #############################


class MockResponse:
    def __init__(self, raw):
        self.raw = raw


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
            uilist_pubmed_fetch._parse_response(None)

    def test_get_records_chunks(self, mocker, fetch_response):
        uids = ['35196497', '33278872', '24792780', '30158200', '151222']
        mocker.patch('ncbiutils.ncbiutils.PubMedFetch.fetch', return_value=(None, fetch_response))
        chunks = self.pubmed_fetch.get_records_chunks(uids)
        error, only_chunk, ids = list(chunks)[0]
        assert error is None
        assert len(ids) == len(uids)
        assert len(only_chunk) == len(uids)

    def test_get_records_chunks_on_error(self, mocker):
        uids = ['35196497', '33890651', '33279447', '33278872', '24792780', '30158200', '151222']
        mocker.patch('ncbiutils.ncbiutils.PubMedFetch.fetch', return_value=(Exception, None))
        chunks = self.pubmed_fetch.get_records_chunks(uids)
        error, _, ids = list(chunks)[0]
        assert error is not None
        assert len(ids) == len(uids)
