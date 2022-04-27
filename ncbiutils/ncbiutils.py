from pydantic import BaseModel, HttpUrl, validator
from typing import ClassVar
from ncbiutils.types import HttpMethodEnum
from ncbiutils.http import safe_requests

# from loguru import logger


class Eutil(BaseModel):
    """
    A base class for other NCBI E-Utilities

    Class attributes
    ----------
    base_url : HttpUrl
        Base URL for the various NCBI E-Utilities
    retmax_limit : int
        Maximum number of records that can be returned

    Attributes
    ----------
    retstart : int
        Index before the first record to return (default 0)
    retmax : int
        Maximum number of records to return (default 10000)
    api_key : str
        Key for NCBI E-Utilities

    """

    base_url: ClassVar[HttpUrl] = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    retmax_limit: ClassVar[int] = 10000

    retstart: int = 0
    retmax: int = retmax_limit
    api_key: str = None

    @validator('retmax')
    def retmax_is_nonneg_lt_limit(cls, v):
        if v < 0 or v > cls.retmax_limit:
            raise ValueError(f'Must be positive number less than {cls.retmax_limit}')
        return v


    def _get_eutil_response(self, url: HttpUrl, **opts):
        """Call one of the NCBI E-Utilities and return a requests.Reponse"""
        params = {'retstart': self.retstart, 'retmax': self.retmax}
        params.update(opts)
        if self.api_key:
            params.update({'api_key': self.api_key})
        err, response = safe_requests(url, method = HttpMethodEnum.POST, files = params)
        return err, response


# class Fetcher(Eutil):
#     """
#     A class that provides for record retrieval.

#     Class attributes
#     ----------
#     efetch_url : HttpUrl
#         The E-Utilities URL for EFETCH

#     """

#     efetch_url: ClassVar[HttpUrl] = f'{Eutil.base_url}efetch.fcgi'

#     def _fetch(self, db: DbEnum, id: str, **opts):
#         """Return raw HTTP Response given uid list and db"""
#         efetch_params = {'db': db, 'id': id}
#         efetch_params.update(opts)
#         return self._get_eutil_response(self.efetch_url, **efetch_params)


# class Medline(Fetcher):
#     """
#     A class that retrieves article text from PubMed

#     Class attributes
#     ----------
#     db : DbEnum
#         The pubmed database

#     Methods
#     -------
#     get(uids: List[str])
#         Retrieve text records given the list of uids

#     """

#     db: ClassVar[DbEnum] = DbEnum.pubmed

#     def get(self, uids: List[str]):
#         """Return uid, and text (i.e. title + abstract) given a PubMed uid"""
#         id = ','.join(uids)
#         pubmed_opts = {'retmode': RetModeEnum.text, 'rettype': RetTypeEnum.medline}
#         return self._fetch(db=self.db, id=id, **pubmed_opts)


# class HelloWorld:
#     text = 'Hello World!'

#     def load_data(self):
#         data = 2
#         return data