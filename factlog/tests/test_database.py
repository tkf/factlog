import unittest

from ..database import DataBase


def setdefaults(d, **kwds):
    for (k, v) in kwds.items():
        d.setdefault(k, v)


class TestDataBaseScript(unittest.TestCase):

    dbclass = DataBase

    @classmethod
    def script_search_file_log(cls, limit, **kwds):
        setdefaults(kwds, activity_types=None, unique=True,
                    include_glob=[], exclude_glob=[])
        return cls.dbclass._script_search_file_log(limit, **kwds)

    def test_script_search_file_log_simple(self):
        (sql, params) = self.script_search_file_log(50)
        self.assertEqual(
            sql,
            'SELECT file_path, file_point, MAX(recorded), activity_type '
            'FROM file_log '
            'GROUP BY file_path '
            'ORDER BY recorded DESC LIMIT ?')
        self.assertEqual(
            params,
            [50])

    def test_script_search_file_log_only_write(self):
        (sql, params) = self.script_search_file_log(
            50, activity_types=['write'])
        self.assertEqual(
            sql,
            'SELECT file_path, file_point, MAX(recorded), activity_type '
            'FROM file_log '
            'WHERE activity_type in (?) '
            'GROUP BY file_path '
            'ORDER BY recorded DESC LIMIT ?')
        self.assertEqual(params, ['write', 50])

    def test_script_search_file_log_write_or_open(self):
        (sql, params) = self.script_search_file_log(
            50, activity_types=['write', 'open'])
        self.assertEqual(
            sql,
            'SELECT file_path, file_point, MAX(recorded), activity_type '
            'FROM file_log '
            'WHERE activity_type in (?, ?) '
            'GROUP BY file_path '
            'ORDER BY recorded DESC LIMIT ?')
        self.assertEqual(params, ['write', 'open', 50])

    def test_script_search_file_log_include_glob(self):
        (sql, params) = self.script_search_file_log(
            50, include_glob=['*.py', '*.el'])
        self.assertEqual(
            sql,
            'SELECT file_path, file_point, MAX(recorded), activity_type '
            'FROM file_log '
            'WHERE (glob(?, file_path) OR glob(?, file_path)) '
            'GROUP BY file_path '
            'ORDER BY recorded DESC LIMIT ?')
        self.assertEqual(params, ['*.py', '*.el', 50])

    def test_script_search_file_log_exclude_glob(self):
        (sql, params) = self.script_search_file_log(
            50, exclude_glob=['*.py', '*.el'])
        self.assertEqual(
            sql,
            'SELECT file_path, file_point, MAX(recorded), activity_type '
            'FROM file_log '
            'WHERE NOT glob(?, file_path) AND NOT glob(?, file_path) '
            'GROUP BY file_path '
            'ORDER BY recorded DESC LIMIT ?')
        self.assertEqual(params, ['*.py', '*.el', 50])

    def test_script_search_file_log_include_exclude_glob(self):
        (sql, params) = self.script_search_file_log(
            50, include_glob=['*.py', '*.el'], exclude_glob=['/home/*'])
        self.assertEqual(
            sql,
            'SELECT file_path, file_point, MAX(recorded), activity_type '
            'FROM file_log '
            'WHERE (glob(?, file_path) OR glob(?, file_path)) '
            'AND NOT glob(?, file_path) '
            'GROUP BY file_path '
            'ORDER BY recorded DESC LIMIT ?')
        self.assertEqual(params, ['*.py', '*.el', '/home/*', 50])

    def test_script_search_file_log_no_unique(self):
        (sql, params) = self.script_search_file_log(
            50, unique=False)
        self.assertEqual(
            sql,
            'SELECT file_path, file_point, recorded, activity_type '
            'FROM file_log '
            'ORDER BY recorded DESC LIMIT ?')
        self.assertEqual(params, [50])
