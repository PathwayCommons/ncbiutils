from typing import Optional, List
from lxml import etree
from typing_extensions import TypeAlias

#############################
#   Aliases
#############################

XmlTree: TypeAlias = etree._ElementTree
Element: TypeAlias = etree._Element

##################################
#   XML package-specific
##################################


def _from_raw(data: bytes) -> XmlTree:
    """Parse an xml tree representation from bytes

    Do not provide parser text - ambiguity wrt prolog encoding can occur
    See https://lxml.de/parsing.html#python-unicode-strings
    """
    root = etree.XML(data)
    element_tree = etree.ElementTree(root)
    return element_tree


def _find_all(element: Element, xpath: str) -> List[Element]:
    """Wrapper for finding elements for xpath query, possibly empty"""
    return element.findall(xpath)


def _find_safe(element: Element, xpath: str) -> Optional[Element]:
    """Safe find, where None is returned in case xpath query returns no element"""
    optional = element.find(xpath)
    return optional if etree.iselement(optional) else None


def _text_safe(element: Element, xpath: str) -> Optional[str]:
    """Safe get for element text, where None is returned in case xpath query returns no element"""
    optional = _find_safe(element, xpath)
    return optional.text if optional is not None else None


def _collect_element_text(element: Element) -> str:
    """Collect all text from child elements as a single string

    Note: This implemenation essentially ignores text and math markup
    """
    return ' '.join(element.xpath('string()').split())


def _collect_element_text_with_prefix(element: Element, attribute: str):
    """Collect all text from child elements, prefixed by attribute from this Element"""
    prefix = element.get(attribute)
    text = _collect_element_text(element)
    return ': '.join([prefix, text]) if prefix else text
