# from enum import Enum

# from typing import ClassVar, List

# from pydantic import BaseModel, HttpUrl, EmailStr, validator

# import requests
# from loguru import logger


# class HttpMethodEnum(str, Enum):
#     get = 'GET'
#     post = 'POST'


# class EutilEnum(str, Enum):
#     efetch = 'efetch'


# class DbEnum(str, Enum):
#     pubmed = 'pubmed'


# class RetModeEnum(str, Enum):
#     text = 'text'
#     xml = 'xml'
#     asn = 'asn.1'


# class RetTypeEnum(str, Enum):
#     uilist = 'uilist'
#     full = 'full'
#     abstract = 'abstract'
#     docsum = 'docsum'
#     medline = 'medline'


# class Eutil(BaseModel):
#     """
#     A class that holds values related to various NCBI E-Utilities.

#     Class attributes
#     ----------
#     name : str
#         Package name
#     version : str
#         Package version
#     package_url : HttpUrl
#         URL for package repsitory
#     admin_email : EmailStr
#         Email for package maintainer
#     base_url : HttpUrl
#         Base URL for the various NCBI E-Utilities
#     retmax_limit : int
#         Maximum number of records that can be returned

#     Attributes
#     ----------
#     http_request_timeout_seconds : int
#         Timeout in seconds for server response (default 5)
#     retstart : int
#         Index before the first record to return (default 0)
#     retmax : int
#         Maximum number of records to return (default 10000)
#     api_key : str
#         API key for requests up to 10/sec

#     """

#     name: ClassVar[str] = 'ncbiutils'
#     version: ClassVar[str] = '0.1.0'
#     package_url: ClassVar[HttpUrl] = 'https://github.com/jvwong/ncbiutils'
#     admin_email: ClassVar[EmailStr] = 'info@biofactoid.org'
#     base_url: ClassVar[HttpUrl] = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
#     retmax_limit: ClassVar[int] = 10000

#     http_request_timeout_seconds: int = 5
#     retstart: int = 0
#     retmax: int = retmax_limit
#     api_key: str = None

#     @validator('retmax')
#     def retmax_is_nonneg_lt_limit(cls, v):
#         if v < 0 or v > cls.retmax_limit:
#             raise ValueError(f'Must be positive number less than {cls.retmax_limit}')
#         return v

#     def _safe_request(self, url: HttpUrl, method: HttpMethodEnum = HttpMethodEnum.get, headers={}, **opts):
#         user_agent = f'{self.name}/{self.version} ({self.package_url};mailto:{self.admin_email})'
#         request_headers = {'user-agent': user_agent}
#         request_headers.update(headers)
#         try:
#             r = requests.request(
#                 method, url, headers=request_headers, timeout=self.http_request_timeout_seconds, **opts
#             )
#             r.raise_for_status()
#         except requests.exceptions.Timeout as e:
#             logger.error(f'Timeout error {e}')
#             raise
#         except requests.exceptions.HTTPError as e:
#             logger.error(f'HTTP error {e}; status code: {r.status_code}')
#             raise
#         except requests.exceptions.RequestException as e:
#             logger.error(f'Error in request {e}')
#             raise
#         else:
#             return r

#     def _get_eutil_response(self, url: HttpUrl, **opts):
#         """Call one of the NCBI EUTILITIES and returns data as Python objects."""

#         eutils_params = {'retstart': self.retstart, 'retmax': self.retmax}
#         eutils_params.update(opts)
#         if self.api_key is not None:
#             eutils_params.update({'api_key': self.api_key})
#         eutilResponse = self._safe_request(url, HttpMethodEnum.post, files=eutils_params)
#         return eutilResponse


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


class HelloWorld:
    text = 'Hello World!'