import regex

def regex_searcher(pattern: str, string: str):
    """
    Safely searches for a regex pattern in a string with a timeout.
    Returns the match object if found, else False.
    """
    try:
        search = regex.search(pattern, string, timeout=6)  # Timeout to prevent hanging
        return search
    except regex.TimeoutError:
        # Regex took too long to execute
        return False
    except Exception:
        # Any other exception (invalid regex, etc.)
        return False


def infinite_loop_check(pattern: str) -> bool:
    """
    Checks the regex pattern for potential catastrophic backtracking patterns.
    Returns True if risky patterns are found.
    """
    loop_patterns = [
        r"\((.{1,}[\+\*]){1,}\)[\+\*].",            # Nested quantifiers like (a+)+
        r"[\(\[].{1,}\{\d+,?\}[\)\]]\{\d+,?\}",     # Repeated quantifiers {m}{n}
        r"\(.{1,}\)\{.{1,}(,)?\}\(.*\)(\+|\*|\{.*\})",  # Complex nested patterns
    ]
    
    for lp in loop_patterns:
        if regex.search(lp, pattern):
            return True
    return False
