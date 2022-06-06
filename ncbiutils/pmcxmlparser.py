from pydantic import BaseModel
from typing import Optional, List, Generator, Dict, Any
from typing_extensions import TypeAlias
from ncbiutils.pubmed import Citation, Author, Journal
from ncbiutils.xml import (
    Element,
    XmlTree,
    _find_safe,
    _text_safe,
    _find_all,
    _collect_element_text,
)


def unique_list(alist):
    return list(dict.fromkeys(alist))


#############################
#   Aliases
#############################

PmcArticle: TypeAlias = Element
PmcArticleSet: TypeAlias = Element


class PmcXmlParser(BaseModel):
    """
    Capabilities to parse PubMedCentral XML.
    See DTD https://dtd.nlm.nih.gov/ncbi/pmc/articleset/nlm-articleset-2.0.dtd

    Methods
    ----------
    parse(data: bytes) -> Generator[Citation, None, None]
        Return a list of article data given pmc-articleset bytes
    """

    def _get_pmid(self, pmc_article: PmcArticle) -> Optional[str]:
        pmid = _text_safe(pmc_article, './/front/article-meta/article-id[@pub-id-type="pmid"]')
        return pmid

    def _get_doi(self, pmc_article: PmcArticle) -> Optional[str]:
        doi = _text_safe(pmc_article, './/front/article-meta/article-id[@pub-id-type="doi"]')
        return doi

    def _get_pmc(self, pmc_article: PmcArticle) -> Optional[str]:
        pmc = _text_safe(pmc_article, './/front/article-meta/article-id[@pub-id-type="pmc"]')
        return pmc

    def _get_abstract(self, pmc_article: PmcArticle) -> Optional[str]:
        abstract = []
        abstracts = _find_all(pmc_article, './/front/article-meta/abstract')
        for abstract_elt in abstracts:
            abstract.append(_collect_element_text(abstract_elt))
        return ' '.join(abstract) if len(abstract) > 0 else None

    def _get_title(self, pmc_article: PmcArticle) -> str:
        title = pmc_article.find('.//front/article-meta/title-group/article-title')
        text = _collect_element_text(title)
        return text

    def _get_affiliations(self, author: Element, pmc_article: PmcArticle) -> Optional[List[str]]:
        alist = []
        affiliation_xrefs = _find_all(author, './/xref[@ref-type="aff"]')
        rids = [affiliation_xref.get('rid') for affiliation_xref in affiliation_xrefs]
        for rid in rids:
            aff = pmc_article.find(f'.//aff[@id="{rid}"]')
            alist.append(_collect_element_text(aff))
        return alist if len(alist) > 0 else None

    def _get_emails(self, author: Element, pmc_article: PmcArticle) -> Optional[List[str]]:
        emails: List[str] = []
        contrib_emails = _find_all(author, './/email')
        corresp_xrefs = _find_all(author, './/xref[@ref-type="corresp"]')
        # embedded within <contrib>
        for contrib_email in contrib_emails:
            emails.append(_collect_element_text(contrib_email))
        # referenced within <contrib>
        for corresp_xref in corresp_xrefs:
            rid = corresp_xref.get('rid')
            corresp_elt = _find_safe(pmc_article, f'.//author-notes/corresp[@id="{rid}"]')
            corresp_emails = _find_all(corresp_elt, './/email')
            for corresp_email in corresp_emails:
                emails.append(_collect_element_text(corresp_email))
        return unique_list(emails) if len(emails) > 0 else None

    def _get_author(self, author: Element, pmc_article: PmcArticle) -> Author:
        return Author(
            fore_name=_text_safe(author, './/name/given-names'),
            last_name=_text_safe(author, './/name/surname'),
            initials=None,
            collective_name=None,
            orcid=_text_safe(author, './/contrib-id[@contrib-id-type="orcid"]'),
            affiliations=self._get_affiliations(author, pmc_article),
            emails=self._get_emails(author, pmc_article),
        )

    def _get_author_list(self, pmc_article: PmcArticle) -> Optional[List[Author]]:
        authors = _find_all(pmc_article, './/front/article-meta/contrib-group/contrib[@contrib-type="author"]')
        author_list = [self._get_author(author, pmc_article) for author in authors]
        return author_list if len(author_list) > 0 else None

    def _get_PmcArticleSet(self, xml_tree: XmlTree) -> PmcArticleSet:
        pmc_article_set = xml_tree.getroot()
        if pmc_article_set.tag != 'pmc-articleset':
            raise ValueError('XML document does not contain a pmc-articleset')
        return pmc_article_set

    def _get_journal(self, pmc_article: PmcArticle) -> Journal:
        journal = _find_safe(pmc_article, './/front/journal-meta')
        issn = [_collect_element_text(issn) for issn in _find_all(journal, './/issn')]
        title = _text_safe(journal, './/journal-title-group/journal-title')
        article = _find_safe(pmc_article, './/front/article-meta')
        volume = _text_safe(article, './/volume')
        issue = _text_safe(article, './/issue')
        pub_date = _find_safe(article, './/pub-date')
        if pub_date is not None:
            pub_year = _text_safe(pub_date, './/year')
            pub_month = _text_safe(pub_date, './/month')
            pub_day = _text_safe(pub_date, './/day')
        return Journal(
            issn=issn, title=title, volume=volume, issue=issue, pub_year=pub_year, pub_month=pub_month, pub_day=pub_day
        )

    def _get_correspondence(self, pmc_article: PmcArticle) -> List[Dict[str, Any]]:
        correspondence = []
        corresp_elts = _find_all(pmc_article, './/author-notes/corresp')
        for corresp_elt in corresp_elts:
            emails = []
            corresp_emails = _find_all(corresp_elt, './/email')
            for corresp_email in corresp_emails:
                emails.append(_collect_element_text(corresp_email))
            notes = _collect_element_text(corresp_elt)
            correspondence.append({'emails': emails, 'notes': notes})
        return correspondence

    def parse(self, xml_tree: XmlTree) -> Generator[Citation, None, None]:
        """Parse an XML document to a list of custom citations"""
        pmc_article_set = self._get_PmcArticleSet(xml_tree)
        pmc_articles = _find_all(pmc_article_set, './/article')

        for pmc_article in pmc_articles:
            pmid = self._get_pmid(pmc_article)
            pmc = self._get_pmc(pmc_article)
            doi = self._get_doi(pmc_article)
            title = self._get_title(pmc_article)
            abstract = self._get_abstract(pmc_article)
            author_list = self._get_author_list(pmc_article)
            journal = self._get_journal(pmc_article)
            correspondence = self._get_correspondence(pmc_article)
            citation = Citation(
                pmid=pmid,
                pmc=pmc,
                title=title,
                doi=doi,
                abstract=abstract,
                author_list=author_list,
                journal=journal,
                publication_type_list=[],
                correspondence=correspondence,
            )
            yield citation
