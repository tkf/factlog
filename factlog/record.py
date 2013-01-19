from .config import ConfigStore
from .database import DataBase


def get_db(*args, **kwds):
    config = ConfigStore(*args, **kwds)
    return DataBase(config.db_path)


def record_add_arguments(parser):
    parser.add_argument('file_path')
    parser.add_argument('--activity-type', default='write',
                        choices=DataBase.ACTIVITY_TYPES)
    parser.add_argument('--file-point', type=int)


def record_run(file_path, file_point, activity_type):
    """
    Record activities on file.
    """
    db = get_db()
    db.record_file_log(file_path, file_point, activity_type)


def list_add_arguments(parser):
    parser.add_argument('--limit')


def list_run(limit):
    """
    List recently accessed files.
    """
    pass


commands = [
    ('record', record_add_arguments, record_run),
    ('list', list_add_arguments, list_run),
]
