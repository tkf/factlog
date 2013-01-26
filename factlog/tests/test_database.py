import os
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


class InMemoryDataBase(DataBase):

    def __init__(self):
        import sqlite3
        db = sqlite3.connect(':memory:')
        self._get_db = lambda: db
        self._init_db()


class TestInMemoryDataBase(unittest.TestCase):

    dbclass = InMemoryDataBase

    def abspath(self, *ps):
        return os.path.join(os.path.sep, *ps)

    def setUp(self):
        self.db = self.dbclass()
        self.paths = [
            self.abspath('DUMMY', 'PATH', '{0:02d}'.format(i))
            for i in range(100)
        ]

    def test_record_and_search(self):
        self.db.record_file_log(self.paths[0], 'write')
        self.db.record_file_log(self.paths[1], 'open')
        self.db.record_file_log(self.paths[2], 'close')
        rows = list(self.db.search_file_log(10, only_existing=False))
        self.assertEqual(
            [i.path for i in rows],
            self.paths[:3])
        self.assertEqual(
            [i.type for i in rows],
            ['write', 'open', 'close'])

    def test_record_file_point(self):
        atype = 'write'
        point = 23
        self.db.record_file_log(self.paths[0], atype, file_point=point)
        rows = list(self.db.search_file_log(10, only_existing=False))
        info = rows[0]
        self.assertEqual(len(rows), 1)
        self.assertEqual(info.path, self.paths[0])
        self.assertEqual(info.type, atype)
        self.assertEqual(info.point, point)
