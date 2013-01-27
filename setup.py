from distutils.core import setup

import factlog

setup(
    name='factlog',
    version=factlog.__version__,
    packages=['factlog', 'factlog.utils', 'factlog.tests'],
    author=factlog.__author__,
    author_email='aka.tkf@gmail.com',
    url='https://github.com/tkf/factlog',
    license=factlog.__license__,
    description='factlog - File ACTivity LOGger',
    long_description=factlog.__doc__,
    keywords='history, recently used files',
    classifiers=[
        "Development Status :: 3 - Alpha",
        # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    install_requires=[
        'argparse',
    ],
)
