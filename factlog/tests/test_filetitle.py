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


import unittest
import textwrap
import io

from ..utils.py3compat import PY3
from .. import filetitle


class TestGetTitle(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.rootdir = tempfile.mkdtemp(prefix='factlog-test-')

    def tearDown(self):
        import shutil
        shutil.rmtree(self.rootdir)

    def create_file(self, file_name, content):
        import os
        path = os.path.join(self.rootdir, file_name)
        with open(path, 'wt') as fp:
            fp.write(textwrap.dedent(content))
        return path

    def test_get_title_rst(self):
        path = self.create_file(
            'test.rst',
            """
            Title
            =====
            """)
        self.assertEqual(filetitle.get_title(path), 'Title')

    def test_get_title_md_sharp(self):
        path = self.create_file(
            'test.md',
            """
            # Title
            """)
        self.assertEqual(filetitle.get_title(path), 'Title')

    def test_get_title_md_underline(self):
        path = self.create_file(
            'test.md',
            """
            Title
            =====
            """)
        self.assertEqual(filetitle.get_title(path), 'Title')

    def test_get_title_org(self):
        path = self.create_file(
            'test.org',
            """
            * Title
            """)
        self.assertEqual(filetitle.get_title(path), 'Title')

    def test_get_title_py(self):
        path = self.create_file(
            'test.py',
            """
            '''Title'''
            """)
        self.assertEqual(filetitle.get_title(path), 'Title')


class TestGetTitleNoFS(unittest.TestCase):

    if PY3:
        InMemoryIO = io.StringIO
    else:
        InMemoryIO = io.BytesIO

    def check_get_title(self, content, title, get_title):
        self.fp = fp = self.InMemoryIO()
        fp.write(textwrap.dedent(content))
        fp.seek(0)
        self.assertEqual(get_title(fp), title)

    def check_underline_title(self, underline_symbol, get_title):
        """
        Check underline-based title format.

        Create a file-like object containing the following content
        and run `get_title` on it to see if it returns 'Title'.::

           Title
           xxxxx

        where ``x = underline_symbol``.

        """
        title = 'Title'
        underline = underline_symbol * len(title)
        content = '\n'.join([title, underline])
        self.check_get_title(content, title, get_title)

    def test_get_title_rst_underline_symbols(self):
        import re
        symbols = re.findall(filetitle.NONALPHANUM7BIT,
                             ''.join(map(chr, range(128))))
        for s in symbols:
            self.check_underline_title(s, filetitle.get_title_rst)

    def test_get_title_md_underline_symbols(self):
        for s in '=-':
            self.check_underline_title(s, filetitle.get_title_md)
