from enum import Enum


class HttpMethodEnum(str, Enum):
    GET = 'GET'
    POST = 'POST'


class EutilEnum(str, Enum):
    esearch = 'esearch'
    esummary = 'esummary'
    efetch = 'efetch'
    elink = 'elink'


class DbEnum(str, Enum):
    pubmed = 'pubmed'


class RetModeEnum(str, Enum):
    text = 'text'
    xml = 'xml'
    asn = 'asn.1'


class RetTypeEnum(str, Enum):
    uilist = 'uilist'
    abstract = 'abstract'
    docsum = 'docsum'
    medline = 'medline'


class DownloadPathEnum(str, Enum):
    updatefiles = 'updatefiles'
    baseline = 'baseline'
