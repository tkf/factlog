import unittest
import textwrap
import io

from .test_accessinfo import MockedAccessInfo


class TestWriteListedRows(unittest.TestCase):

    def gene_lines_at_point(self, *args):
        return [(i, 'LINE AT POINT') for i in range(*args)]

    def setUp(self):
        ai = MockedAccessInfo
        self.rows = [
            ai('PATH-A', lines_at_point=self.gene_lines_at_point(2)),
            ai('PATH-B', lines_at_point=self.gene_lines_at_point(1)),
        ]
        self.output = io.BytesIO()
        self.output.close = lambda *_: None

    def write_listed_rows(
            self, newline='\n', title=False,
            before_context=None, after_context=None, context=None):
        from ..record import write_listed_rows
        write_listed_rows(
            self.rows, newline, self.output, title,
            before_context, after_context, context)

    def test_title(self):
        self.write_listed_rows(title=True)
        self.assertEqual(
            self.output.getvalue(),
            textwrap.dedent("""\
            PATH-A
            PATH-B
            """))

    def test_context(self):
        self.write_listed_rows(context=100)
        self.assertEqual(
            self.output.getvalue(),
            textwrap.dedent("""\
            PATH-A:0:LINE AT POINT
            PATH-A:1:LINE AT POINT
            PATH-B:0:LINE AT POINT
            """))

    def test_plain(self):
        self.write_listed_rows()
        self.assertEqual(
            self.output.getvalue(),
            textwrap.dedent("""\
            PATH-A
            PATH-B
            """))
