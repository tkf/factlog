import unittest
import textwrap
import io

from ..accessinfo import AccessInfo


class MockedAccessInfo(AccessInfo):

    _lines_at_point = []
    _title = None

    def _get_lines_at_point(self, *args):
        self._get_lines_at_point_args = args
        return self._lines_at_point

    def write_path_and_title(self, file, newline='\n', separator=':'):
        get_title = lambda x: self._title
        super(MockedAccessInfo, self).write_path_and_title(
            file, newline, separator, _get_title=get_title)


class TestAccessInfo(unittest.TestCase):

    def setUp(self):
        self.info = MockedAccessInfo('PATH', 10, 'DUMMY', 'write')
        self.output = io.BytesIO()

    def test_write_paths_and_lines(self):
        pre_lines = 2
        post_lines = 3
        self.info._lines_at_point = [
            (1, 'LINE AT POINT'),
            (2, 'LINE AT POINT'),
            (3, 'LINE AT POINT'),
            (4, 'LINE AT POINT'),
        ]
        self.info.write_paths_and_lines(self.output, pre_lines, post_lines)
        self.assertEqual(
            self.output.getvalue(),
            textwrap.dedent("""\
            PATH:1:LINE AT POINT
            PATH:2:LINE AT POINT
            PATH:3:LINE AT POINT
            PATH:4:LINE AT POINT
            """))
        self.assertEqual(self.info._get_lines_at_point_args,
                         (pre_lines, post_lines))

    def test_write_path_and_title_not_found(self):
        self.info.write_path_and_title(self.output)
        self.assertEqual(self.output.getvalue(), "PATH\n")

    def test_write_path_and_title_found(self):
        self.info._title = 'TITLE'
        self.info.write_path_and_title(self.output)
        self.assertEqual(self.output.getvalue(), "PATH:TITLE\n")
