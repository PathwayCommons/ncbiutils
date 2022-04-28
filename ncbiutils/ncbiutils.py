from pydantic import BaseModel, validator
from typing import ClassVar, Any, Optional, Tuple, List, Dict, Generator, Union
from ncbiutils.types import HttpMethodEnum, DbEnum, RetModeEnum, RetTypeEnum
from ncbiutils.http import safe_requests

import io
from Bio import Medline

from loguru import logger


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
        """Return a list of dicts of Medline data (class 'Bio.Medline.Record') given Medline text

        Caveats
          - PMIDs can be duplicates, deleted and output garbage
          - Output is not guaranteed to be consistent with PubMed DTD
        See https://biopython.org/docs/1.75/api/Bio.Medline.html#Bio.Medline.Record
        """
        f = io.StringIO(text)
        records = Medline.parse(f)  # class 'Bio.Medline.Record'>
        return list(records)

    def _parse_response(self, response) -> List[Dict[str, str]]:
        """Delegate to an implementation or raise ValueError."""
        if self.rettype == RetTypeEnum.medline:
            return self._parse_medline(response.text)
        else:
            raise ValueError(f'Unsupported retmode: {self.rettype}')

    def _chunks(self, lst: List[str], n: int) -> Generator[List[str], None, None]:
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]

    def get_records(self, uids: List[str]) -> Generator[List[Dict[str, str]], None, None]:
        """Yields a list of records for PubMed uids"""
        i = 0
        for ids in self._chunks(uids, self.retmax):
            try:
                error, response = self.fetch(ids)
                if error:
                    raise error
            except Exception as e:
                logger.warning(f"Error encountered in get_articles: {e}")
                continue
            else:
                logger.info(f'Retrieved record chunk {i}')
                i += 1
                yield self._parse_response(response)
