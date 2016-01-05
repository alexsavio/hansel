# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Crumb manipulation utilities
"""
import os
import os.path as op

from   six import string_types


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


def _is_crumb_arg(crumb_arg, start_sym='{', end_sym='}'):
    """ Returns True if `crumb_arg` is a well formed crumb argument, i.e.,
    is a string that starts with `start_sym` and ends with `end_sym`. False otherwise."""
    if not isinstance(crumb_arg, string_types):
        return False

    return crumb_arg.startswith(start_sym) and crumb_arg.endswith(end_sym)


def _arg_name(arg, start_sym='{', end_sym='}'):
    """ Return the name of the argument given its crumb representation.
    Parameters
    ----------
    arg_crumb: str

    Returns
    -------
    arg_name: str
    """
    if not _is_crumb_arg(arg):
        raise ValueError("Expected an well formed crumb argument, "
                         "got {}.".format(arg))
    return arg[len(start_sym):-len(end_sym)]


def _arg_format(arg_name, start_sym='{', end_sym='}'):
    """ Return the crumb argument for its string `format()` representation.
    Parameters
    ----------
    arg_name: str

    Returns
    -------
    arg_format: str
    """
    return start_sym + arg_name + end_sym


def is_valid(crumb_path, start_sym='{', end_sym='}'):
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

    splt = crumb_path.split(op.sep)
    for crumb in splt:
        if op.isdir(crumb):
            continue

        if _is_crumb_arg(crumb, start_sym=start_sym, end_sym=end_sym):
            crumb = _arg_name(crumb, start_sym=start_sym, end_sym=end_sym)

        if start_sym in crumb or end_sym in crumb:
            return False

    return True


def has_crumbs(crumb_path, start_sym='{', end_sym='}'):
    """ Return True if the `crumb_path.split(op.sep)` has item which is a crumb argument
    that starts with '{' and ends with '}'."""
    crumb_path = _get_path(crumb_path)

    splt = crumb_path.split(op.sep)
    for i in splt:
        if _is_crumb_arg(i, start_sym=start_sym, end_sym=end_sym):
            return True

    return False


def _replace(crumb_path, start_sym='{', end_sym='}', **kwargs):
    """ Return `crumb_path` where every crumb argument found in `kwargs` has been
    replaced by the given value in `kwargs."""
    if not kwargs:
        return crumb_path

    for k in kwargs:
        karg = _arg_format(k, start_sym=start_sym, end_sym=end_sym)
        if k not in crumb_path:
            raise KeyError("Could not find argument {} in"
                           " `path` {}.".format(k, crumb_path))

        crumb_path = crumb_path.replace(karg, kwargs[k])

    return crumb_path


def _split(crumb_path, start_sym='{', end_sym='}'):
    """ Return a list of sub-strings of `crumb_path` where the
        path parts are separated from the crumb arguments.
    """
    crumb_path = _get_path(crumb_path)

    if not is_valid(crumb_path, start_sym, end_sym):
        raise ValueError('Crumb path {} is not valid.'.format(crumb_path))

    splt = []
    tmp = '/' if crumb_path.startswith(op.sep) else ''
    for i in crumb_path.split(op.sep):
        if i.startswith(start_sym):
            splt.append(tmp)
            tmp = ''
            splt.append(i)
        else:
            tmp = op.join(tmp, i)

    return splt


def _touch(crumb_path, exist_ok=True, start_sym='{', end_sym='}'):
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
    if has_crumbs(crumb_path, start_sym=start_sym, end_sym=end_sym):
        nupath = _split(crumb_path, start_sym=start_sym, end_sym=end_sym)[0]
    else:
        nupath = crumb_path

    if op.exists(nupath) and not exist_ok:
        raise IOError("Folder {} already exists.".format(nupath))

    try:
        os.makedirs(nupath, exist_ok=exist_ok)
    except:
        raise
    else:
        return nupath


def _split_exists(crumb_path, start_sym='{', end_sym='}'):
    """ Return True if the part without crumb arguments of `crumb_path`
    is an existing path or a symlink, False otherwise.
    Returns
    -------
    exists: bool
    """
    if has_crumbs(crumb_path):
        rpath = _split(crumb_path, start_sym=start_sym, end_sym=end_sym)[0]
    else:
        rpath = str(crumb_path)

    return op.exists(rpath) or op.islink(rpath)
