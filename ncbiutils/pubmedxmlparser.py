from pydantic import BaseModel
from typing import Optional, List, Generator, Dict, Any
import re
from typing_extensions import TypeAlias
from ncbiutils.pubmed import Author, Journal, Citation
from ncbiutils.xml import (
    Element,
    XmlTree,
    _find_safe,
    _text_safe,
    _find_all,
    _collect_element_text_with_prefix,
    _collect_element_text,
)

#############################
#   Aliases
#############################

PubmedArticle: TypeAlias = Element
PubmedArticleSet: TypeAlias = Element


class PubmedXmlParser(BaseModel):
    """
    Capabilities to parse PubMed XML.
    See DTD http://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_190101.dtd

    Methods
    ----------
    parse(data: bytes) -> Generator[Citation, None, None]
        Return a list of article data given PubMed XML bytes

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

    def _get_ui(self, element: Element) -> Dict[str, str]:
        ui = element.get('UI')
        value = _collect_element_text(element)
        return {'ui': ui, 'value': value}

    def _get_mesh_heading(self, mesh_heading: Element) -> Dict[str, Any]:
        heading: Dict[str, Any] = {}
        descriptor_name = _find_safe(mesh_heading, './/DescriptorName')
        heading['descriptor_name'] = self._get_ui(descriptor_name)
        qualifier_name_list = _find_all(mesh_heading, './/QualifierName')
        if len(qualifier_name_list) > 0:
            heading['qualifier_name'] = [self._get_ui(qualifier_name) for qualifier_name in qualifier_name_list]
        return heading

    def _get_mesh_list(self, pubmed_article: PubmedArticle) -> Optional[List[Dict[str, Any]]]:
        mesh_heading_list = _find_all(pubmed_article, './/MedlineCitation/MeshHeadingList/MeshHeading')
        mesh_list = [self._get_mesh_heading(mesh_heading) for mesh_heading in mesh_heading_list]
        return mesh_list if len(mesh_list) > 0 else None

    def parse(self, xml_tree: XmlTree) -> Generator[Citation, None, None]:
        """Parse an XML document to a list of custom citations"""
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
            mesh_list = self._get_mesh_list(pubmed_article)
            citation = Citation(
                pmid=pmid,
                pmc=pmc,
                title=title,
                doi=doi,
                abstract=abstract,
                author_list=author_list,
                journal=journal,
                publication_type_list=publication_type_list,
                correspondence=[],
                mesh_list=mesh_list,
            )
            yield citation
