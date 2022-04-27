from pydantic import BaseModel, HttpUrl, validator
from typing import ClassVar, List
from ncbiutils.types import HttpMethodEnum, DbEnum, RetModeEnum, RetTypeEnum
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

    Methods
    ----------
    request(url: HttpUrl, **opts)
        Make request with appropriate body form parameters

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


    def request(self, url: HttpUrl, **opts):
        """Call one of the NCBI E-Utilities and return (error, requests.Response)"""
        params = {'retstart': self.retstart, 'retmax': self.retmax}
        params.update(opts)
        if self.api_key:
            params.update({'api_key': self.api_key})
        err, response = safe_requests(url, method = HttpMethodEnum.POST, files = params)
        return err, response


class Efetch(Eutil):
    """
    A class tailored for the EFETCH E-Utility

    Class attributes
    ----------
    efetch_url : HttpUrl
        The E-Utilities URL for EFETCH

     Methods
    ----------
    request(db: DbEnum, id: str, **opts)
        Make request to EFETCH URL with constrained body form parameters

    """

    url: ClassVar[HttpUrl] = f'{Eutil.base_url}efetch.fcgi'

    def fetch(self, db: DbEnum, id: str, **opts):
        """Call EFETCH E-Utility for the given id and db"""
        params = {'db': db, 'id': id}
        params.update(opts)
        return self.request(self.url, **params)


class PubMedFetch(Efetch):
    """
    A class that retrieves article information from PubMed

    Class attributes
    ----------
    db : DbEnum
        The pubmed database

    Methods
    -------
    fetch(uids: List[str])
        Retrieve text records given the list of uids

    """

    db: ClassVar[DbEnum] = DbEnum.pubmed

    retmode: RetModeEnum = RetModeEnum.text
    rettype: RetTypeEnum = RetTypeEnum.medline

    def fetch(self, uids: List[str]):
        """Return uid, and text (i.e. title + abstract) given a PubMed uid"""
        id = ','.join(uids)
        params = {'retmode': self.retmode, 'rettype': self.rettype}
        return super().fetch(db=self.db, id=id, **params)


# class HelloWorld:
#     text = 'Hello World!'

#     def load_data(self):
#         data = 2
#         return data