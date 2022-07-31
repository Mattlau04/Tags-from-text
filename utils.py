import re


def is_regex_valid(regex: str) -> bool:
    try:
        re.compile(regex)
        return True
    except re.error:
        return False

def test_regex(regex: str, test_string: str) -> bool:
    return bool(re.search(regex, test_string, flags=re.I))

def single_space(s: str) -> str:
    while '  ' in s:
        s = s.replace('  ', ' ')
    return s
