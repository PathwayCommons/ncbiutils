import pytest
from ncbiutils.pubmedxmlparser import PubmedXmlParser, Citation, _from_raw

#############################
#   Unit tests
#############################


def test_from_file_returns_xmltree(shared_datadir):
    data = (shared_datadir / 'double.xml').read_bytes()
    xml_tree = _from_raw(data)
    assert xml_tree.docinfo.xml_version == '1.0'
    assert '<!DOCTYPE PubmedArticleSet' in xml_tree.docinfo.doctype


class TestPubmedXmlParserClass(object):
    xmlparser = PubmedXmlParser()

    @pytest.fixture
    def double_xml(self, shared_datadir):
        data = (shared_datadir / 'double.xml').read_bytes()
        return data

    def test_parse_returns_citation_list(self, double_xml):
        parse_result = self.xmlparser.parse(double_xml)
        first_result = next(parse_result)
        assert first_result is not None
        assert isinstance(first_result, Citation)

    def test_get_pubmed_article_set(self, double_xml):
        xml_tree = _from_raw(double_xml)
        pubmed_article_set = self.xmlparser._get_PubmedArticleSet(xml_tree)
        assert len(pubmed_article_set) == 2

    def test_parse_no_pubmedarticleset(self, shared_datadir):
        data = (shared_datadir / 'no_pubmedarticleset.xml').read_bytes()
        xml_tree = _from_raw(data)
        with pytest.raises(ValueError):
            self.xmlparser._get_PubmedArticleSet(xml_tree)

    def test_duplicate_pmid(self, shared_datadir):
        data = (shared_datadir / 'duplicate.xml').read_bytes()
        parse_result = self.xmlparser.parse(data)
        result = list(parse_result)
        assert len(result) == 0

    @pytest.mark.parametrize(
        'pmid, doi, abstract, title, last_name, email, jtitle, issn, volume, issue, pub_year',
        [
            (
                '31302001',
                '10.1016/j.molcel.2019.06.008',
                'Sirt3, as a major mitochondrial nicotinamide',
                'SENP1-Sirt3 Signaling Controls Mitochondrial',
                'Cheng',
                'jkcheng@shsmu.edu.cn',
                'Molecular cell',
                '1097-4164',
                '75',
                '4',
                '2019',
            ),
            (
                '22454523',
                '10.1242/jcs.103564',
                'Botulinum neurotoxins (BoNTs) are classified',
                'Botulinum neurotoxin D-C uses synaptotagmin',
                'Dong',
                None,
                'Journal of cell science',
                '1477-9137',
                '125',
                'Pt 13',
                '2012',
            ),
        ],
    )
    def test_complete_citation_attributes_match(
        self, pmid, doi, abstract, title, last_name, email, jtitle, issn, volume, issue, pub_year, double_xml
    ):
        parse_result = self.xmlparser.parse(double_xml)
        result = next(r for r in parse_result if r.pmid == pmid)
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
        'pmid, doi, abstract, title, last_name, email, jtitle, issn, volume, issue, pub_year',
        [
            (
                '33279447',
                '10.1016/j.reuma.2020.11.001',
                None,
                '',
                'Vicente Moreno',
                'dr.vicentemoreno@gmail.com',
                'Reumatologia clinica',
                '2173-5743',
                None,
                None,
                '2020',
            ),
        ],
    )
    def test_no_abstract_empty_title(
        self, pmid, doi, abstract, title, last_name, email, jtitle, issn, volume, issue, pub_year, shared_datadir
    ):
        data = (shared_datadir / 'no_title_abstract.xml').read_bytes()
        parse_result = self.xmlparser.parse(data)
        result = next(r for r in parse_result if r.pmid == pmid)
        assert result.doi == doi
        assert result.abstract is abstract
        assert result.title == title
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
        'pmid, doi, abstract, title, last_name, email, collective_name, jtitle, issn, volume, issue, pub_year',
        [
            (
                '30158200',
                '10.1136/bmj.k3225',
                'RESULTS: Of 15 fracture associated loci identified, all were also associated with bone mineral',
                'Assessment of the genetic and clinical determinants of',
                'Rivadeneira',
                'brent.richards@mcgill.ca',
                'GEFOS/GENOMOS consortium and the 23andMe research team',
                'BMJ (Clinical research ed.)',
                '1756-1833',
                '362',
                None,
                '2018',
            ),
        ],
    )
    def test_strucabstract_markup_collectivename(
        self,
        pmid,
        doi,
        abstract,
        title,
        last_name,
        email,
        collective_name,
        jtitle,
        issn,
        volume,
        issue,
        pub_year,
        shared_datadir,
    ):
        data = (shared_datadir / 'markup.xml').read_bytes()
        parse_result = self.xmlparser.parse(data)
        result = next(r for r in parse_result if r.pmid == pmid)
        assert result.doi == doi
        assert abstract in result.abstract
        assert title in result.title
        anauthor = next(author for author in result.author_list if author.last_name == last_name)
        assert anauthor is not None
        assert email in anauthor.emails if email is not None else True
        cauthor = next(author for author in result.author_list if author.collective_name == collective_name)
        assert cauthor is not None
        journal = result.journal
        assert journal.title == jtitle
        assert issn in journal.issn
        assert journal.volume == volume
        assert journal.issue == issue
        assert journal.pub_year == pub_year

    @pytest.mark.parametrize(
        'pmid, doi, abstract, title, last_name, orcid, jtitle, issn, volume, issue, pub_year',
        [
            (
                '32820036',
                '10.1101/gad.337584.120',
                'In Ptch1 +/- ; Bcor ΔE9-10 tumors',
                'Functional loss of a noncanonical BCOR-PRC1.1',
                'Kutscher',
                '0000-0002-1130-4582',
                'Genes & development',
                '1549-5477',
                '34',
                '17-18',
                '2020',
            ),
        ],
    )
    def test_markup_orcid(
        self, pmid, doi, abstract, title, last_name, orcid, jtitle, issn, volume, issue, pub_year, shared_datadir
    ):
        data = (shared_datadir / 'orcid.xml').read_bytes()
        parse_result = self.xmlparser.parse(data)
        result = next(r for r in parse_result if r.pmid == pmid)
        assert result.doi == doi
        assert abstract in result.abstract
        assert title in result.title
        anauthor = next(author for author in result.author_list if author.last_name == last_name)
        assert anauthor is not None
        assert orcid == anauthor.orcid
        journal = result.journal
        assert journal.title == jtitle
        assert issn in journal.issn
        assert journal.volume == volume
        assert journal.issue == issue
        assert journal.pub_year == pub_year
