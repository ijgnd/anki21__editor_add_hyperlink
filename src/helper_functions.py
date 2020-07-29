import re


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
    " ": "%20",
    '"': "%22",
    "'": "%27",
    ",": "%2C",
    ";": "%3B",
    "<": "%3C",
    ">": "%3E",
    "?": "%3F",
    "[": "%5B",
    "]": "%5D",
    "{": "%7B",
    "|": "%7C",
    "}": "%7D",
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
