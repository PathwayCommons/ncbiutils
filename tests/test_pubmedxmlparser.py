import pytest
from ncbiutils.pubmedxmlparser import PubmedXmlParser
from ncbiutils.pubmed import Citation
from ncbiutils.xml import _from_raw

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
        xml_tree = _from_raw(data)
        return xml_tree

    def test_parse_returns_citation_list(self, double_xml):
        parse_result = self.xmlparser.parse(double_xml)
        first_result = next(parse_result)
        assert first_result is not None
        assert isinstance(first_result, Citation)

    def test_get_pubmed_article_set(self, double_xml):
        pubmed_article_set = self.xmlparser._get_PubmedArticleSet(double_xml)
        assert len(pubmed_article_set) == 2

    def test_parse_no_pubmedarticleset(self, shared_datadir):
        data = (shared_datadir / 'no_pubmedarticleset.xml').read_bytes()
        xml_tree = _from_raw(data)
        with pytest.raises(ValueError):
            self.xmlparser._get_PubmedArticleSet(xml_tree)

    def test_duplicate_pmid(self, shared_datadir):
        data = (shared_datadir / 'duplicate.xml').read_bytes()
        parse_result = self.xmlparser.parse(_from_raw(data))
        result = list(parse_result)
        assert len(result) == 0

    @pytest.mark.parametrize(
        'pmid, pmc, doi, abstract, title, last_name, email, jtitle, isoabbrev,'
        ' issn, volume, issue, pub_year, pub_type, mesh_heading',
        [
            (
                '31302001',
                None,
                '10.1016/j.molcel.2019.06.008',
                'Sirt3, as a major mitochondrial nicotinamide',
                'SENP1-Sirt3 Signaling Controls Mitochondrial',
                'Cheng',
                'jkcheng@shsmu.edu.cn',
                'Molecular cell',
                'Mol Cell',
                '1097-4164',
                '75',
                '4',
                '2019',
                'D016428',
                {
                    'descriptor_name': {'ui': 'D008928', 'value': 'Mitochondria'},
                    'qualifier_name': [
                        {'ui': 'Q000235', 'value': 'genetics'},
                        {'ui': 'Q000378', 'value': 'metabolism'},
                        {'ui': 'Q000473', 'value': 'pathology'},
                    ],
                },
            ),
            (
                '22454523',
                'PMC4067266',
                '10.1242/jcs.103564',
                'Botulinum neurotoxins (BoNTs) are classified',
                'Botulinum neurotoxin D-C uses synaptotagmin',
                'Dong',
                None,
                'Journal of cell science',
                'J Cell Sci',
                '1477-9137',
                '125',
                'Pt 13',
                '2012',
                'D016428',
                {
                    'descriptor_name': {'ui': 'D050861', 'value': 'Synaptotagmin II'},
                    'qualifier_name': [{'ui': 'Q000378', 'value': 'metabolism'}],
                },
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
        isoabbrev,
        issn,
        volume,
        issue,
        pub_year,
        pub_type,
        mesh_heading,
        double_xml,
    ):
        parse_result = self.xmlparser.parse(double_xml)
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
        assert journal.iso_abbreviation == isoabbrev
        assert issn in journal.issn
        assert journal.volume == volume
        assert journal.issue == issue
        assert journal.pub_year == pub_year
        assert pub_type in result.publication_type_list
        ameshheading = next(
            heading
            for heading in result.mesh_list
            if heading['descriptor_name']['ui'] == mesh_heading['descriptor_name']['ui']
        )
        assert ameshheading['descriptor_name']['value'] == mesh_heading['descriptor_name']['value']
        qualifier_values = [qualifier['value'] for qualifier in mesh_heading['qualifier_name']]
        aqualifiername = next(
            qualifier
            for qualifier in ameshheading['qualifier_name']
            if qualifier['ui'] == mesh_heading['qualifier_name'][0]['ui']
        )
        assert aqualifiername['value'] in qualifier_values

    @pytest.mark.parametrize(
        'pmid, doi, abstract, title, last_name, email, jtitle, isoabbrev, issn, volume, issue, pub_year, pub_type',
        [
            (
                '33279447',
                '10.1016/j.reuma.2020.11.001',
                None,
                '',
                'Vicente Moreno',
                'dr.vicentemoreno@gmail.com',
                'Reumatologia clinica',
                'Reumatol Clin (Engl Ed)',
                '2173-5743',
                None,
                None,
                '2020',
                'D016428',
            ),
        ],
    )
    def test_no_abstract_empty_title(
        self,
        pmid,
        doi,
        abstract,
        title,
        last_name,
        email,
        jtitle,
        isoabbrev,
        issn,
        volume,
        issue,
        pub_year,
        pub_type,
        shared_datadir,
    ):
        data = (shared_datadir / 'no_title_abstract.xml').read_bytes()
        parse_result = self.xmlparser.parse(_from_raw(data))
        result = next(r for r in parse_result if r.pmid == pmid)
        assert result.doi == doi
        assert result.abstract is abstract
        assert result.title == title
        anauthor = next(author for author in result.author_list if author.last_name == last_name)
        assert anauthor is not None
        assert email in anauthor.emails if email is not None else True
        journal = result.journal
        assert journal.title == jtitle
        assert journal.iso_abbreviation == isoabbrev
        assert issn in journal.issn
        assert journal.volume == volume
        assert journal.issue == issue
        assert journal.pub_year == pub_year
        assert pub_type in result.publication_type_list
        assert result.mesh_list is None

    @pytest.mark.parametrize(
        'pmid, pmc, doi, abstract, title, last_name, email, collective_name, jtitle, isoabbrev,'
        ' issn, volume, issue, pub_year, pub_type, mesh_heading',
        [
            (
                '30158200',
                'PMC6113773',
                '10.1136/bmj.k3225',
                'RESULTS: Of 15 fracture associated loci identified, all were also associated with bone mineral',
                'Assessment of the genetic and clinical determinants of',
                'Rivadeneira',
                'brent.richards@mcgill.ca',
                'GEFOS/GENOMOS consortium and the 23andMe research team',
                'BMJ (Clinical research ed.)',
                'BMJ',
                '1756-1833',
                '362',
                None,
                '2018',
                'D017418',
                {
                    'descriptor_name': {'ui': 'D010024', 'value': 'Osteoporosis'},
                    'qualifier_name': [
                        {'ui': 'Q000453', 'value': 'epidemiology'},
                        {'ui': 'Q000235', 'value': 'genetics'},
                        {'ui': 'Q000503', 'value': 'physiopathology'},
                    ],
                },
            ),
        ],
    )
    def test_strucabstract_markup_collectivename(
        self,
        pmid,
        pmc,
        doi,
        abstract,
        title,
        last_name,
        email,
        collective_name,
        jtitle,
        isoabbrev,
        issn,
        volume,
        issue,
        pub_year,
        pub_type,
        mesh_heading,
        shared_datadir,
    ):
        data = (shared_datadir / 'markup.xml').read_bytes()
        parse_result = self.xmlparser.parse(_from_raw(data))
        result = next(r for r in parse_result if r.pmid == pmid)
        assert result.pmc == pmc
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
        assert journal.iso_abbreviation == isoabbrev
        assert issn in journal.issn
        assert journal.volume == volume
        assert journal.issue == issue
        assert journal.pub_year == pub_year
        assert pub_type in result.publication_type_list
        ameshheading = next(
            heading
            for heading in result.mesh_list
            if heading['descriptor_name']['ui'] == mesh_heading['descriptor_name']['ui']
        )
        assert ameshheading['descriptor_name']['value'] == mesh_heading['descriptor_name']['value']
        qualifier_values = [qualifier['value'] for qualifier in mesh_heading['qualifier_name']]
        aqualifiername = next(
            qualifier
            for qualifier in ameshheading['qualifier_name']
            if qualifier['ui'] == mesh_heading['qualifier_name'][0]['ui']
        )
        assert aqualifiername['value'] in qualifier_values

    @pytest.mark.parametrize(
        'pmid, pmc, doi, abstract, title, last_name, orcid, jtitle, isoabbrev,'
        ' issn, volume, issue, pub_year, pub_type, mesh_heading',
        [
            (
                '32820036',
                'PMC7462063',
                '10.1101/gad.337584.120',
                'In Ptch1 +/- ; Bcor ΔE9-10 tumors',
                'Functional loss of a noncanonical BCOR-PRC1.1',
                'Kutscher',
                '0000-0002-1130-4582',
                'Genes & development',
                'Genes Dev',
                '1549-5477',
                '34',
                '17-18',
                '2020',
                'D052061',
                {
                    'descriptor_name': {'ui': 'D015972', 'value': 'Gene Expression Regulation, Neoplastic'},
                    'qualifier_name': [{'ui': 'Q000235', 'value': 'genetics'}],
                },
            ),
        ],
    )
    def test_markup_orcid(
        self,
        pmid,
        pmc,
        doi,
        abstract,
        title,
        last_name,
        orcid,
        jtitle,
        isoabbrev,
        issn,
        volume,
        issue,
        pub_year,
        pub_type,
        mesh_heading,
        shared_datadir,
    ):
        data = (shared_datadir / 'orcid.xml').read_bytes()
        parse_result = self.xmlparser.parse(_from_raw(data))
        result = next(r for r in parse_result if r.pmid == pmid)
        assert result.pmc == pmc
        assert result.doi == doi
        assert abstract in result.abstract
        assert title in result.title
        anauthor = next(author for author in result.author_list if author.last_name == last_name)
        assert anauthor is not None
        assert orcid == anauthor.orcid
        journal = result.journal
        assert journal.title == jtitle
        assert journal.iso_abbreviation == isoabbrev
        assert issn in journal.issn
        assert journal.volume == volume
        assert journal.issue == issue
        assert journal.pub_year == pub_year
        assert pub_type in result.publication_type_list
        ameshheading = next(
            heading
            for heading in result.mesh_list
            if heading['descriptor_name']['ui'] == mesh_heading['descriptor_name']['ui']
        )
        assert ameshheading['descriptor_name']['value'] == mesh_heading['descriptor_name']['value']
        qualifier_values = [qualifier['value'] for qualifier in mesh_heading['qualifier_name']]
        aqualifiername = next(
            qualifier
            for qualifier in ameshheading['qualifier_name']
            if qualifier['ui'] == mesh_heading['qualifier_name'][0]['ui']
        )
        assert aqualifiername['value'] in qualifier_values
