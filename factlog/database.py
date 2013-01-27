import os
import sqlite3
import functools
from contextlib import closing

from .utils.iterutils import repeat, uniq
from .accessinfo import AccessInfo

schema_version = '0.1.dev1'


def concat_expr(operator, conditions):
    """
    Concatenate `conditions` with `operator` and wrap it by ().

    It returns a string in a list or empty list, if `conditions` is empty.

    """
    expr = " {0} ".format(operator).join(conditions)
    return ["({0})".format(expr)] if expr else []


class DataBase(object):

    ACCESS_TYPES = ('write', 'open', 'close')
    access_type_to_int = dict((a, i) for (i, a) in enumerate(ACCESS_TYPES))
    int_to_access_type = dict(enumerate(ACCESS_TYPES))

    schemapath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'schema.sql')

    def __init__(self, dbpath):
        self.dbpath = dbpath
        if not os.path.exists(dbpath):
            self._init_db()

    def _get_db(self):
        """Returns a new connection to the database."""
        return closing(sqlite3.connect(self.dbpath))

    def _init_db(self):
        """Creates the database tables."""
        from .__init__ import __version__ as version
        with self._get_db() as db:
            with open(self.schemapath) as f:
                db.cursor().executescript(f.read())
            db.execute(
                'INSERT INTO factlog_info (factlog_version, schema_version) '
                'VALUES (?, ?)',
                [version, schema_version])
            db.commit()

    def record_file_log(self, file_path, access_type, file_point=None,
                        file_exists=None, program=None):
        """
        Record file activity.

        :type     file_path: str
        :arg      file_path: path to the file
        :type    file_point: int or None
        :arg     file_point: point of cursor at the time of saving.
        :type   file_exists: bool or None
        :arg    file_exists: True if the file exists.  If None (default),
                             call `os.path.exists` to automatically record.
        :type   access_type: str
        :arg    access_type: one of 'write', 'open', 'close'

        `file_path` is converted to absolute path before saving
        to the database.

        """
        # FIXME: Add more activities (if possible):
        #        create/delete/move/copy
        access_type = self.access_type_to_int[access_type]
        file_path = os.path.abspath(file_path)
        if file_exists is None:
            file_exists = os.path.exists(file_path)
        with self._get_db() as db:
            db.execute(
                """
                INSERT INTO access_log
                    (file_path, file_point, file_exists, access_type, program)
                VALUES (?, ?, ?, ?, ?)
                """,
                [file_path, file_point, file_exists, access_type, program])
            db.commit()

    @classmethod
    def _script_search_file_log(
            cls, limit, access_types, unique, include_glob, exclude_glob,
            exists):
        # FIXME: support `unique` (currently ignored)
        params = []
        conditions = []
        if access_types is not None:
            conditions.append('access_type in ({0})'.format(
                ', '.join(repeat('?', len(access_types)))))
            params.extend(map(cls.access_type_to_int.get, access_types))

        if exists is not None:
            conditions.append('file_exists = ?')
            params.append(exists)

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
            columns = 'file_path, file_point, MAX(recorded), access_type'
            group_by = 'GROUP BY file_path '
        else:
            columns = 'file_path, file_point, recorded, access_type'
            group_by = ''
        sql = (
            'SELECT {0} FROM access_log {1}{2}'
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
        def wrapper(self, limit, access_types=None, unique=True,
                    include_glob=[], exclude_glob=[], exists=None,
                    under=[], relative=False,
                    only_existing=True):
            return func(
                self, limit, access_types, unique,
                include_glob, exclude_glob, exists,
                under, relative,
                only_existing=only_existing)
        return wrapper

    def __wrap_search_file_log_exclude_non_existing_path(func):
        """
        Filter out rows for non-existing path.
        """
        @functools.wraps(func)
        def wrapper(self, *args, **kwds):
            only_existing = kwds.pop('only_existing')
            iter_info = func(self, *args, **kwds)
            if only_existing:
                return (i for i in iter_info if os.path.exists(i.path))
            else:
                return iter_info
        return wrapper

    def __wrap_search_file_log_for_under(func):
        """
        Implement `under` and `relative` part for :meth:`search_file_log`.
        """
        @functools.wraps(func)
        def wrapper(self, limit, access_types, unique,
                    include_glob, exclude_glob, exists,
                    under, relative):
            absunder = [os.path.join(os.path.abspath(p), "") for p in under]
            include_glob = include_glob + \
                           [os.path.join(p, "*") for p in absunder]
            iter_info = func(
                self, limit, access_types, unique,
                include_glob, exclude_glob, exists)
            if relative:
                return uniq(
                    iter_info,
                    lambda i: i._set_relative_path(absunder))
            else:
                return iter_info
        return wrapper

    @__wrap_search_file_log_defaults
    @__wrap_search_file_log_exclude_non_existing_path
    @__wrap_search_file_log_for_under
    def search_file_log(
            self, limit, access_types, unique, include_glob, exclude_glob,
            exists):
        """
        Return an iterator which yields file access information.

        :type          limit: int
        :arg           limit: maximum number of files to list
        :type   access_types: tuple
        :arg    access_types: subset of :attr:`ACCESS_TYPES`
        :type         unique: bool
        :arg          unique: if true (default), strip off duplications
        :type   include_glob: list
        :arg    include_glob: a list of glob expression
        :type   exclude_glob: list
        :arg    exclude_glob: a list of glob expression
        :type         exists: bool or None
        :arg          exists: whether the file exists at *recording* time

        :type          under: list of str
        :arg           under: paths given by --under
        :type       relative: bool
        :arg        relative:
        :type  only_existing: bool
        :arg   only_existing: if true (default), exclude non-existing paths

        :rtype: list of AccessInfo

        """
        i2at = self.int_to_access_type
        with self._get_db() as db:
            cursor = db.execute(*self._script_search_file_log(
                limit, access_types, unique, include_glob, exclude_glob,
                exists))
            for (path, point, recorded, atype) in cursor:
                yield AccessInfo(path, point, recorded, i2at[atype])
