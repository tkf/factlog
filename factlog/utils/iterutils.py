# Copyright (c) 2013- Takafumi Arakaki

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


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
