# import pytest
# from ncbiutils.pmcxmlparser import PmcXmlParser
# from ncbiutils.xml import _from_raw

# #############################
# #   Unit tests
# #############################


# def test_from_file_returns_xmltree(shared_datadir):
#     data = (shared_datadir / 'double.xml').read_bytes()
#     xml_tree = _from_raw(data)
#     assert xml_tree.docinfo.xml_version == '1.0'
#     assert '<!DOCTYPE pmc-articleset' in xml_tree.docinfo.doctype


# class TestPubmedXmlParserClass(object):
#     xmlparser = PubmedXmlParser()

#     @pytest.fixture
#     def double_xml(self, shared_datadir):
#         data = (shared_datadir / 'double.xml').read_bytes()
#         return data

#     def test_parse_returns_citation_list(self, double_xml):
#         parse_result = self.xmlparser.parse(double_xml)
#         first_result = next(parse_result)
#         assert first_result is not None
#         assert isinstance(first_result, Citation)

#     def test_get_pubmed_article_set(self, double_xml):
#         xml_tree = _from_raw(double_xml)
#         pubmed_article_set = self.xmlparser._get_PubmedArticleSet(xml_tree)
#         assert len(pubmed_article_set) == 2

#     def test_parse_no_pubmedarticleset(self, shared_datadir):
#         data = (shared_datadir / 'no_pubmedarticleset.xml').read_bytes()
#         xml_tree = _from_raw(data)
#         with pytest.raises(ValueError):
#             self.xmlparser._get_PubmedArticleSet(xml_tree)

#     def test_duplicate_pmid(self, shared_datadir):
#         data = (shared_datadir / 'duplicate.xml').read_bytes()
#         parse_result = self.xmlparser.parse(data)
#         result = list(parse_result)
#         assert len(result) == 0

#     @pytest.mark.parametrize(
#         'pmid, pmc, doi, abstract, title, last_name, email, jtitle, issn, volume, issue, pub_year, pub_type',
#         [
#             (
#                 '31302001',
#                 None,
#                 '10.1016/j.molcel.2019.06.008',
#                 'Sirt3, as a major mitochondrial nicotinamide',
#                 'SENP1-Sirt3 Signaling Controls Mitochondrial',
#                 'Cheng',
#                 'jkcheng@shsmu.edu.cn',
#                 'Molecular cell',
#                 '1097-4164',
#                 '75',
#                 '4',
#                 '2019',
#                 'D016428',
#             ),
#             (
#                 '22454523',
#                 'PMC4067266',
#                 '10.1242/jcs.103564',
#                 'Botulinum neurotoxins (BoNTs) are classified',
#                 'Botulinum neurotoxin D-C uses synaptotagmin',
#                 'Dong',
#                 None,
#                 'Journal of cell science',
#                 '1477-9137',
#                 '125',
#                 'Pt 13',
#                 '2012',
#                 'D016428',
#             ),
#         ],
#     )
#     def test_complete_citation_attributes_match(
#         self,
#         pmid,
#         pmc,
#         doi,
#         abstract,
#         title,
#         last_name,
#         email,
#         jtitle,
#         issn,
#         volume,
#         issue,
#         pub_year,
#         pub_type,
#         double_xml,
#     ):
#         parse_result = self.xmlparser.parse(double_xml)
#         result = next(r for r in parse_result if r.pmid == pmid)
#         assert result.pmc == pmc
#         assert result.doi == doi
#         assert abstract in result.abstract
#         assert title in result.title
#         anauthor = next(author for author in result.author_list if author.last_name == last_name)
#         assert anauthor is not None
#         assert email in anauthor.emails if email is not None else True
#         journal = result.journal
#         assert journal.title == jtitle
#         assert issn in journal.issn
#         assert journal.volume == volume
#         assert journal.issue == issue
#         assert journal.pub_year == pub_year
#         assert pub_type in result.publication_type_list

