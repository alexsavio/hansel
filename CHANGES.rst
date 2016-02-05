

Changelog
=========

Version 0.5.4
-------------
- Deprecating `Crumbs.keys()` function.
- Renamed `Crumbs.keys()` to `Crumbs.open_args()` and added `Crumbs.all_args()`.
- Substitute the internal logic of Crumbs to work with `Crumbs.open_args()`, made it a bit faster.


Version 0.5.3
-------------
- Add `Crumbs.keys()` function.
- Rename `utils.remove_duplicates()` to `utils.rm_dups()`.


Version 0.5.2
-------------
- Add `utils.check_path` function.
- Fix `Crumb.split` function to return the not defined part of the crumb.


Version 0.5.1
-------------
- Add 're.ignorecase' option for the `regex` argument in the constructor.


Version 0.5.0
-------------
- Add Python 2.7 compatibility. Friends don't let friends use Python 2.7!


Version 0.4.2
-------------
- Improve documentation in README.
- Rename member `_argreg` to `patterns`, so the user can use it to manage the argument patterns.


Version 0.4.1
-------------

- Fix CHANGES.rst to correct restview in PyPI.
- Thanks to restview: https://pypi.python.org/pypi/restview.


Version 0.4.0
-------------

- Fill CHANGES.rst.
- All outputs from `Crumb.ls` function will be sorted.
- Add regular expressions or `fnmatch` option for crumb arguments.
- Change `exists` behaviour. Now the empty crumb arguments will return False when `exist()`.
- Code clean up.
- Fix bugs.


Version 0.3.1
-------------

- Fix README.
- Code clean up.


Version 0.3.0
-------------

- Add `_argval` member, a dict which stores crumb arguments replacements.
- Add tests.
- Remove `rm_dups` option in `Crumb.ls` function.
- Remove conversion to `Paths` when `Crumb` has no crumb arguments in `Crumb.ls`.


Version 0.2.0
-------------

- Add `ignore_list` parameter in `Crumb` constructor.


Version 0.1.1
-------------

- Add `Crumb.unfold` function.
- Move `mktree` out of `Crumb` class.


Version 0.1.0
-------------

- Simplify code.
- Increase test coverage.
- Add `exist_check` to `Crumb.ls` function.
- Fix bugs.
