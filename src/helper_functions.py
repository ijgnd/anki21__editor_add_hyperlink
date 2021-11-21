import re

from .config import gc

def escape_html_chars(s):
    """
    Escape HTML characters in a string. Return a safe string.
    >>> escape_html_chars(u"this&that")
    u'this&amp;that'
    >>> escape_html_chars(u"#lorem")
    u'#lorem'
    """
    if not s:
        return ""

    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }

    result = "".join(html_escape_table.get(c, c) for c in s)
    return result


def some_percent_encoding(s):
    # https://en.wikipedia.org/wiki/Help:URL#Fixing_links_with_unsupported_characters
    replacements = {
    # " ": "%20",
    '"': "%22",
    # "'": "%27",
    # ",": "%2C",
    # ";": "%3B",
    # "<": "%3C",
    # ">": "%3E",
    # "?": "%3F",
    # "[": "%5B",
    # "]": "%5D",
    # "{": "%7B",
    # "|": "%7C",
    # "}": "%7D",
    }
    result = "".join(replacements.get(c, c) for c in s)
    return result
 	 		 	 	 	 


def is_valid_url(string):
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, string)


def combine_to_hyperlink(url, text):
    # Create a hyperlink string, where `url` is the hyperlink reference
    # and `text` the content of the tag.
    text = escape_html_chars(text)
    if gc("remove whitespace from beginning and end of urls"):
        url = url.strip()
    if gc("encode_illegal_characters_in_links"):
        url = some_percent_encoding(url)
    out = "<a href=\"{0}\">{1}</a>".format(url, text)
    return out
