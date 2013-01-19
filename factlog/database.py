import os
import itertools
import sqlite3
from contextlib import closing


class DataBase(object):

    ACTIVITY_TYPES = ('write', 'open', 'close')

    schemapath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'schema.sql')

    def __init__(self, dbpath):
        self.dbpath = dbpath
        if not os.path.exists(dbpath):
            self._init_db()

    def _get_db(self):
        """Returns a new connection to the database."""
        return sqlite3.connect(self.dbpath)

    def _init_db(self):
        """Creates the database tables."""
        from .__init__ import __version__ as version
        with closing(self._get_db()) as db:
            with open(self.schemapath) as f:
                db.cursor().executescript(f.read())
            db.execute(
                'INSERT INTO system_info (version) VALUES (?)',
                [version])
            db.commit()

    def record_file_log(self, file_path, activity_type, file_point=None):
        """
        Record file activity.

        :type     file_path: str
        :arg      file_path: path to the file
        :type    file_point: int or None
        :arg     file_point: point of cursor at the time of saving.
        :type activity_type: str
        :arg  activity_type: one of 'write', 'open', 'close'

        `file_path` is converted to absolute path before saving
        to the database.

        """
        # FIXME: Record file existence.  If it does not exist when
        #        opened and it does after the next save, it means that
        #        the file is created at that time.
        # FIXME: Add more activities (if possible):
        #        create/delete/move/copy
        assert activity_type in self.ACTIVITY_TYPES
        file_path = os.path.abspath(file_path)
        with closing(self._get_db()) as db:
            db.execute(
                """
                INSERT INTO file_log (file_path, file_point, activity_type)
                VALUES (?, ?, ?)
                """,
                [file_path, file_point, activity_type])
            db.commit()

    @staticmethod
    def _script_list_file_path(limit, activity_types, unique):
        columns = 'file_path'
        if unique:
            # FIXME: make sure that the selected row is the most recent one
            columns = 'DISTINCT ' + columns
        if activity_types is None:
            where = ''
        else:
            where = ' WHERE activity_type in ({0}) '.format(
                ', '.join(itertools.islice(itertools.repeat('?'),
                                           len(activity_types))))
        sql = (
            'SELECT {0} FROM file_log {1}'
            'ORDER BY recorded DESC '
            'LIMIT ?'
        ).format(columns, where)
        return sql

    @staticmethod
    def _params_list_file_path(limit, activity_types, unique):
        if activity_types is None:
            activity_types = []
        return activity_types + [limit]

    def list_file_path(self, limit, activity_types=None, unique=True):
        """
        Return an iterator which yields file paths.

        :type          limit: int
        :arg           limit: maximum number of files to list
        :type activity_types: tuple
        :arg  activity_types: subset of :attr:`ACTIVITY_TYPES`
        :type         unique: bool
        :arg          unique: if true (default), strip off duplications

        """
        args = (limit, activity_types, unique)
        with closing(self._get_db()) as db:
            cursor = db.execute(
                self._script_list_file_path(*args),
                self._params_list_file_path(*args))
            for (file_path,) in cursor:
                yield file_path
