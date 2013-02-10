"""
File title extractor.
"""

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


import os
import re
import ast
from itertools import tee

from .utils.py3compat import map, zip, filter


def gene_iparse_underline_headings(symbols):
    underline_re = re.compile(r'({0})\1* *$'.format(symbols))

    def iparse_underline_headings(lines):
        lines = iter(lines)
        previous = next(lines)
        yield
        for line in lines:
            if underline_re.match(line.rstrip()):
                yield previous
            else:
                yield
            previous = line

    return iparse_underline_headings


def gene_iparse_prefix_headings(prefixes):
    prefix_re = re.compile(r'^{0} .+'.format(re.escape(prefixes)))

    def iparse_prefix_headings(lines):
        for line in lines:
            if prefix_re.match(line):
                yield line.strip(prefixes).strip()
            else:
                yield

    return iparse_prefix_headings

NONALPHANUM7BIT = '[!-/:-@[-`{-~]'
# See also: docutils.parsers.rst.states.Body.pats['nonalphanum7bit']
iparse_rst_underline_headings = gene_iparse_underline_headings(NONALPHANUM7BIT)
iparse_md_underline_headings = gene_iparse_underline_headings(r'[=\-]')

iparse_sharps_headings = gene_iparse_prefix_headings('#')
iparse_asterisk_headings = gene_iparse_prefix_headings('*')


def first(iterative):
    for item in iterative:
        return item


def get_first_heading(lines, parsers):
    lines = map(str.rstrip, lines)
    iteratives = map(lambda p, ls: p(ls), parsers, tee(lines, len(parsers)))
    candidates = first(filter(any, zip(*iteratives)))
    if candidates:
        return first(filter(None, candidates))  # get non-None candidate


def get_title_rst(fp):
    parsers = [iparse_rst_underline_headings]
    return get_first_heading(fp, parsers)


def get_title_md(fp):
    parsers = [iparse_md_underline_headings, iparse_sharps_headings]
    return get_first_heading(fp, parsers)


def get_title_org(fp):
    parsers = [iparse_asterisk_headings]
    return get_first_heading(fp, parsers)


def get_title_py(fp):
    # FIXME: Find more quick way to get file title of Python file.
    # Parsing python file using ast module can be pretty slow because
    # it parses entire file.
    node = ast.parse(fp.read())
    doc = ast.get_docstring(node)
    if doc is None:
        return None
    for line in doc.splitlines():
        if line:
            return line


exts_func = [
    (('rst', 'rest'), get_title_rst),
    (('md', 'markdown'), get_title_md),
    (('org',), get_title_org),
    (('py',), get_title_py),
]

dispatcher = dict((ext, func) for (exts, func) in exts_func for ext in exts)


def get_title(path):
    """
    Get title of the document at `path` or None if cannot be retrieved.
    """
    if not os.path.exists(path):
        return None
    ext = os.path.splitext(path)[1].lower()[1:]
    func = dispatcher.get(ext)
    if func:
        with open(path) as fp:
            return func(fp)


def write_path_and_title(file, path, showpath, newline, separator,
                         _get_title=get_title):
    r"""
    Write `showpath` to `file` with its title if found.

    Following line is written to the `file`::

      {showpath}{separator}{title}{newline}
                \________________/
                  written only when title is found.

    Title is searched in the file specified by `path`.

    """
    file.write(showpath)
    title = _get_title(path)
    if title:
        file.write(separator)
        file.write(title)
    file.write(newline)


def write_paths_and_titles(
        file, paths, showpaths=None, newline='\n', separator=':'):
    """
    Write path in `paths` to `file` with its title if found.

    Following line is written in `file` for each path in `paths`::

      {path}{separator}{title}{newline}

    Example line::

        mynote/2013/01/note.rst:Title of my note

    """
    if showpaths is None:
        showpaths = paths
    for (path, show) in zip(paths, showpaths):
        write_path_and_title(file, path, show, newline, separator)


def main(args=None):
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__)
    parser.add_argument(
        'path', nargs='+')
    parser.add_argument(
        '--output', default='-', type=argparse.FileType('w'),
        help='file to write output. "-" means stdout.')
    ns = parser.parse_args(args)
    write_paths_and_titles(ns.output, ns.path)


if __name__ == '__main__':
    main()
