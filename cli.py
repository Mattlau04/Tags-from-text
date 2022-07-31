from rule import load_rules
from utils import is_regex_valid, test_regex, single_space


def do_cli(input_string: str) -> None:
    """The whole CLI program"""

    # First we load the rules
    rules = load_rules()

    # The we find the ones that match
    tags = ""
    for r in rules:
        # If the regex is valid
        if is_regex_valid(r.regex):
            # If the regex matches
            if test_regex(r.regex, input_string):
                # We add the tags
                tags += r.tags + ' '

    # We remove duplicates
    tags = ' '.join( set(tags.split(' ')) )
    # We make sure there's only on space at max between tags
    tags = single_space(tags).strip()
    # Then we finally output
    print(tags)
