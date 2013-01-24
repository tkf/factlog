def remove_prefix(prefixes, string):
    """
    Remove prefix of string if one of the candidate in `prefixes` matches.
    """
    for pre in prefixes:
        if string.startswith(pre):
            return string[len(pre):]
    return string
