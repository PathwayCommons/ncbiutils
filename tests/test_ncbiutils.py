import pytest
from ncbiutils.ncbiutils import Eutil, Efetch, PubMedFetch, RetModeEnum, RetTypeEnum
from ncbiutils.types import DbEnum

NCBI_EUTILS_BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'


#############################
#   Unit tests
#############################


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
    def test_class_attributes(self):
        assert PubMedFetch.db == DbEnum.pubmed
        assert isinstance(self.pubmed_fetch.retmode, RetModeEnum)
        assert isinstance(self.pubmed_fetch.rettype, RetTypeEnum)


#############################
#   Integration tests
#############################


@pytest.mark.parametrize(
    'id, db, expected', [('31827641,31772623,31766097', 'pubmed', 200), ('00000000', 'pubmed', 400)]
)
class TestEutilIntegration:
    eutil = Eutil()

    def test_request_pubmed_id(self, id, db, expected):
        url = f'{Eutil.base_url}efetch.fcgi'
        opts = {'id': id, 'db': db}
        _, response = self.eutil.request(url, **opts)
        assert response.status_code == expected


@pytest.mark.parametrize(
    'id, db, expected', [('31827641,31772623,31766097', 'pubmed', 200), ('00000000', 'pubmed', 400)]
)
class TestFetchIntegration:
    efetch = Efetch()

    def test_request_pubmed_id(self, id, db, expected):
        _, response = self.efetch.fetch(db = db, id = id)
        assert response.status_code == expected

# class TestHelloWorld:
#     def test_data(self, mocker):
#         mockData = 3
#         mocker.patch('tests.test_ncbiutils.HelloWorld.load_data', return_value = mockData)
#         h = HelloWorld()
#         data = h.load_data()
#         assert data == mockData
