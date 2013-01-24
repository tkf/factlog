import os
import sys
import itertools

from .config import ConfigStore
from .database import DataBase
from .utils.iterutils import interleave
from .utils.strutils import remove_prefix


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
        Include all duplicates.  See also --format.
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
        Print NUM lines after the cursor line.
        It requires --line-number.
        """)
    parser.add_argument(
        '--before-context', '-B', type=int, metavar='NUM',
        help="""
        Print NUM lines before the cursor line.
        It requires --line-number.
        """)
    parser.add_argument(
        '--context', '-C', type=int, metavar='NUM',
        help="""
        Print NUM lines before and after the cursor line.
        It requires --line-number.
        """)
    parser.add_argument(
        '--null', action='store_true',
        help="""
        Use the NULL character instead of newline for separating
        files.
        """)
    parser.add_argument(
        '--output', default='-', type=argparse.FileType('w'),
        help='file to write output. "-" means stdout.')


def list_run(
        limit, activity_types, unique, include_glob, exclude_glob,
        under, null, **kwds):
    """
    List recently accessed files.
    """
    separator = '\0' if null else '\n'
    absunder = [os.path.join(os.path.abspath(p), "") for p in under]
    include_glob += [os.path.join(p, "*") for p in absunder]
    db = get_db()
    rows = db.search_file_log(
        limit, activity_types, unique, include_glob, exclude_glob)
    write_listed_rows(rows, absunder, separator, **kwds)


def write_listed_rows(
        rows, absunder, separator, output, relative, title,
        before_context, after_context, context, **_):
    r"""
    Write `rows` into `output`.

    :type            rows: iterative of :class:`factlog.database.AccessInfo`
    :arg             rows:
    :type        absunder: str
    :arg         absunder: absolute path of the path given by --under
    :type       separator: str
    :arg        separator: '\n' or '\0'
    :type        relative: bool
    :arg         relative:
    :type           title: bool
    :arg            title:
    :type  before_context: int
    :arg   before_context: print this number of line before the point
    :type   after_context: int
    :arg    after_context: print this number of line after the point
    :type         context: int
    :arg          context: print this number of line before and after the point

    """
    rows = (r for r in rows if os.path.exists(r.path))
    rows = list(rows)           # FIXME: optimize!
    paths = showpaths = [r.path for r in rows]
    if relative:
        showpaths = [remove_prefix(absunder, p) for p in paths]
        (showpaths, paths) = zip(*list(dict(zip(showpaths, paths)).items()))
    if title:
        from .filetitle import write_paths_and_titles
        write_paths_and_titles(output, paths, showpaths, separator)
    elif before_context or after_context or context:
        from .utils.fileutils import write_paths_and_lines
        points = (r.point for r in rows)
        pre_lines = next(iter(filter(None, [before_context, context, 0])))
        post_lines = next(iter(filter(None, [after_context, context, 0])))
        write_paths_and_lines(output, paths, points, showpaths, separator,
                              pre_lines=pre_lines, post_lines=post_lines)
    else:
        output.writelines(interleave(showpaths, itertools.repeat(separator)))
    if output is not sys.stdout:
        output.close()


commands = [
    ('record', record_add_arguments, record_run),
    ('list', list_add_arguments, list_run),
]
