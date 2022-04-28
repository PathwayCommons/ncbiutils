from pydantic import BaseModel, validator
from typing import ClassVar, Any, Optional, Tuple, List, Dict, Generator, Union
from ncbiutils.types import HttpMethodEnum, DbEnum, RetModeEnum, RetTypeEnum
from ncbiutils.http import safe_requests

import io
import Bio

# # from loguru import logger


class Eutil(BaseModel):
    """
    A base class for other NCBI E-Utilities

    Class attributes
    ----------
    base_url : str
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
    request(url: str, **opts)
        Make request with appropriate body form parameters

    """

    base_url: ClassVar[str] = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    retmax_limit: ClassVar[int] = 10000

    retstart: int = 0
    retmax: int = retmax_limit
    api_key: Optional[str] = None

    @validator('retmax')
    def retmax_is_nonneg_lt_limit(cls, v):
        if v < 0 or v > cls.retmax_limit:
            raise ValueError(f'Must be positive number less than {cls.retmax_limit}')
        return v

    def request(self, url: str, **opts) -> Tuple[Optional[Exception], Any]:
        """Call one of the NCBI E-Utilities and return (error, requests.Response)"""
        params: Dict[str, Union[str, int]] = {'retstart': self.retstart, 'retmax': self.retmax}
        params.update(opts)
        if self.api_key:
            params.update({'api_key': self.api_key})
        err, response = safe_requests(url, method=HttpMethodEnum.POST, files=params)
        return err, response


class Efetch(Eutil):
    """
    A class tailored for the EFETCH E-Utility

    Class attributes
    ----------
    efetch_url : str
        The E-Utilities URL for EFETCH

     Methods
    ----------
    request(db: DbEnum, id: str, **opts)
        Make request to EFETCH URL with constrained body form parameters

    """

    url: ClassVar[str] = f'{Eutil.base_url}efetch.fcgi'

    def _fetch(self, db: DbEnum, id: str, **opts) -> Tuple[Optional[Exception], Any]:
        """Call EFETCH E-Utility for the given id and db"""
        params: Dict[str, Union[str, int]] = {'db': db, 'id': id}
        params.update(opts)
        err, response = self.request(self.url, **params)
        return err, response


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

    def fetch(self, ids: List[str]) -> Tuple[Optional[Exception], Any]:
        """Return id, and text (i.e. title + abstract) given a PubMed id"""
        id = ','.join(ids)
        params: Dict[str, Union[str, int]] = {'retmode': self.retmode, 'rettype': self.rettype}
        err, response = self._fetch(db=self.db, id=id, **params)
        return err, response

    def _parse_medline(self, text: str) -> List[Dict[str, str]]:
        """Return a list article records given Medline text
        See https://www.nlm.nih.gov/bsd/mms/medlineelements.html
        """
        return text
        f = io.StringIO(text)
        records = Bio.Medline.parse(f)
        docs = []
        # for record in records:
        #     if "PMID" not in record:
        #         raise HTTPException(status_code=422, detail=record["id:"][-1])
        #     pmid = record["PMID"]
        #     abstract = record["AB"] if "AB" in record else ""
        #     title = record["TI"] if "TI" in record else ""
        #     text = " ".join(_compact([title, abstract]))
        #     docs.append({"uid": pmid, "text": text})
        return docs

    def _parse_reponse(self, response):
        # if self.retmode = RetModeEnum.medline else raise ValueError(f"Unsupported eutil '{eutil}''")
        pass

    def _chunks(self, lst: List[str], n: int) -> Generator[List[str], None, None]:
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]

    def get_articles(self, uids: List[str]) -> Generator[List[Dict[str, str]], None, None]:
        """Return article fields for each PubMed ID"""
        pass


#         len_uids = len(uids)
#         num_fetches = (len_uids // self.retmax_limit) + (1 if len_uids % self.retmax_limit > 0 else 0)
#         for i in range(num_fetches):
#             lower = i * self.retmax_limit
#             upper = min([lower + self.retmax_limit, len_uids])
#             ids = uids[lower:upper]
#             try:
#                 error, response = self.fetch(ids)
#                 if error:
#                     raise error
#             except Exception as e:
#                 logger.warning(f"Error encountered in get_articles: {e}")
#                 continue
#             else:
#                 logger.info(f'Retrieved article {lower} through {upper - 1} of {len_uids - 1}')
#                 yield self._parse_reponse(response)
