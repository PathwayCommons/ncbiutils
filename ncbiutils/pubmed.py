from pydantic import BaseModel
from typing import Optional, List, Dict, Any


#############################
#   Classes
#############################


class Author(BaseModel):
    """
    A wrapper for Author data

    Attributes
    ----------
    fore_name : Optional[str]
        First name
    last_name : Optional[str]
        Last name
    initials : Optional[str]
        Initials
    email : Optional[str]
        Email address
    collective_name : Optional[str]
        Organization name
    orcid : Optional[str]
        ORCID
    affiliations: Optional[List[str]]
        List of the affiliations

    """

    fore_name: Optional[str]
    last_name: Optional[str]
    initials: Optional[str]
    collective_name: Optional[str]
    orcid: Optional[str]
    affiliations: Optional[List[str]]
    emails: Optional[List[str]]


class Journal(BaseModel):
    """
    A wrapper for Journal data

    Attributes
    ----------
    title : Optional[str]
        Journal name
    issn : Optional[List[str]]
        International Standard Serial Number
    volume : Optional[str]
        Journal volume
    issue : Optional[str]
        Journal issue
    pub_year : Optional[str]
        Year of publication
    pub_month : Optional[str]
        Month of publication
    pub_day : Optional[str]
        Day of publication
    """

    title: Optional[str]
    issn: Optional[List[str]]
    volume: Optional[str]
    issue: Optional[str]
    pub_year: Optional[str]
    pub_month: Optional[str]
    pub_day: Optional[str]


class Citation(BaseModel):
    """
    A custom represenation of Pubmed article data

    Attributes
    ----------
    pmid : str
        PubMed unique id (uid)
    pmc : Optional[str]
        PubMedCentral id
    doi : Optional[str]
        Digital Object Identifier
    title : str
        Article title
    abstract : Optional[str]
        Sanitized and joined from various text elements
    author_list : Optional[List[Author]]
        List of Authors
    publication_type_list: List[str]
        MeSH codes https://www.nlm.nih.gov/mesh/pubtypes.html
    correspondence: List[Dict[str, Any]]
        Catch-all for correspondence fields
    correspondence: List[Dict[str, Any]]
    mesh_list
        Collection of MeSH DescriptorName, QualifierName(s)
    """

    pmid: str
    pmc: Optional[str]
    doi: Optional[str]
    title: str
    abstract: Optional[str]
    author_list: Optional[List[Author]]
    journal: Journal
    publication_type_list: List[str]
    correspondence: List[Dict[str, Any]]
    mesh_list: Optional[List[Dict[str, Any]]]
