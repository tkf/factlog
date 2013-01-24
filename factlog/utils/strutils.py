from string import count


def remove_prefix(prefixes, string):
    """
    Remove prefix of string if one of the candidate in `prefixes` matches.

    >>> remove_prefix(['aaa', 'aa', 'a'], 'aaax')
    'x'
    >>> remove_prefix(['aaa', 'aa', 'a'], 'aax')
    'x'

    """
    for pre in prefixes:
        if string.startswith(pre):
            return string[len(pre):]
    return string


def get_lineno_at_point(string, point):
    r"""
    Get 1-based line number at given `point`.

    >>> string = '''\
    ... 1
    ... 34
    ... 678
    ... '''
    >>> get_lineno_at_point(string, 3)
    2
    >>> get_lineno_at_point(string, 6)
    3
    >>> get_lineno_at_point(string, 7)
    3

    """
    return count(string, '\n', 0, point - 1) + 1


def get_lines_at_point(string, point, pre_lines=0, post_lines=0):
    r"""
    Get lines containing point.

    :type      string: str
    :arg       string: target string
    :type       point: int
    :arg        point: 1-origin index to specify a point
    :type   pre_lines: int
    :arg    pre_lines: number of previous lines to include (default: 0)
    :type  post_lines: int
    :arg   post_lines: number of post lines to include (default: 0)

    :rtype: list of tuple of int and str
    :return: Pairs of 1-based line number and line.
             Newline at the end of lines are stripped off.

    >>> string = '''\
    ... 1
    ... 3
    ... 5
    ... 7
    ... 9
    ... '''
    >>> get_lines_at_point(string, 5)
    [(3, '5')]
    >>> get_lines_at_point(string, 5, 2, 1)
    [(1, '1'), (2, '3'), (3, '5'), (4, '7')]
    >>> get_lines_at_point(string, 3, 2)  # not enough previous lines
    [(1, '1'), (2, '3')]
    >>> get_lines_at_point(string, 7, 0, 2)  # not enough post lines
    [(4, '7'), (5, '9')]

    """
    line_no = get_lineno_at_point(string, point) - 1  # 0-origin
    i = max(line_no - pre_lines, 0)
    j = line_no + post_lines + 1
    return zip(range(i + 1, j + 1), string.splitlines()[i:j])
