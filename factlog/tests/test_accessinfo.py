import unittest
import textwrap
import io

from ..database import AccessInfo


class MockedAccessInfo(AccessInfo):

    _lines_at_point = []

    def _get_lines_at_point(self, *args):
        self._get_lines_at_point_args = args
        return self._lines_at_point


class TestSequenceFunctions(unittest.TestCase):

    def test_write_paths_and_lines(self):
        info = MockedAccessInfo('PATH', 10, 'DUMMY', 'write')
        pre_lines = 2
        post_lines = 3
        info._lines_at_point = [
            (1, 'LINE AT POINT'),
            (2, 'LINE AT POINT'),
            (3, 'LINE AT POINT'),
            (4, 'LINE AT POINT'),
        ]
        output = io.BytesIO()
        info.write_paths_and_lines(output, pre_lines, post_lines)
        self.assertEqual(
            output.getvalue(),
            textwrap.dedent("""\
            PATH:1:LINE AT POINT
            PATH:2:LINE AT POINT
            PATH:3:LINE AT POINT
            PATH:4:LINE AT POINT
            """))
        self.assertEqual(info._get_lines_at_point_args,
                         (pre_lines, post_lines))
