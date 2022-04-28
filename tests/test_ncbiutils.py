import pytest
from ncbiutils.ncbiutils import Eutil, Efetch, PubMedFetch
from ncbiutils.types import DbEnum, RetTypeEnum, RetModeEnum

NCBI_EUTILS_BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'


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

    @pytest.fixture(autouse=False)
    def medlines_text(self, shared_datadir):
        text = (shared_datadir / 'medlines_valid.txt').read_text()
        return text

    def test_class_attributes(self):
        assert PubMedFetch.db == DbEnum.pubmed
        assert isinstance(self.pubmed_fetch.retmode, RetModeEnum)
        assert isinstance(self.pubmed_fetch.rettype, RetTypeEnum)

    def test_parse_medline(self, medlines_text):
        parsed = self.pubmed_fetch._parse_medline(medlines_text)
        assert parsed is not None

    def test_get_articles(self):
        assert self.pubmed_fetch.get_articles is not None
