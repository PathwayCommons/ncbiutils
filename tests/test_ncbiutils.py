import pytest
from ncbiutils.ncbiutils import Eutil, Efetch, PubMedFetch
from ncbiutils.types import DbEnum, RetTypeEnum, RetModeEnum
import pprint


pp = pprint.PrettyPrinter(indent=2)

NCBI_EUTILS_BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'


# #############################
# #   Helpers
# #############################


class MockResponse:
    def __init__(self, text):
        self.text = text


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
    def medlines_text(self, shared_datadir):
        text = (shared_datadir / 'medlines.txt').read_text()
        return text

    @pytest.fixture
    def medlines_response(self, medlines_text):
        return MockResponse(medlines_text)

    def test_attributes(self):
        assert PubMedFetch.db == DbEnum.pubmed
        assert isinstance(self.pubmed_fetch.retmode, RetModeEnum)
        assert isinstance(self.pubmed_fetch.rettype, RetTypeEnum)

    def test_parse_medline(self, medlines_text):
        """Cannot guarantee the constituents whatsover
        Each element instance of class 'Bio.Medline.Record'>
        """
        parsed = self.pubmed_fetch._parse_medline(medlines_text)
        print(type(parsed))
        assert parsed is not None
        for item in parsed:
            assert isinstance(item, dict)

    def test_parse_reponse(self):
        uilist_pubmed_fetch = PubMedFetch(rettype=RetTypeEnum.uilist)
        with pytest.raises(ValueError):
            uilist_pubmed_fetch._parse_response(None)

    def test_get_records(self, mocker, medlines_response):
        mocker.patch('ncbiutils.ncbiutils.PubMedFetch.fetch', return_value = (None, medlines_response))
        # FYI these uids sync up with the 'medlines.txt' fixture
        uids = ['35196497', '33890651', '33279447', '33278872', '24792780', '30158200', '151222']
        chunks = self.pubmed_fetch.get_records(uids)
        only_chunk = list(chunks)[0]
        assert len(only_chunk) == len(uids)
