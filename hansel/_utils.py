# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Crumb manipulation utilities
"""
import os
from string import Formatter
from typing import Iterable, Tuple, Dict, Iterator

_txt_idx = 0
_fld_idx = 1
_rgx_idx = 2
_cnv_idx = 3


def _yield_items(crumb_path: str, index=None) -> Iterator[str]:
    """ An iterator over the items in `crumb_path` given by string.Formatter."""
    if index is None:
        return Formatter().parse(crumb_path)

    # for (literal_text, field_name, format_spec, conversion) in fmt.parse(crumb_path):
    # (txt, fld, fmt, conv)
    return (items[index] for items in Formatter().parse(crumb_path) if items[index] is not None)


def _enum_items(crumb_path: str) -> Iterator[Tuple[int, str]]:
    """ An iterator over the enumerated items, i.e., (index, items) in
    `crumb_path` given by string.Formatter. """
    yield from enumerate(Formatter().parse(crumb_path))


def _depth_items(crumb_path: str, index: int = None) -> Iterator[Tuple[int, str]]:
    """ Return a generator with  (depth, items) in `crumb_path`. Being `depth`
     the place in the file path each argument is."""
    if index is None:
        index = slice(_txt_idx, _cnv_idx + 1)

    depth = 0
    for idx, items in _enum_items(crumb_path):
        if items[_fld_idx]:
            depth += items[_txt_idx].count(os.path.sep)
            yield depth, items[index]


def _arg_names(crumb_path: str) -> Iterator[str]:
    """ Return an iterator over arg_name in crumb_path."""
    yield from _yield_items(crumb_path, _fld_idx)


def _depth_names(crumb_path: str) -> Iterator[Tuple[int, str]]:
    """ Return an iterator over (depth, arg_name)."""
    yield from _depth_items(crumb_path, _fld_idx)


def _depth_names_regexes(crumb_path: str) -> Iterator[Tuple[int, str]]:
    """ Return an iterator over (depth, (arg_name, arg_regex))."""
    yield from _depth_items(crumb_path, slice(_fld_idx, _cnv_idx))


def _build_path(
    crumb_path: str,
    arg_values: Dict[str, str],
    with_regex: bool=True,
    regexes: Dict[str, str]=None
) -> str:
    """ Build the crumb_path with the values in arg_values.
    Parameters
    ----------
    crumb_path:

    arg_values:
        arg_name -> arg_value

    with_regex:

    regexes:
        dict[arg_name] -> regex
        The regexes contained here will replace or be added as a regex for
        the corresponding arg_name.

    Returns
    -------
    built_path:
    """
    if regexes is None:
        regexes = {}

    path = ''
    for txt, fld, rgx, conv in _yield_items(crumb_path):
        path += txt
        if fld is None:
            continue

        if fld in arg_values:
            path += arg_values[fld]
        else:
            regex = regexes.get(fld, rgx) if with_regex else ''
            path += _format_arg(fld, regex=regex)

    return path


def is_valid(crumb_path: str) -> bool:
    """ Return True if `crumb_path` is a valid Crumb value, False otherwise. """
    try:
        list(_depth_names_regexes(crumb_path))
    except ValueError:
        return False
    else:
        return True


def _first_txt(crumb_path: str) -> str:
    """ Return the first text part without arguments in `crumb_path`. """
    for txt in _yield_items(crumb_path, index=_txt_idx):
        return txt


def _find_arg_depth(crumb_path: str, arg_name: str) -> Tuple[int, str, str]:
    """ Return the depth, name and regex of the argument with name `arg_name`.
    """
    for depth, (txt, fld, rgx, conv) in _depth_items(crumb_path):
        if fld == arg_name:
            return depth, fld, rgx


def _has_arg(crumb_path: str, arg_name: str) -> bool:
    """ Return the True if the `arg_name` is found in `crumb_path`. """
    for txt, fld, rgx, conv in _yield_items(crumb_path):
        if fld == arg_name:
            return True
    return False


def _check(crumb_path: str) -> str:
    """ Raises some Errors if there is something wrong with `crumb_path`, if
    not the type needed or is not valid.
    Parameters
    ----------
    crumb_path: str

    Raises
    ------
     - ValueError if the path of the Crumb has errors using `self.is_valid`.
     - TypeError if the crumb_path is not a str or a Crumb.
    """
    if not isinstance(crumb_path, str):
        raise TypeError("Expected `crumb_path` to be a {}, "
                        "got {}.".format(str, type(crumb_path)))

    if not is_valid(crumb_path):
        raise ValueError("The current crumb path has errors, "
                         "got {}.".format(crumb_path))

    return crumb_path


def _get_path(crumb_path: str) -> str:
    """ Return the path string from `crumb_path`.
    Parameters
    ----------
    crumb_path: str or Crumb

    Returns
    -------
    path: str
    """
    if hasattr(crumb_path, '_path'):
        crumb_path = crumb_path._path

    if not isinstance(crumb_path, str):
        raise TypeError(
            "Expected `crumb_path` to be a string, got {}.".format(type(crumb_path))
        )

    return crumb_path


def _is_crumb_arg(crumb_arg: str) -> bool:
    """ Return True if `crumb_arg` is a well formed crumb argument, i.e.,
    is a string that starts with `start_sym` and ends with `end_sym`.
    False otherwise.
    """
    if not isinstance(crumb_arg, str):
        return False
    start_sym, end_sym = ('{', '}')
    return crumb_arg.startswith(start_sym) and crumb_arg.endswith(end_sym)


def _format_arg(arg_name: str, regex: str='') -> str:
    """ Return the crumb argument for its string `format()` representation. """
    start_sym, end_sym = ('{', '}')
    reg_sym = ':'

    arg_fmt = start_sym + arg_name
    if regex:
        arg_fmt += reg_sym + regex
    arg_fmt += end_sym

    return arg_fmt


def has_crumbs(crumb_path: str) -> bool:
    """ Return True if the `crumb_path.split(os.path.sep)` has item which is a
    crumb argument that starts with '{' and ends with '}'."""
    crumb_path = _get_path(crumb_path)

    splt = crumb_path.split(os.path.sep)
    for i in splt:
        if _is_crumb_arg(i):
            return True

    return False


def _split(crumb_path: str) -> Tuple[str, str]:
    """ Split `crumb_path` in two parts, the first is the base folder without
        any crumb argument and the second is the rest of `crumb_path` beginning
        with the first crumb argument.
        If `crumb_path` starts with an argument, will return ('', crumb_path).
    """
    crumb_path = _get_path(crumb_path)

    if not has_crumbs(crumb_path):
        return crumb_path, ''

    if not is_valid(crumb_path):
        raise ValueError('Crumb path {} is not valid.'.format(crumb_path))

    start_sym = '{'
    if crumb_path.startswith(start_sym):
        base = ''
        rest = crumb_path
    else:
        idx = crumb_path.find(start_sym)
        base = crumb_path[0:idx]
        if base.endswith(os.path.sep):
            base = base[:-1]

        rest = crumb_path[idx:]

    return base, rest


def _touch(crumb_path: str, exist_ok: bool=True) -> str:
    """ Create a leaf directory and all intermediate ones
    using the non crumbed part of `crumb_path`.
    If the target directory already exists, raise an IOError
    if exist_ok is False. Otherwise no exception is raised.
    Parameters
    ----------
    crumb_path:

    exist_ok:
        Default = True

    Returns
    -------
    nupath:
        The new path created.
    """
    if has_crumbs(crumb_path):
        nupath = _split(crumb_path)[0]
    else:
        nupath = crumb_path

    os.makedirs(nupath, exist_ok=exist_ok)
    return nupath


def _split_exists(crumb_path: str) -> bool:
    """ Return True if the part without crumb arguments of `crumb_path`
    is an existing path or a symlink, False otherwise.
    """
    if has_crumbs(crumb_path):
        rpath = _split(crumb_path)[0]
    else:
        rpath = str(crumb_path)

    return os.path.exists(rpath) or os.path.islink(rpath)


def _check_is_subset(list1: Iterable[str], list2: Iterable[str]):
    """ Raise an error if `list1` is not a subset of `list2`."""
    if not set(list1).issubset(set(list2)):
        raise KeyError(
            'The `list1` argument should be a subset of `list2` '
            'got {} and {}.'.format(list1, list2)
        )
