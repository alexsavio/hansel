# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Crumb manipulation utilities
"""
import functools
import os
import os.path as op
import warnings
from string import Formatter

from   six import string_types


def _replace_fmt(crumb_path):
    fmt = Formatter()
    for (literal_text, field_name, format_spec, conversion) in fmt.parse(crumb_path):
        pass


def _dict_popitems(adict, **kwargs):
    if not adict:
        return

    if not kwargs:
        return

    _ = [adict.pop(k) for k in kwargs if k in adict]


def _get_path(crumb_path):
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

    if not isinstance(crumb_path, string_types):
        raise TypeError("Expected `crumb_path` to be a {}, got {}.".format(string_types, type(crumb_path)))

    return crumb_path


def _is_crumb_arg(crumb_arg, start_end_syms=('{', '}')):
    """ Returns True if `crumb_arg` is a well formed crumb argument, i.e.,
    is a string that starts with `start_sym` and ends with `end_sym`. False otherwise."""
    if not isinstance(crumb_arg, string_types):
        return False

    start_sym, end_sym = start_end_syms
    return crumb_arg.startswith(start_sym) and crumb_arg.endswith(end_sym)


def _arg_params(arg, start_end_syms=('{', '}'), reg_sym=':'):
    """ Return the name and the regex of the argument given its crumb representation.
    Parameters
    ----------
    arg_crumb: str

    start_end_syms: 2-tuple of str
        The strings that indicate the start and end of a crumb argument

    reg_sym: str
        The string that separate the crumb argument name from the
        crumb argument regular expression.

    Returns
    -------
    arg_name: str

    arg_regex: str
    """
    arg_content = _arg_content(arg, start_end_syms=start_end_syms)

    if reg_sym in arg_content:
        return tuple(arg_content.split(reg_sym))
    else:
        return arg_content, None


def _arg_name(arg, start_end_syms=('{', '}'), reg_sym=':'):
    """ Return the name of the argument given its crumb representation.
    Parameters
    ----------
    arg_crumb: str

    start_end_syms: 2-tuple of str
        The strings that indicate the start and end of a crumb argument

    reg_sym: str
        The string that separate the crumb argument name from the
        crumb argument regular expression.

    Returns
    -------
    arg_name: str
    """
    arg_content = _arg_content(arg, start_end_syms=start_end_syms)

    if reg_sym in arg_content:
        return arg_content.split(reg_sym)[0]
    else:
        return arg_content


def _arg_regex(arg, start_end_syms=('{', '}'), reg_sym=':'):
    """ Return the name of the argument given its crumb representation.
    Parameters
    ----------
    arg_crumb: str

    start_end_syms: 2-tuple of str
        The strings that indicate the start and end of a crumb argument

    reg_sym: str
        The string that separate the crumb argument name from the
        crumb argument regular expression.

    Returns
    -------
    arg_name: str
    """
    arg_content = _arg_content(arg, start_end_syms=start_end_syms)

    if reg_sym in arg_content:
        return arg_content.split(reg_sym)[1]
    else:
        return None


def _arg_content(arg, start_end_syms=('{', '}')):
    """ Return the name of the argument given its crumb representation.
    Parameters
    ----------
    arg_crumb: str

    start_end_syms: 2-tuple of str
        The strings that indicate the start and end of a crumb argument

    Returns
    -------
    arg_name: str
    """
    if not _is_crumb_arg(arg):
        raise ValueError("Expected an well formed crumb argument, "
                         "got {}.".format(arg))

    start_sym, end_sym = start_end_syms
    return arg[len(start_sym):-len(end_sym)]


def _arg_format(arg_name, start_end_syms=('{', '}'), reg_sym=':', regex=None):
    """ Return the crumb argument for its string `format()` representation.
    Parameters
    ----------
    arg_name: str

    Returns
    -------
    arg_format: str
    """
    start_sym, end_sym = start_end_syms

    arg_fmt = start_sym + arg_name
    if regex is not None:
        arg_fmt += reg_sym + regex
    arg_fmt += end_sym

    return arg_fmt


def is_valid(crumb_path, start_end_syms=('{', '}')):
    """ Return True if `crumb_path` is a well formed path with crumb arguments,
    False otherwise.
    Parameters
    ----------
    crumb_path: str

    Returns
    -------
    is_valid: bool
    """
    crumb_path = _get_path(crumb_path)

    start_sym, end_sym = start_end_syms

    splt = crumb_path.split(op.sep)
    for crumb in splt:
        if op.isdir(crumb):
            continue

        if _is_crumb_arg(crumb, start_end_syms=start_end_syms):
            crumb = _arg_name(crumb, start_end_syms=start_end_syms)

        if start_sym in crumb or end_sym in crumb:
            return False

    return True


def has_crumbs(crumb_path, start_end_syms=('{', '}')):
    """ Return True if the `crumb_path.split(op.sep)` has item which is a crumb argument
    that starts with '{' and ends with '}'."""
    crumb_path = _get_path(crumb_path)

    splt = crumb_path.split(op.sep)
    for i in splt:
        if _is_crumb_arg(i, start_end_syms=start_end_syms):
            return True

    return False


def _replace(crumb_path, start_end_syms=('{', '}'), regexes=None, **kwargs):
    """ Return `crumb_path` where every crumb argument found in `kwargs` has been
    replaced by the given value in `kwargs."""
    if not kwargs:
        return crumb_path

    if regexes is None:
        regexes = {}

    for k in kwargs:
        karg = _arg_format(k, start_end_syms=start_end_syms, regex=regexes.get(k, None))
        if k not in crumb_path:
            raise KeyError("Could not find argument {} in"
                           " `crumb_path` {}.".format(k, crumb_path))

        crumb_path = crumb_path.replace(karg, kwargs[k])

    return crumb_path


def _split(crumb_path, start_end_syms=('{', '}')):
    """ Split `crumb_path` in two parts, the first is the base folder without any crumb argument
        and the second is the rest of `crumb_path` beginning with the first crumb argument.
        If `crumb_path` has no crumb arguments or starts with a crumb argument, return `crumb_path`.
    """
    crumb_path = _get_path(crumb_path)

    if not has_crumbs(crumb_path, start_end_syms=start_end_syms):
        return crumb_path

    if not is_valid(crumb_path, start_end_syms=start_end_syms):
        raise ValueError('Crumb path {} is not valid.'.format(crumb_path))

    start_sym, _ = start_end_syms
    if crumb_path.startswith(start_sym):
        return crumb_path

    idx = crumb_path.find(start_sym)
    base = crumb_path[0:idx]
    if base.endswith(op.sep):
        base = base[:-1]

    rest = crumb_path[idx:]

    return base, rest


def _touch(crumb_path, exist_ok=True, start_end_syms=('{', '}')):
    """ Create a leaf directory and all intermediate ones
    using the non crumbed part of `crumb_path`.
    If the target directory already exists, raise an IOError
    if exist_ok is False. Otherwise no exception is raised.
    Parameters
    ----------
    crumb_path: str

    exist_ok: bool
        Default = True

    Returns
    -------
    nupath: str
        The new path created.
    """
    if has_crumbs(crumb_path, start_end_syms=start_end_syms):
        nupath = _split(crumb_path, start_end_syms=start_end_syms)[0]
    else:
        nupath = crumb_path

    if op.exists(nupath) and not exist_ok:
        raise IOError("Folder {} already exists.".format(nupath))

    try:
        os.makedirs(nupath)
    except:
        raise
    else:
        return nupath


def _split_exists(crumb_path, start_end_syms=('{', '}')):
    """ Return True if the part without crumb arguments of `crumb_path`
    is an existing path or a symlink, False otherwise.
    Returns
    -------
    exists: bool
    """
    if has_crumbs(crumb_path):
        rpath = _split(crumb_path, start_end_syms=start_end_syms)[0]
    else:
        rpath = str(crumb_path)

    return op.exists(rpath) or op.islink(rpath)


def _check_is_subset(list1, list2):
    """ Raise an error if `list1` is not a subset of `list2`."""
    if not set(list1).issubset(set(list2)):
        raise KeyError('The `list1` argument should be a subset of `list2`, '
                       'got {} and {}.'.format(list1, list2))


def deprecated(replacement=None):
    """A decorator which can be used to mark functions as deprecated.
    replacement is a callable that will be called with the same args
    as the decorated function.

    >>> @deprecated()
    ... def foo(x):
    ...     return x
    ...
    >>> ret = foo(1)
    DeprecationWarning: foo is deprecated
    >>> ret
    1
    >>>
    >>>
    >>> def newfun(x):
    ...     return 0
    ...
    >>> @deprecated(newfun)
    ... def foo(x):
    ...     return x
    ...
    >>> ret = foo(1)
    DeprecationWarning: foo is deprecated; use newfun instead
    >>> ret
    0
    >>>
    """
    def outer(fun):
        msg = "psutil.%s is deprecated" % fun.__name__
        if replacement is not None:
            msg += "; use %s instead" % replacement
        if fun.__doc__ is None:
            fun.__doc__ = msg

        @functools.wraps(fun)
        def inner(*args, **kwargs):
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return fun(*args, **kwargs)

        return inner
    return outer
