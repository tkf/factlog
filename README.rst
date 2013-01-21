factlog - File ACTivity LOGger
==============================

Log your activity on files and use it for searching.


Rich command line interface.  Useful for unix style searching::

   factlog list | xargs grep 'def record'


"I want to see some Python files I edited recently"::

  factlog list --include-glob '*.py'


**WORK IN PROGRESS**
"I want to list files in this particular project I touched.  I don't
care about in which branch I opened the file."::

  factlog list --under BRANCH-A --under BRANCH-B --relative


**WORK IN PROGRESS**
"I want to see last 50 notes I took with title"::

  factlog list --under MY-NOTE-DIRECTORY --relative --title --limit 50


**WORK IN PROGRESS**
"The files I touched are huge.  I want to search only the locations
I touched."::

   factlog list -C 50 | grep 'def record'


More to come
------------

- Record line at the time of writing the file.
- Ranking based on many data points: how many times you
  write to the file, how recent you visited the file, etc.
- Understand "project" (VCS repository).
- Concurrent grep.
- Extract URLs in the documents and use them as URL bookmark.
