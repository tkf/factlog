"""
Command line interface.
"""

import argparse
import textwrap


class Formatter(argparse.RawTextHelpFormatter,
                argparse.RawDescriptionHelpFormatter,
                argparse.ArgumentDefaultsHelpFormatter):
    pass


def get_parser(commands):
    """
    Generate argument parser given a list of subcommand specifications.

    :type commands: list of (str, function, function)
    :arg  commands:
        Each element must be a tuple ``(name, adder, runner)``.

        :param   name: subcommand
        :param  adder: a function takes one object which is an instance
                       of :class:`argparse.ArgumentParser` and add
                       arguments to it
        :param runner: a function takes keyword arguments which must be
                       specified by the arguments parsed by the parser
                       defined by `adder`.  Docstring of this function
                       will be the description of the subcommand.

    """
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers()

    for (name, adder, runner) in commands:
        subp = subparsers.add_parser(
            name,
            formatter_class=Formatter,
            description=runner.__doc__ and textwrap.dedent(runner.__doc__))
        adder(subp)
        subp.set_defaults(func=runner)

    return parser


def main(args=None):
    # cli.py can be executed as a script (python factlog/cli.py).
    # In that case, relative import cannot be used:
    from factlog import record
    # from notman import search
    parser = get_parser(
        record.commands
        # + search.commands
    )
    ns = parser.parse_args(args=args)
    applyargs = lambda func, **kwds: func(**kwds)
    applyargs(**vars(ns))


if __name__ == '__main__':
    main()
