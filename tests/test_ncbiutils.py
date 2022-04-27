# import pytest
from ncbiutils.ncbiutils import HelloWorld


# NCBI_EUTILS_BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'


# class TestMedlineAttributes:
#     key = 'somekey'
#     medline = Medline(api_key=key)

#     def test_inherits_class_base_url(self):
#         assert Medline.base_url == f'{NCBI_EUTILS_BASE_URL}'

#     def test_class_efetch_url(self):
#         assert Medline.efetch_url == f'{NCBI_EUTILS_BASE_URL}efetch.fcgi'

#     def test_set_api_key(self):
#         assert self.medline.api_key == self.key


# class TestMedlineFetchIntegration:
#     medline = Medline()

#     def test_fetch_valid_uids(self):
#         uids = ['31827641', '31772623', '31766097']
#         response = self.medline.get(uids)
#         assert response.status_code == 200

#     def test_fetch_invalid_uids(self):
#         uids = ['00000000']
#         with pytest.raises(Exception):
#             self.medline.get(uids)


class TestHelloWorld:
    text = HelloWorld.text

    def test_text(self):
        assert self.text == 'Hello World!'


