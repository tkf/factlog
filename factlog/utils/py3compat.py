import sys
PY3 = (sys.version_info[0] >= 3)


try:
    from string import count
except ImportError:
    count = str.count


try:
    from itertools import imap as map, izip as zip, ifilter as filter
except ImportError:
    map = map
    zip = zip
    filter = filter
