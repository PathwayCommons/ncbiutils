from ncbiutils.pubmedxmlparser import PubMedXmlParser

# #############################
# #   Unit tests
# #############################


class TestPubMedXmlParserClass:
    xmlparser = PubMedXmlParser()

    def test_parse_exists(self):
        assert self.xmlparser.parse is not None
