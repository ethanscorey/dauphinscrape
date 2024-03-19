import re


def get_regex(pattern: str | re.Pattern, text: str, groups: list):
    """Get matching expression, if it exists, or return empty string."""
    match = re.search(pattern, text)
    if match:
        return "".join(match.group(*groups))
    return ""
