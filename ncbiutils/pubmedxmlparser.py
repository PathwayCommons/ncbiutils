from pydantic import BaseModel


class PubMedXmlParser(BaseModel):
    """
    A base class for other parsers

    Class attributes
    ----------

    Attributes
    ----------

    Methods
    ----------
    parse(xml: str)
        Return a dictionary of data given PubMed XML

    """

    pass

    def parse(self):
        pass