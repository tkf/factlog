# [[[cog import cog; cog.outl('"""\n%s\n"""' % file('../README.rst').read())]]]
"""
factlog - File ACTivity LOGger
==============================


.. sidebar:: Links:

   * `Repository <https://github.com/tkf/factlog>`_ (at GitHub)
   * `Issue tracker <https://github.com/tkf/factlog/issues>`_ (at GitHub)
   * `PyPI <http://pypi.python.org/pypi/factlog>`_
   * `Travis CI <https://travis-ci.org/#!/tkf/factlog>`_ |build-status|


Factlog logs your activity on files and uses it for searching.


Rich command line interface.  Useful for unix style searching::

  factlog list | xargs grep 'def record'


"I want to see some Python files I edited recently"::

  factlog list --include-glob '*.py'


"I want to list files in this particular project I touched.  I don't
care about in which branch I opened the file."::

  factlog list --under BRANCH-A --under BRANCH-B --relative


"I want to see last 50 notes I took with title"::

  factlog list --under MY-NOTE-DIRECTORY --relative --title --limit 50


"The files I touched are huge.  I want to search only the locations
I touched."::

  factlog list -C 50 | grep 'def record'


Editor plugin
-------------

Factlog currently only have Emacs integration.  If you make a plugin
for other editors, please let me know.  See `interfaces for plugin`_
for more information.

Emacs
^^^^^

Factlog has Emacs plugin.
You can get `factlog.el` from factlog repository_.

Command line programs
^^^^^^^^^^^^^^^^^^^^^

Factlog is easy to integrate with command line programs such as
``less`` and ``vim``.  See ``shell/config.sh`` for sample setup.
You can use ``shell/config.sh`` like this::

   source PATH/TO/factlog/shell/config.sh
   alias less="factlog-record-wrapper \\less"
   alias vim="factlog-record-wrapper \\vim"


Interfaces for plugin
---------------------

Command line interface
^^^^^^^^^^^^^^^^^^^^^^

If your editor can run a command line program, it is possible to
write a factlog plugin!  See ``factlog record --help``.

RPC interface
^^^^^^^^^^^^^

Work in progress...

Python interface
^^^^^^^^^^^^^^^^

Work in progress...


More to come / ideas
--------------------

- Ranking based on many data points: how many times you
  write to the file, how recent you visited the file, etc.
- Understand "project" (VCS repository).
- Concurrent grep.
- Extract URLs in the documents and use them as URL bookmark.


..
   License
   -------

   Factlog is licensed under GPL v3.
   See COPYING for details.


.. Travis CI build status badge
.. |build-status|
   image:: https://secure.travis-ci.org/tkf/factlog.png?branch=master
   :target: http://travis-ci.org/tkf/factlog
   :alt: Build Status

"""
# [[[end]]]

__version__ = '0.0.1.dev0'
__author__ = 'Takafumi Arakaki'
__license__ = "MIT License"
