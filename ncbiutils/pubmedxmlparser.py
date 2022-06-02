from pydantic import BaseModel
from typing import Optional, List, Generator
from lxml import etree
import re
from typing_extensions import TypeAlias

#############################
#   Aliases
#############################

XmlTree: TypeAlias = etree._ElementTree
Element: TypeAlias = etree._Element
PubmedArticle: TypeAlias = Element
PubmedArticleSet: TypeAlias = Element


##################################
#   XML package-specific
##################################


def _from_raw(data: bytes) -> XmlTree:
    """Parse an xml tree representation from bytes

    Do not provide parser text - ambiguity wrt prolog encoding can occur
    See https://lxml.de/parsing.html#python-unicode-strings
    """
    root = etree.XML(data)
    element_tree = etree.ElementTree(root)
    return element_tree


def _find_all(element: Element, xpath: str) -> List[Element]:
    """Wrapper for finding elements for xpath query, possibly empty"""
    return element.findall(xpath)


def _find_safe(element: Element, xpath: str) -> Optional[Element]:
    """Safe find, where None is returned in case xpath query returns no element"""
    optional = element.find(xpath)
    return optional if etree.iselement(optional) else None


def _text_safe(element: Element, xpath: str) -> Optional[str]:
    """Safe get for element text, where None is returned in case xpath query returns no element"""
    optional = _find_safe(element, xpath)
    return optional.text if optional is not None else None


def _collect_element_text(element: Element) -> str:
    """Collect all text from child elements as a single string

    Note: This implemenation essentially ignores text and math markup
    """
    return ' '.join(element.xpath('string()').split())


def _collect_element_text_with_prefix(element: Element, attribute: str):
    """Collect all text from child elements, prefixed by attribute from this Element"""
    prefix = element.get(attribute)
    text = _collect_element_text(element)
    return ': '.join([prefix, text]) if prefix else text


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

    """

    pmid: str
    pmc: Optional[str]
    doi: Optional[str]
    title: str
    abstract: Optional[str]
    author_list: Optional[List[Author]]
    journal: Journal
    publication_type_list: List[str]


class PubmedXmlParser(BaseModel):
    """
    Capabilities to parse PubMed XML.
    See DTD http://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_190101.dtd

    Class attributes
    ----------

    Attributes
    ----------
    citations : List[Optional[PubMedCitation]] = []
        List of PubMedCitation

    Methods
    ----------
    parse(text: str) -> List[Optional[PubMedCitation]]
        Return a list of article data given PubMed XML text

    """

    def _get_pmid(self, pubmed_article: PubmedArticle) -> Optional[str]:
        pmid = _text_safe(pubmed_article, './/MedlineCitation/PMID')
        return pmid

    def _get_doi(self, pubmed_article: PubmedArticle) -> Optional[str]:
        doi = _text_safe(pubmed_article, './/PubmedData/ArticleIdList/ArticleId[@IdType="doi"]')
        return doi

    def _get_pmc(self, pubmed_article: PubmedArticle) -> Optional[str]:
        pmc = _text_safe(pubmed_article, './/PubmedData/ArticleIdList/ArticleId[@IdType="pmc"]')
        return pmc

    def _get_abstract(self, pubmed_article: PubmedArticle) -> Optional[str]:
        abstract = []
        AbstractTexts = _find_all(pubmed_article, './/MedlineCitation/Article/Abstract/AbstractText')
        for AbstractText in AbstractTexts:
            abstract.append(_collect_element_text_with_prefix(AbstractText, 'Label'))
        return ' '.join(abstract) if len(abstract) > 0 else None

    def _get_title(self, pubmed_article: PubmedArticle) -> str:
        title = pubmed_article.find('.//MedlineCitation/Article/ArticleTitle')
        text = _collect_element_text(title)
        return text

    def _get_affiliations(self, author: Element) -> Optional[List[str]]:
        affiliations = _find_all(author, './/AffiliationInfo/Affiliation')
        alist = [_collect_element_text(affiliation) for affiliation in affiliations]
        return alist if len(alist) > 0 else None

    def _get_emails(self, author: Element) -> Optional[List[str]]:
        emails: List[str] = []
        email_regex = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
        affiliations = _find_all(author, './/AffiliationInfo/Affiliation')
        for affiliation in affiliations:
            line = _collect_element_text(affiliation)
            sanitized = line.strip('.')
            matches = re.findall(email_regex, sanitized)
            emails = emails + matches
        return emails if len(emails) > 0 else None

    def _get_author(self, author: Element) -> Author:
        return Author(
            fore_name=_text_safe(author, './/ForeName'),
            last_name=_text_safe(author, './/LastName'),
            initials=_text_safe(author, './/Initials'),
            collective_name=_text_safe(author, './/CollectiveName'),
            orcid=_text_safe(author, './/Identifier[@Source="ORCID"]'),
            affiliations=self._get_affiliations(author),
            emails=self._get_emails(author),
        )

    def _get_author_list(self, pubmed_article: PubmedArticle) -> Optional[List[Author]]:
        authors = _find_all(pubmed_article, './/MedlineCitation/Article/AuthorList/Author')
        author_list = [self._get_author(author) for author in authors]
        return author_list if len(author_list) > 0 else None

    def _get_PubmedArticleSet(self, xml_tree: XmlTree) -> PubmedArticleSet:
        pubmed_article_set = xml_tree.getroot()
        if pubmed_article_set.tag != 'PubmedArticleSet':
            raise ValueError('XML document does not contain a PubmedArticleSet')
        return pubmed_article_set

    def _get_journal(self, pubmed_article: PubmedArticle) -> Journal:
        journal = _find_safe(pubmed_article, './/MedlineCitation/Article/Journal')
        issn = [_collect_element_text(issn) for issn in _find_all(journal, './/ISSN')]
        title = _text_safe(journal, './/Title')
        volume = _text_safe(journal, './/JournalIssue/Volume')
        issue = _text_safe(journal, './/JournalIssue/Issue')
        pub_year = _text_safe(journal, './/JournalIssue/PubDate/Year')
        pub_month = _text_safe(journal, './/JournalIssue/PubDate/Month')
        pub_day = _text_safe(journal, './/JournalIssue/PubDate/Day')
        return Journal(
            issn=issn, title=title, volume=volume, issue=issue, pub_year=pub_year, pub_month=pub_month, pub_day=pub_day
        )

    def _get_pubtypes(self, pubmed_article: PubmedArticle) -> List[str]:
        publication_types = _find_all(pubmed_article, './/MedlineCitation/Article/PublicationTypeList/PublicationType')
        uids = [element.get('UI') for element in publication_types]
        return uids

    def parse(self, data: bytes) -> Generator[Citation, None, None]:
        """Parse an XML document to a list of custom citations"""
        xml_tree = _from_raw(data)
        pubmed_article_set = self._get_PubmedArticleSet(xml_tree)
        pubmed_articles = _find_all(pubmed_article_set, './/PubmedArticle')

        for pubmed_article in pubmed_articles:
            pmid = self._get_pmid(pubmed_article)
            pmc = self._get_pmc(pubmed_article)
            doi = self._get_doi(pubmed_article)
            title = self._get_title(pubmed_article)
            abstract = self._get_abstract(pubmed_article)
            author_list = self._get_author_list(pubmed_article)
            journal = self._get_journal(pubmed_article)
            publication_type_list = self._get_pubtypes(pubmed_article)
            citation = Citation(
                pmid=pmid,
                pmc=pmc,
                title=title,
                doi=doi,
                abstract=abstract,
                author_list=author_list,
                journal=journal,
                publication_type_list=publication_type_list,
            )
            yield citation
