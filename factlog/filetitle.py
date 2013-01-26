"""
File title extractor.
"""

import os
import re
import ast
from itertools import imap, ifilter, izip, tee


def gene_iparse_underline_headings(symbols):
    underline_re = re.compile(r'({0})\1* *$'.format(symbols))

    def iparse_underline_headings(lines):
        lines = iter(lines)
        previous = lines.next()
        yield
        for line in lines:
            if underline_re.match(line.rstrip()):
                yield previous
            else:
                yield
            previous = line

    return iparse_underline_headings


def gene_iparse_prefix_headings(regexp):
    prefix_re = re.compile(r'^{0} .+'.format(regexp))

    def iparse_prefix_headings(lines):
        for line in lines:
            if prefix_re.match(line):
                yield line.strip("#").strip()
            else:
                yield

    return iparse_prefix_headings

iparse_md_underline_headings = gene_iparse_underline_headings(r'[=\-]')
iparse_rst_underline_headings = gene_iparse_underline_headings(
    '[!-/:-@[-`{-~]')
# See also: docutils.parsers.rst.states.Body.pats['nonalphanum7bit']

iparse_sharps_headings = gene_iparse_prefix_headings('#{1,6}')
iparse_asterisk_headings = gene_iparse_prefix_headings(r'\*+')


def first(iterative):
    for item in iterative:
        return item


def get_first_heading(lines, parsers):
    lines = imap(str.rstrip, lines)
    iteratives = map(lambda p, ls: p(ls), parsers, tee(lines, len(parsers)))
    candidates = first(ifilter(any, izip(*iteratives)))
    if candidates:
        return first(ifilter(None, candidates))  # get non-None candidate


def get_title_rst(path):
    return get_first_heading(
        open(path).xreadlines(),
        [iparse_rst_underline_headings])


def get_title_md(path):
    return get_first_heading(
        open(path).xreadlines(),
        [iparse_md_underline_headings, iparse_sharps_headings])


def get_title_org(path):
    return get_first_heading(
        open(path).xreadlines(),
        [iparse_asterisk_headings])


def get_title_py(path):
    # FIXME: Find more quick way to get file title of Python file.
    # Parsing python file using ast module can be pretty slow because
    # it parses entire file.
    with open(path) as f:
        node = ast.parse(f.read())
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
        return func(path)


def write_path_and_title(file, path, showpath, newline, separator):
    r"""
    Write `showpath` to `file` with its title if found.

    Following line is written to the `file`::

      {showpath}{separator}{title}{newline}
                \________________/
                  written only when title is found.

    Title is searched in the file specified by `path`.

    """
    file.write(showpath)
    title = get_title(path)
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
