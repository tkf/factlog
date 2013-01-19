import sys
import itertools

from .config import ConfigStore
from .database import DataBase


def get_db(*args, **kwds):
    config = ConfigStore(*args, **kwds)
    return DataBase(config.db_path)


def record_add_arguments(parser):
    parser.add_argument('file_path')
    parser.add_argument('--activity-type', default='write',
                        choices=DataBase.ACTIVITY_TYPES)
    parser.add_argument('--file-point', type=int)


def record_run(file_path, file_point, activity_type):
    """
    Record activities on file.
    """
    db = get_db()
    db.record_file_log(
        file_path, file_point=file_point, activity_type=activity_type)


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


def list_add_arguments(parser):
    import argparse
    parser.add_argument(
        '--limit', type=int, default=20,
        help="Maximum number of files to list.")
    parser.add_argument(
        '--activity-type', '-a', dest='activity_types',
        action='append', choices=DataBase.ACTIVITY_TYPES,
        help="""
        Activity types to include.
        This option can be called multiple times.
        Default is to include all activities.
        """)
    parser.add_argument(
        '--output', default='-', type=argparse.FileType('w'),
        help='file to write output. "-" means stdout.')


def list_run(limit, activity_types, output):
    """
    List recently accessed files.
    """
    separator = '\n'
    db = get_db()
    paths = db.list_file_path(
        limit, activity_types)
    output.writelines(interleave(paths, itertools.repeat(separator)))
    if output is not sys.stdout:
        output.close()


commands = [
    ('record', record_add_arguments, record_run),
    ('list', list_add_arguments, list_run),
]
