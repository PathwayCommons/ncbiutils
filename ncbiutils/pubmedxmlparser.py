from pydantic import BaseModel, NoneIsAllowedError
from typing import Optional, List, Generator, Dict
from lxml import etree
import re

#############################
#   Aliases
#############################

XmlTree = etree._ElementTree
Element = etree._Element
PubmedArticle = Element
PubmedArticleSet = Element


#############################
#   Helpers
#############################


def _find_safe( element: Element, xpath: str ) -> Optional[Element]:
    """Safe find, where None is returned in case xpath returns no element"""
    optional = element.find(xpath)
    return optional if etree.iselement(optional) else None


def _text_safe( element: Element, xpath: str ) -> Optional[str]:
    """Safe get for element text, where None is returned in case  xpath returns no element"""
    optional = _find_safe( element, xpath )
    return optional.text if optional is not None else None


def _collect_element_text(element: Element) -> str:
    """Collect all text from child elements as a single string"""
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
    emails: Optional[str]
    collective_name: Optional[str]
    orcid: Optional[str]
    affiliations: Optional[List[str]]
    emails: Optional[List[str]]


class PubmedCitation(BaseModel):
    """
    A wrapper for PubmedArticle data

    Attributes
    ----------
    pmid : str
        PubMed unique id (uid)
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
    doi: Optional[str]
    title: str
    abstract: Optional[str]
    author_list: Optional[List[Author]]


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

    def _get_pmid(self, pubmed_article: PubmedArticle) -> str:
        pmid = _text_safe(pubmed_article, './/MedlineCitation/PMID')
        return pmid

    def _get_doi(self, pubmed_article: PubmedArticle) -> Optional[str]:
        doi = _text_safe( pubmed_article, './/PubmedData/ArticleIdList/ArticleId[@IdType="doi"]')
        return doi

    def _get_abstract(self, pubmed_article: PubmedArticle) -> Optional[str]:
        abstract = []
        AbstractTexts = pubmed_article.findall('.//MedlineCitation/Article/Abstract/AbstractText')
        for AbstractText in AbstractTexts:
            abstract.append(_collect_element_text_with_prefix(AbstractText, 'Label'))
        return ' '.join(abstract) if len(abstract) > 0 else None

    def _get_title(self, pubmed_article: PubmedArticle) -> str:
        title = pubmed_article.find('.//MedlineCitation/Article/ArticleTitle')
        text = _collect_element_text(title)
        return text

    def _get_affiliations(self, author: Element) -> Optional[List[str]]:
        affiliations = author.findall('.//AffiliationInfo/Affiliation')
        alist = [_collect_element_text(affiliation) for affiliation in affiliations]
        return alist if len(alist) > 0 else None

    def _get_emails(self, author: Element) -> Optional[List[str]]:
        emails = []
        afilliations = author.findall('.//AffiliationInfo/Affiliation')
        for affiliation in afilliations:
            line = _collect_element_text(affiliation)
            match = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', line)
            santizied = [m.strip('.') for m in match]
            emails = emails + santizied
        return emails if len(emails) > 0 else None

    def _get_author(self, author: Element) -> Author:
        return Author(
            fore_name = _text_safe(author, './/ForeName'),
            last_name = _text_safe(author, './/LastName'),
            initials = _text_safe(author, './/Initials'),
            collective_name = _text_safe(author, './/CollectiveName'),
            orcid = _text_safe(author, './/Identifier[@Source="ORCID"]'),
            affiliations = self._get_affiliations(author),
            emails = self._get_emails(author)
        )

    def _get_author_list(self, pubmed_article: PubmedArticle) -> Optional[List[Author]]:
        authors = pubmed_article.findall('.//MedlineCitation/Article/AuthorList/Author')
        author_list = [self._get_author(author) for author in authors]
        return author_list if len(author_list) > 0 else None

    def _get_PubmedArticleSet(self, xml_tree: XmlTree) -> PubmedArticleSet:
        pubmed_article_set = xml_tree.getroot()
        # if pubmed_article_set is None:
        #     raise ValueError('There is no PubmedArticleSet available')
        # if pubmed_article_set.tag != 'PubmedArticleSet':
        #     raise ValueError('There is no PubmedArticleSet available')
        return pubmed_article_set

    def _from_text(self, text: str) -> XmlTree:
        root = etree.XML(text)
        element_tree = etree.ElementTree(root)
        return element_tree

    def parse(self, text: str) -> Generator[PubmedCitation, None, None]:
        xml_tree = self._from_text(text)
        pubmed_article_set = self._get_PubmedArticleSet(xml_tree)

        for pubmed_article in pubmed_article_set:
            pmid = self._get_pmid(pubmed_article)
            doi = self._get_doi(pubmed_article)
            title = self._get_title(pubmed_article)
            abstract = self._get_abstract(pubmed_article)
            author_list = self._get_author_list(pubmed_article)
            citation = PubmedCitation(
                pmid = pmid,
                title = title,
                doi = doi,
                abstract = abstract,
                author_list = author_list
                )
            yield citation
