

Changelog
=========

Version 0.8.0 - 
---------------
- Set to True the default value for `check_exists` in `Crumb.ls` function. 
  I don't think anybody is interested in non-existing paths.

- Now it is possible to set a non-open item in a Crumb, i.e., I can replace the value for an already set crumb argument.

- Update README.rst

- Code clean-up.

- Replace dict to OrderedDict output in `valuesmap_to_dict` function.

- Add regex option within `arg_name` argument of `ls` and `__get_item__`.


Version 0.7.0 - 0.7.5
---------------------
- Refactoring of how Crumb works, now using string.Formatter.
  This will help with new features due to simpler logic.Now it is not possible to change the syntax of the Crumbs,
  although I guess nobody is interested in that.
- Fixed a few bugs from previous versions.
- Now `copy` function is not a classmethod anymore, so you can do `crumb.copy()` as well as `Crumb.copy(crumb)`.
- `patterns` is not a dictionary anymore, the regexes are embedded in the `_path` string.
  The property `patterns` returns the dictionary as before.  The function `set_pattern` must be used instead to set a different pattern to a given argument.

- Update README.rst

- Fix README.rst because of bad syntax for PyPI.

- Fix bug for Python 2.7

- Fix the bug in .rst for PyPI.

- Code cleanup


Version 0.6.0 - 0.6.2
---------------------
- Added `intersection` function in `utils.py`.
- Change of behaviour in `__getitem__`, now it returns a list of values even if is only the one replace string from `_argval`.
- General renaming of the private functions inside Crumbs, more in accordance to the `open_args`/`all_args` idea.
- Fixed a few bugs and now the generated crumbs from `unfold` and `ls` will have the same parameters as the original Crumb.

- Change the behaviour or `intersection` with `len(arg_names) == 1` for compatibility with `crumb.build_path` function.
- Improve README, update with new examples using `intersection`.

- Add `pandas` helper functions.
- Add `utils` to convert from values_maps to dicts.
- Improve docstrings.


Version 0.5.0 - 0.5.5
---------------------
- Add Python 2.7 compatibility. Friends don't let friends use Python 2.7!
- Add 're.ignorecase' option for the `regex` argument in the constructor.

- Add `utils.check_path` function.
- Fix `Crumb.split` function to return the not defined part of the crumb.

- Add `Crumbs.keys()` function.
- Rename `utils.remove_duplicates()` to `utils.rm_dups()`.

- Deprecating `Crumbs.keys()` function.
- Renamed `Crumbs.keys()` to `Crumbs.open_args()` and added `Crumbs.all_args()`.
- Substitute the internal logic of Crumbs to work with `Crumbs.open_args()`, made it a bit faster.

- Added CHANGES.rst to MANIFEST.in


Version 0.4.0 - 0.4.2
---------------------
- Fill CHANGES.rst.

- All outputs from `Crumb.ls` function will be sorted.
- Add regular expressions or `fnmatch` option for crumb arguments.
- Change `exists` behaviour. Now the empty crumb arguments will return False when `exist()`.

- Code clean up.
- Fix bugs.

- Fix CHANGES.rst to correct restview in PyPI.
- Thanks to restview: https://pypi.python.org/pypi/restview.
  Use: ``restview --long-description``
- Improve documentation in README.
- Rename member `_argreg` to `patterns`, so the user can use it to manage the argument patterns.


Version 0.3.0 - 0.3.1
---------------------
- Add `_argval` member, a dict which stores crumb arguments replacements.
- Add tests.
- Remove `rm_dups` option in `Crumb.ls` function.
- Remove conversion to `Paths` when `Crumb` has no crumb arguments in `Crumb.ls`.

- Fix README.
- Code clean up.


Version 0.2.0
-------------
- Add `ignore_list` parameter in `Crumb` constructor.


Version 0.1.0 - 0.1.1
---------------------
- Simplify code.
- Increase test coverage.
- Add `exist_check` to `Crumb.ls` function.

- Fix bugs.
- Add `Crumb.unfold` function.
- Move `mktree` out of `Crumb` class.

