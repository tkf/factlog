def record_add_arguments(parser):
    parser.add_argument(
        'file')


def record_run():
    """
    Record activities on file.
    """
    pass


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
