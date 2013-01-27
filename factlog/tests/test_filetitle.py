import unittest

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
        import textwrap
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
