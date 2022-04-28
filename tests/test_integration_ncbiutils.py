import pytest
from ncbiutils.ncbiutils import Eutil, Efetch, PubMedFetch, RetModeEnum, RetTypeEnum

# from ncbiutils.types import DbEnum


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
class TestEfetchIntegration:
    efetch = Efetch()

    def test_request_pubmed_id(self, id, db, expected):
        _, response = self.efetch._fetch(db=db, id=id)
        assert response.status_code == expected


@pytest.mark.parametrize('ids, expected', [(['31827641', '31772623', '31766097'], 200), (['00000000'], 400)])
class TestPubMedFetchIntegration:
    pubMedFetch = PubMedFetch()

    def test_request_pubmed_id(self, ids, expected):
        _, response = self.pubMedFetch.fetch(ids)
        assert response.status_code == expected
