import os
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
                'insert into system_info (version) values (?)',
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
        assert activity_type in self.ACTIVITY_TYPES
        file_path = os.path.abspath(file_path)
        with closing(self._get_db()) as db:
            db.execute(
                """
                insert into file_log (file_path, file_point, activity_type)
                values (?, ?, ?)
                """,
                [file_path, file_point, activity_type])
            db.commit()
