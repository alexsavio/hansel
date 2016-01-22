=========
Changelog
=========


Version 0.4.0
==============

- Fill CHANGES.rst
- All outputs from `Crumb.ls` function will be sorted.
- Add regular expressions or `fnmatch` option for crumb arguments.
- Change `exists` behaviour. Now the empty crumb arguments will return False when `exist()`.
- Code clean up.
- Fix bugs


Version 0.3.1
==============

- Fix README
- Code clean up.


Version 0.3.0
==============

- Add `_argval` member, a dict which stores crumb arguments replacements.
- Add tests.
- Remove `rm_dups` option in `Crumb.ls` function.
- Remove conversion to `Paths` when `Crumb` has no crumb arguments in `Crumb.ls`.


Version 0.2.0
==============

- Add `ignore_list` parameter in `Crumb` constructor.


Version 0.1.1
==============

- Add `Crumb.unfold` function.
- Move `mktree` out of `Crumb` class.


Version 0.1.0
==============

- Simplify code.
- Increase test coverage.
- Add `exist_check` to `Crumb.ls` function.
- Fix bugs.