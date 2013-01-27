import itertools

from .py3compat import map


def repeat(item, num):
    return itertools.islice(itertools.repeat(item), num)


def interleave(*iteratives):
    """
    Return an iterator that interleave elements from given `iteratives`.

    >>> list(interleave([1, 2, 3], itertools.repeat(None)))
    [1, None, 2, None, 3, None]

    """
    iters = list(map(iter, iteratives))
    while True:
        for it in iters:
            yield next(it)


def uniq(seq, key=lambda x: x):
    """
    Return unique elements in `seq`, preserving the order.

    >>> list(uniq([0, 1, 0, 2, 1, 2]))
    [0, 1, 2]
    >>> list(uniq(enumerate('iljkiljk'), key=lambda x: x[1]))
    [(0, 'i'), (1, 'l'), (2, 'j'), (3, 'k')]

    """
    seen = set()
    for i in seq:
        k = key(i)
        if k not in seen:
            yield i
            seen.add(k)
