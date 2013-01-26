import os
import sqlite3
import functools
from contextlib import closing

from .utils.iterutils import repeat, uniq
from .utils.strutils import remove_prefix, get_lines_at_point


def concat_expr(operator, conditions):
    """
    Concatenate `conditions` with `operator` and wrap it by ().

    It returns a string in a list or empty list, if `conditions` is empty.

    """
    expr = " {0} ".format(operator).join(conditions)
    return ["({0})".format(expr)] if expr else []


class AccessInfo(object):

    """
    Access information object.
    """

    __slots__ = ['path', 'point', 'recorded', 'type', 'showpath']

    def __init__(self, path, point, recorded, type):
        self.path = self.showpath = path
        self.point = point
        self.recorded = recorded
        self.type = type

    def _set_relative_path(self, absunder):
        """
        Set :attr:`showpath` and return the newly set value.

        :attr:`showpath` is set the relative path of :attr:`path` from
        one of the path in `absunder`.

        """
        self.showpath = remove_prefix(absunder, self.path)
        return self.showpath

    def _get_lines_at_point(self, pre_lines, post_lines):
        with open(self.path) as f:
            return get_lines_at_point(
                f.read(), self.point, pre_lines, post_lines)

    def write_paths_and_lines(self, file, pre_lines=0, post_lines=0,
                              newline='\n', separator=':'):
        """
        Write :attr:`showpath` and lines around :attr:`point` to `file`.
        """
        for (lineno, line) in self._get_lines_at_point(pre_lines, post_lines):
            file.write(self.showpath)
            file.write(separator)
            file.write(str(lineno))
            file.write(separator)
            file.write(line)
            file.write(newline)


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
    def _script_search_file_log(
            limit, activity_types, unique, include_glob, exclude_glob):
        # FIXME: support `unique` (currently ignored)
        params = []
        conditions = []
        if activity_types is not None:
            conditions.append('activity_type in ({0})'.format(
                ', '.join(repeat('?', len(activity_types)))))
            params.extend(activity_types)

        conditions.extend(concat_expr(
            'OR', repeat('glob(?, file_path)', len(include_glob))))
        conditions.extend(repeat('NOT glob(?, file_path)', len(exclude_glob)))
        params.extend(include_glob)
        params.extend(exclude_glob)

        if conditions:
            where = 'WHERE {0} '.format(" AND ".join(conditions))
        else:
            where = ''
        if unique:
            columns = 'file_path, file_point, MAX(recorded), activity_type'
            group_by = 'GROUP BY file_path '
        else:
            columns = 'file_path, file_point, recorded, activity_type'
            group_by = ''
        sql = (
            'SELECT {0} FROM file_log {1}{2}'
            'ORDER BY recorded DESC '
            'LIMIT ?'
        ).format(columns, where, group_by)
        params.append(limit)
        return (sql, params)

    def __wrap_search_file_log_defaults(func):
        """
        Set default arguments for :meth:`search_file_log`.
        """
        @functools.wraps(func)
        def wrapper(self, limit, activity_types=None, unique=True,
                    include_glob=[], exclude_glob=[],
                    under=[], relative=False):
            return func(
                self, limit, activity_types, unique,
                include_glob, exclude_glob, under, relative)
        return wrapper

    def __wrap_search_file_log_for_under(func):
        """
        Implement `under` and `relative` part for :meth:`search_file_log`.
        """
        @functools.wraps(func)
        def wrapper(self, limit, activity_types, unique,
                    include_glob, exclude_glob, under, relative):
            absunder = [os.path.join(os.path.abspath(p), "") for p in under]
            include_glob += [os.path.join(p, "*") for p in absunder]
            iter_info = func(
                self, limit, activity_types, unique,
                include_glob, exclude_glob)
            if relative:
                return uniq(
                    iter_info,
                    lambda i: i._set_relative_path(absunder))
            else:
                return iter_info
        return wrapper

    @__wrap_search_file_log_defaults
    @__wrap_search_file_log_for_under
    def search_file_log(
            self, limit, activity_types, unique, include_glob, exclude_glob):
        """
        Return an iterator which yields file access information.

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

        :type          under: list of str
        :arg           under: paths given by --under
        :type       relative: bool
        :arg        relative:

        :rtype: list of AccessInfo

        """
        with closing(self._get_db()) as db:
            cursor = db.execute(*self._script_search_file_log(
                limit, activity_types, unique, include_glob, exclude_glob))
            for row in cursor:
                yield AccessInfo(*row)
