import pytest
from ncbiutils.pmcxmlparser import PmcXmlParser
from ncbiutils.pubmed import Citation
from ncbiutils.xml import _from_raw

#############################
#   Unit tests
#############################


class TestPmcXmlParserClass(object):
    xmlparser = PmcXmlParser()

    @pytest.fixture
    def author_xml(self, shared_datadir):
        data = (shared_datadir / 'pmc_author.xml').read_bytes()
        return data

    def test_parse_returns_citation_list(self, author_xml):
        parse_result = self.xmlparser.parse(author_xml)
        first_result = next(parse_result)
        assert first_result is not None
        assert isinstance(first_result, Citation)

    def test_get_pmc_article_set(self, author_xml):
        xml_tree = _from_raw(author_xml)
        pubmed_article_set = self.xmlparser._get_PmcArticleSet(xml_tree)
        assert len(pubmed_article_set) == 3

    def test_parse_no_pubmedarticleset(self, shared_datadir):
        data = (shared_datadir / 'no_pubmedarticleset.xml').read_bytes()
        xml_tree = _from_raw(data)
        with pytest.raises(ValueError):
            self.xmlparser._get_PmcArticleSet(xml_tree)

    @pytest.mark.parametrize(
        'pmid, pmc, doi, abstract, title, last_name, email, jtitle, issn, volume, issue, pub_year',
        [
            (
                '33393230',
                '7857436',
                '10.15252/embr.202051162',
                'Although iron is required for cell proliferation',
                'The deubiquitinase OTUD1 enhances iron transport and potentiates host antitumor immunity',
                'You',
                'fupingyou@bjmu.edu.cn',
                'EMBO Reports',
                '1469-221X',
                '22',
                '2',
                '2021',
            ),
            (
                '35390271',
                '9023058',
                '10.7554/eLife.71624',
                'Ageing is the gradual decline in organismal fitness',
                'Multi-omic rejuvenation of human cells by maturation phase transient reprogramming',
                'Milagre',
                'imilagre@igc.gulbenkian.pt',
                'eLife',
                '2050-084X',
                '11',
                None,
                '2022',
            ),
            (
                '31565136',
                '6756846',
                '10.11604/pamj.2019.33.175.17560',
                'This study aimed to evaluate the long-term retention of',
                'Knowledge, skills and competency retention among health',
                'Draleru',
                None,
                'The Pan African Medical Journal',
                '1937-8688',
                '33',
                None,
                '2019',
            ),
        ],
    )
    def test_complete_citation_attributes_match(
        self,
        pmid,
        pmc,
        doi,
        abstract,
        title,
        last_name,
        email,
        jtitle,
        issn,
        volume,
        issue,
        pub_year,
        author_xml,
    ):
        parse_result = self.xmlparser.parse(author_xml)
        result = next(r for r in parse_result if r.pmid == pmid)
        assert result.pmc == pmc
        assert result.doi == doi
        assert abstract in result.abstract
        assert title in result.title
        anauthor = next(author for author in result.author_list if author.last_name == last_name)
        assert anauthor is not None
        assert email in anauthor.emails if email is not None else True
        journal = result.journal
        assert journal.title == jtitle
        assert issn in journal.issn
        assert journal.volume == volume
        assert journal.issue == issue
        assert journal.pub_year == pub_year

    @pytest.mark.parametrize(
        'pmid, last_name, email',
        [
            (
                '34723746',
                'Mokarram',
                'mokaram2@gmail.com'
            ),
            (
                '33704371',
                'Barabino',
                'silvia.barabino@unimib.it'
            )
        ],
    )
    def test_contrib_xref_email_match(
        self,
        pmid,
        last_name,
        email,
        shared_datadir
    ):
        data = (shared_datadir / 'pmc_corres_author.xml').read_bytes()
        parse_result = self.xmlparser.parse(data)
        result = next(r for r in parse_result if r.pmid == pmid)
        anauthor = next(author for author in result.author_list if author.last_name == last_name)
        assert email in anauthor.emails if email is not None else True

        assert True

