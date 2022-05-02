import pytest
from ncbiutils.pubmedxmlparser import PubmedXmlParser, PubmedCitation, XmlTree, PubmedArticleSet

#############################
#   Unit tests
#############################


class TestPubmedXmlParserClass(object):
    xmlparser = PubmedXmlParser()

    @pytest.fixture
    def double_xml(self, shared_datadir):
        xml = (shared_datadir / 'double.xml').read_text()
        return xml

    def test_parse_returns_citation_list(self, double_xml):
        parse_result = self.xmlparser.parse(double_xml)
        first_result = next(parse_result)
        assert first_result is not None
        assert isinstance(first_result, PubmedCitation)

    def test_from_text_returns_xmltree(self, double_xml):
        xml_tree = self.xmlparser._from_text(double_xml)
        assert isinstance(xml_tree, XmlTree)
        assert xml_tree.docinfo.xml_version == '1.0'
        assert '<!DOCTYPE PubmedArticleSet' in xml_tree.docinfo.doctype

    def test_get_pubmed_article_set(self, double_xml):
        xml_tree = self.xmlparser._from_text(double_xml)
        pubmed_article_set = self.xmlparser._get_PubmedArticleSet(xml_tree)
        assert isinstance(pubmed_article_set, PubmedArticleSet)
        assert len(pubmed_article_set) == 2

    # def test_parse_no_pubmedarticleset(self, shared_datadir):
    #     xml = (shared_datadir / 'no_pubmedarticleset.xml').read_text()
    #     xml_tree = self.xmlparser._from_text(xml)
    #     assert True
    #     # with pytest.raises(ValueError):
    #     #     self.xmlparser._get_PubmedArticleSet(xml_tree)

    @pytest.mark.parametrize(
        'pmid, doi, abstract, title, last_name, email', [
            ('31302001', '10.1016/j.molcel.2019.06.008', 'Sirt3, as a major mitochondrial nicotinamide', 'SENP1-Sirt3 Signaling Controls Mitochondrial', 'Cheng', 'jkcheng@shsmu.edu.cn'),
            ('22454523', '10.1242/jcs.103564', 'Botulinum neurotoxins (BoNTs) are classified', 'Botulinum neurotoxin D-C uses synaptotagmin', 'Dong', None)
            ]
    )
    def test_complete_citation_attributes_match(self, pmid, doi, abstract, title, last_name, email, double_xml):
        parse_result = self.xmlparser.parse(double_xml)
        result = next(r for r in parse_result if r.pmid == pmid)
        assert result.doi == doi
        assert abstract in result.abstract
        assert title in result.title
        anauthor = next(author for author in result.author_list if author.last_name == last_name)
        assert anauthor is not None
        assert email in anauthor.emails if email is not None else True