import os
import itertools
import sqlite3
from contextlib import closing


def repeat(item, num):
    return itertools.islice(itertools.repeat(item), num)


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
    def _script_list_file_path(
            limit, activity_types, unique, include_glob, exclude_glob):
        # FIXME: support `unique` (currently ignored)
        params = []
        columns = 'file_path'
        conditions = []
        if unique:
            # FIXME: make sure that the selected row is the most recent one
            columns = 'DISTINCT ' + columns
        if activity_types is not None:
            conditions.append('activity_type in ({0}) '.format(
                ', '.join(repeat('?', len(activity_types)))))
            params.extend(activity_types)

        conditions.extend(repeat('glob(?, file_path)', len(include_glob)))
        conditions.extend(repeat('NOT glob(?, file_path)', len(exclude_glob)))
        params.extend(include_glob)
        params.extend(exclude_glob)

        if conditions:
            where = ' WHERE {0}'.format(" AND ".join(conditions))
        else:
            where = ''
        sql = (
            'SELECT {0} FROM file_log {1}'
            'ORDER BY recorded DESC '
            'LIMIT ?'
        ).format(columns, where)
        params.append(limit)
        return (sql, params)

    def list_file_path(
            self, limit, activity_types=None, unique=True,
            include_glob=[], exclude_glob=[]):
        """
        Return an iterator which yields file paths.

        :type          limit: int
        :arg           limit: maximum number of files to list
        :type activity_types: tuple
        :arg  activity_types: subset of :attr:`ACTIVITY_TYPES`
        :type         unique: bool
        :arg          unique: if true (default), strip off duplications
        :type   include_glob: list
        :arg    include_glob: a list of glob expression
        :type   exclude_glob: list
        :arg    exclude_glob: a list of glob expression

        """
        with closing(self._get_db()) as db:
            cursor = db.execute(*self._script_list_file_path(
                limit, activity_types, unique, include_glob, exclude_glob))
            for (file_path,) in cursor:
                yield file_path
