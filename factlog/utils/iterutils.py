import itertools


def repeat(item, num):
    return itertools.islice(itertools.repeat(item), num)


def interleave(*iteratives):
    """
    Return an iterator that interleave elements from given `iteratives`.

    >>> list(interleave([1, 2, 3], itertools.repeat(None)))
    [1, None, 2, None, 3, None]

    """
    iters = map(iter, iteratives)
    while True:
        for it in iters:
            yield next(it)