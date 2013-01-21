import os
import sys
import itertools

from .config import ConfigStore
from .database import DataBase


def get_db(*args, **kwds):
    config = ConfigStore(*args, **kwds)
    return DataBase(config.db_path)


def record_add_arguments(parser):
    parser.add_argument(
        'file_path',
        help="record an activity on this file.")
    parser.add_argument(
        '--activity-type', '-a', default='write',
        choices=DataBase.ACTIVITY_TYPES,
        help="activity on the file to record.")
    parser.add_argument(
        '--file-point', type=int,
        help="point of cursor at the time of saving.")


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


def remove_prefix(prefixes, string):
    """
    Remove prefix of string if one of the candidate in `prefixes` matches.
    """
    for pre in prefixes:
        if string.startswith(pre):
            return string[len(pre):]
    return string


def list_add_arguments(parser):
    import argparse
    parser.add_argument(
        '--limit', '-l', type=int, default=20,
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
        '--no-unique', dest='unique', action='store_false', default=True,
        help="""
        [WORK IN PROGRESS]
        Include all duplicates.
        """)
    parser.add_argument(
        '--include-glob', metavar='GLOB', default=[], action='append',
        help="""
        Include only paths that match to unix-style GLOB pattern.
        """)
    parser.add_argument(
        '--exclude-glob', metavar='GLOB', default=[], action='append',
        help="""
        Exclude paths that match to unix-style GLOB pattern.
        """)
    parser.add_argument(
        '--under', metavar='PATH', default=[], action='append',
        help="""
        Show only paths under PATH.  See also: --relative.
        """)
    parser.add_argument(
        '--relative', action='store_true',
        help="""
        Output paths relative to the one given by --under.
        """)
    parser.add_argument(
        '--format',
        help="""
        [WORK IN PROGRESS]
        Python-style string format.  {path}: file path; {point}:
        cursor point; {recorded}: timestamp; {activity}: one of
        'open', 'write' and 'close'; {id}: row id.
        """)
    parser.add_argument(
        '--title', action='store_true',
        help="""
        Output title of the file.  Supported file formats are:
        Python, reStructuredText, Markdown, Org-mode.
        It does not work with --line-number.
        """)
    parser.add_argument(
        '--line-number', action='store_true',
        help="""
        [WORK IN PROGRESS]
        Output the line of the file where the cursor located
        at the time of the action.
        Prefix each output line with the 1-based line number,
        like grep's --line-number.
        """)
    parser.add_argument(
        '--after-context', '-A', type=int, metavar='NUM',
        help="""
        [WORK IN PROGRESS]
        Print NUM lines after the cursor line.
        It requires --line-number.
        """)
    parser.add_argument(
        '--before-context', '-B', type=int, metavar='NUM',
        help="""
        [WORK IN PROGRESS]
        Print NUM lines before the cursor line.
        It requires --line-number.
        """)
    parser.add_argument(
        '--context', '-C', type=int, metavar='NUM',
        help="""
        [WORK IN PROGRESS]
        Print NUM lines before and after the cursor line.
        It requires --line-number.
        """)
    parser.add_argument(
        '--null', action='store_true',
        help="""
        [WORK IN PROGRESS]
        Use the NULL character instead of newline for separating
        files.
        """)
    parser.add_argument(
        '--output', default='-', type=argparse.FileType('w'),
        help='file to write output. "-" means stdout.')


def list_run(
        limit, activity_types, output, unique, include_glob, exclude_glob,
        under, relative, title, **_):
    """
    List recently accessed files.
    """
    separator = '\n'
    absunder = [os.path.join(os.path.abspath(p), "") for p in under]
    include_glob += [os.path.join(p, "*") for p in absunder]
    db = get_db()
    paths = showpaths = list(db.list_file_path(
        limit, activity_types, unique, include_glob, exclude_glob))
    if relative:
        showpaths = [remove_prefix(absunder, p) for p in paths]
    if title:
        from .filetitle import write_paths_and_titles
        write_paths_and_titles(output, paths, showpaths, separator)
    else:
        output.writelines(interleave(paths, itertools.repeat(separator)))
    if output is not sys.stdout:
        output.close()


commands = [
    ('record', record_add_arguments, record_run),
    ('list', list_add_arguments, list_run),
]
