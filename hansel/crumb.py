# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Crumb class: the smart path model class.
"""

import os.path     as op
from   copy        import deepcopy
from   collections import OrderedDict, Mapping, Sequence
from   pathlib     import Path
from   functools   import partial

from   six import string_types

from   .utils import remove_duplicates, list_children
from   ._utils import (_get_path, _arg_name,
                       _is_crumb_arg, _replace,
                       _split_exists, _split,
                       _touch, has_crumbs, is_valid,
                       #_arg_format,
                       )


class Crumb(object):
    """ The crumb path model class.
    Parameters
    ----------
    crumb_path: str
        A file or folder path with crumb arguments. See Examples.

    ignore_list: sequence of str
        A list of `fnmatch` patterns of filenames to be ignored.

    Examples
    --------
    >>> crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")
    >>> cr = Crumb(op.join(op.expanduser('~'), '{user_folder}'))
    """
    _arg_start_sym = '{'
    _arg_end_sym   = '}'

    # specify partial functions from _utils with _arg_start_sym and _arg_end_sym
    # everything would be much simpler if I hardcoded these symbols but I still
    # feel that this flexibility is nice to have.
    # _arg_format   = partial(_arg_format,   start_sym=_arg_start_sym, end_sym=_arg_end_sym)
    _is_crumb_arg = partial(_is_crumb_arg, start_sym=_arg_start_sym, end_sym=_arg_end_sym)
    _arg_name     = partial(_arg_name,     start_sym=_arg_start_sym, end_sym=_arg_end_sym)
    is_valid      = partial(is_valid,      start_sym=_arg_start_sym, end_sym=_arg_end_sym)
    has_crumbs    = partial(has_crumbs,    start_sym=_arg_start_sym, end_sym=_arg_end_sym)
    _replace      = partial(_replace,      start_sym=_arg_start_sym, end_sym=_arg_end_sym)
    _split        = partial(_split,        start_sym=_arg_start_sym, end_sym=_arg_end_sym)
    _touch        = partial(_touch,        start_sym=_arg_start_sym, end_sym=_arg_end_sym)
    _split_exists = partial(_split_exists, start_sym=_arg_start_sym, end_sym=_arg_end_sym)


    def __init__(self, crumb_path, ignore_list=()):
        self._path   = _get_path(crumb_path)
        self._argidx = OrderedDict()
        self._ignore = ignore_list
        self._update()

    @property
    def path(self):
        """Return the current crumb path string."""
        return self._path

    @path.setter
    def path(self, value):
        """ Set the current crumb path string and updates the internal members.
        Parameters
        ----------
        value: str
            A file or folder path with crumb arguments. See Examples in class docstring.
        """
        self._path = value
        self._update()

    def _check(self):
        if not self.is_valid(self._path):
            raise ValueError("The current crumb path has errors, got {}.".format(self.path))

    def _update(self):
        """ Clean up, parse the current crumb path and fill the internal
        members for functioning."""
        self._clean()
        self._check()
        self._set_argidx()
        # self._set_replace_func()

    def _clean(self):
        """ Clean up the private utility members, i.e., _argidx. """
        self._argidx = OrderedDict()

    @classmethod
    def copy(cls, crumb):
        """ Return a deep copy of the given `crumb`.
        Parameters
        ----------
        crumb: str or Crumb

        Returns
        -------
        copy: Crumb
        """
        if isinstance(crumb, cls):
            return cls(crumb._path, ignore_list=crumb._ignore)
        elif isinstance(crumb, string_types):
            return cls.from_path(crumb)
        else:
            raise TypeError("Expected a Crumb or a str to copy, got {}.".format(type(crumb)))

    def _set_argidx(self):
        """ Initialize the self._argidx dict. It holds arg_name -> index.
        The index is the position in the whole `_path.split(op.sep)` where each argument is.
        """
        fs = self._path_split()
        for idx, f in enumerate(fs):
            if self._is_crumb_arg(f):
                self._argidx[self._arg_name(f)] = idx

    def _find_arg(self, arg_name):
        """ Return the index in the current path of the crumb
        argument with name `arg_name`.
        """
        return self._argidx.get(arg_name, -1)

    def isabs(self):
        """ Return True if the current crumb path has an
        absolute path, False otherwise.
        This means that if it is valid and does not start with a `op.sep` character
        or hard disk letter.
        """
        if not self.is_valid(self._path):
            raise ValueError("The given crumb path has errors, got {}.".format(self.path))

        subp = self._path.split(self._arg_start_sym)[0]
        return op.isabs(subp)

    def abspath(self, first_is_basedir=False):
        """ Return a copy of `self` with an absolute crumb path.
        Add as prefix the absolute path to the current directory if the current
        crumb is not absolute.
        Parameters
        ----------
        first_is_basedir: bool
            If True and the current crumb path starts with a crumb argument and first_is_basedir,
            the first argument will be replaced by the absolute path to the current dir,
            otherwise the absolute path to the current dir will be added as a prefix.


        Returns
        -------
        abs_crumb: Crumb
        """
        if not self.is_valid(self._path):
            raise ValueError("The given crumb path has errors, got {}.".format(self.path))

        if self.isabs():
            return deepcopy(self)

        return self.copy(self._abspath(first_is_basedir=first_is_basedir))

    def _path_split(self):
        return self._path.split(op.sep)

    def _abspath(self, first_is_basedir=False):
        """ Return the absolute path of the current crumb path.
        Parameters
        ----------
        first_is_basedir: bool
            If True and the current crumb path starts with a crumb argument and first_is_basedir,
            the first argument will be replaced by the absolute path to the current dir,
            otherwise the absolute path to the current dir will be added as a prefix.


        Returns
        -------
        abspath: str
        """
        if not self.has_crumbs(self._path):
             return op.abspath(self._path)

        splt = self._path_split()
        path = []
        if self._is_crumb_arg(splt[0]):
            path.append(op.abspath(op.curdir))

        if not first_is_basedir:
            path.append(splt[0])

        if splt[1:]:
            path.extend(splt[1:])

        return op.sep.join(path)

    def split(self):
        """ Return a list of sub-strings of the current crumb path where the
            path parts are separated from the crumb arguments.

        Returns
        -------
        crumbs: list of str
        """
        return self._split(self._path)

    @classmethod
    def from_path(cls, crumb_path):
        """ Create an instance of Crumb out of `crumb_path`.
        Parameters
        ----------
        val: str or Crumb or pathlib.Path

        Returns
        -------
        path: Crumb
        """
        if isinstance(crumb_path, (cls, Path)):
            return crumb_path

        if isinstance(crumb_path, string_types):
            return cls(crumb_path)
        else:
            raise TypeError("Expected a `val` to be a `str`, got {}.".format(type(crumb_path)))

    # def _set_replace_func(self):
    #     """ Set the fastest replace algorithm depending on how
    #     many arguments the path has."""
    #     self._replace = self._replace2
    #     if len(self._argidx) > 5:
    #         self._replace = self._replace1

    # def _replace2(self, start_sym='{', end_sym='}', **kwargs):
    #
    #     if start_sym != '{' or end_sym != '}':
    #         raise NotImplementedError
    #
    #     if not kwargs:
    #         return self._path
    #
    #     args = {v: self._arg_format(v) for v in self._argidx}
    #
    #     for k in kwargs:
    #         if k not in args:
    #             raise KeyError("Could not find argument {}"
    #                            " in `path` {}.".format(k, self._path))
    #
    #         args[k] = kwargs[k]
    #
    #     return self._path.format_map(args)

    def _lastarg(self):
        """ Return the name and idx of the last argument."""
        for arg, idx in reversed(list(self._argidx.items())):
            return arg, idx

    def _firstarg(self):
        """ Return the name and idx of the first argument."""
        for arg, idx in self._argidx.items():
            return arg, idx

    def _is_firstarg(self, arg_name):
        """ Return True if `arg_name` is the first argument."""
        # Take into account that self._argidx is OrderedDict
        return arg_name == self._firstarg()[0]

    def _arg_values(self, arg_name, arg_values=None):
        """ Return the existing values in the file system for the crumb argument
        with name `arg_name`.
        The `arg_values` must be a sequence with the tuples with valid values of the dependent
        (previous in the path) crumb arguments.
        The format of `arg_values` work in such a way that `self._path.format(dict(arg_values[0]))`
        would give me a valid path or crumb.
        Parameters
        ----------
        arg_name: str

        arg_values: list of tuples

        Returns
        -------
        vals: list of tuples

        Raises
        ------
        ValueError: if `arg_values` is None and `arg_name` is not the
        first crumb argument in self._path

        IOError: if this crosses to any path that is non-existing.
        """
        if arg_values is None and not self._is_firstarg(arg_name):
            raise ValueError("Cannot get the list of values for {} if"
                             " the previous arguments are not filled"
                             " in `paths`.".format(arg_name))

        aidx = self._find_arg(arg_name)

        # check if the path is absolute, do it absolute
        apath = self._abspath()
        splt = apath.split(op.sep)

        if aidx == len(splt) - 1:  # this means we have to list files too
            just_dirs = False
        else:  # this means we have to list folders
            just_dirs = True

        vals = []
        if arg_values is None:
            base = op.sep.join(splt[:aidx])
            vals = [[(arg_name, val)] for val in list_children(base, just_dirs=just_dirs, ignore=self._ignore)]
        else:
            for aval in arg_values:
                #  create the part of the crumb path that is already specified
                path = self._split(self._replace(self._path, **dict(aval)))[0]

                #  list the children of `path`
                subpaths = list_children(path, just_dirs=just_dirs, ignore=self._ignore)

                #  extend `val` tuples with the new list of values for `aval`
                vals.extend([aval + [(arg_name, sp)] for sp in subpaths])

        return vals

    def replace(self, **kwargs):
        """ Return a copy of self with the crumb arguments in
        `kwargs` replaced by its values.
        Parameters
        ----------
        kwargs: strings

        Returns
        -------
        crumb:
        """
        for arg_name in kwargs:
            if arg_name not in self._argidx:
                raise KeyError("Expected `arg_name` to be one of ({}),"
                                 " got {}.".format(list(self._argidx), arg_name))

        cr = self.copy(self)
        cr._path = cr._replace(self._path, **kwargs)
        return Crumb.from_path(cr._path)

    def _arg_deps(self, arg_name):
        """ Return a subdict of `self._argidx` with the
         values from the crumb arguments that come before
         `arg_name` in the crumb path.
        Parameters
        ----------
        arg_name: str

        Returns
        -------
        arg_deps: Mapping[str, int]
        """
        argidx = self._find_arg(arg_name)
        return OrderedDict([(arg, idx) for arg, idx in self._argidx.items() if idx <= argidx])

    def values_map(self, arg_name, check_exists=False):
        """ Return a list of tuples of crumb arguments with their values.

        Parameters
        ----------
        arg_name: str

        check_exists: bool

        Returns
        -------
        values_map: list of lists of 2-tuples
        """
        arg_deps = self._arg_deps(arg_name)
        values_map = None
        for arg in arg_deps:
            values_map = self._arg_values(arg, values_map)

        if check_exists:
            paths = [self.from_path(path) for path in self._build_paths(values_map)]
            values_map_checked = [args for args, path in zip(values_map, paths) if path.exists()]
        else:
            values_map_checked = values_map

        return values_map_checked

    def _build_paths(self, values_map):
        """ Return a list of paths from each tuple of args from `values_map`
        Parameters
        ----------
        values_map: list of sequences of 2-tuple

        Returns
        -------
        paths: list of str
        """
        return [self._replace(self._path, **dict(val)) for val in values_map]

    def ls(self, arg_name, fullpath=True, rm_dups=False, make_crumbs=True, check_exists=False):
        """
        Return the list of values for the argument crumb `arg_name`.
        This will also unfold any other argument crumb that appears before in the
        path.
        Parameters
        ----------
        arg_name: str
            Name of the argument crumb to be unfolded.

        fullpath: bool
            If True will build the full path of the crumb path, will also append
            the rest of crumbs not unfolded.
            If False will only return the values for the argument with name
            `arg_name`.

        rm_dups: bool
            If True will remove and sort the duplicate values from the result.
            Otherwise it will leave it as it is.

        make_crumbs: bool
            If `fullpath` and `make_crumbs` is True will create a Crumb for
            each element of the result.

        check_exists: bool
            If True will return only str, Crumb or Path if it exists
            in the file path, otherwise it may create file paths
            that don't have to exist.

        Returns
        -------
        values: list of str or Crumb

        Examples
        --------
        >>> cr = Crumb(op.join(op.expanduser('~'), '{user_folder}'))
        >>> user_folders = cr.ls('user_folder', fullpath=True, rm_dups=True, make_crumbs=True)
        """
        if arg_name not in self._argidx:
            raise ValueError("Expected `arg_name` to be one of ({}),"
                             " got {}.".format(list(self._argidx), arg_name))

        # if the first chunk of the path is a parameter, I am not interested in this (for now)
        if self._path.startswith(self._arg_start_sym):
            raise NotImplementedError("Can't list paths that starts"
                                      " with an argument.")

        if make_crumbs and not fullpath:
            raise ValueError("`make_crumbs` can only work if `fullpath` is also True.")

        values_map = self.values_map(arg_name, check_exists=check_exists)

        if not fullpath and not make_crumbs:
            paths = [dict(val)[arg_name] for val in values_map]
        else:
            paths = self._build_paths(values_map)

        if rm_dups:
            paths = remove_duplicates(paths)

        if fullpath and make_crumbs:
            paths = sorted([self.from_path(path) for path in paths])

        return paths

    def _remaining_deps(self, arg_names):
        """ Return the name of the arguments that are dependencies of `arg_names`.
        Parameters
        ----------
        arg_names: Sequence[str]

        Returns
        -------
        rem_deps: Sequence[str]
        """
        started = False
        rem_deps = []
        for an in reversed(list(self._argidx.keys())):  # take into account that argidx is ordered
            if an in arg_names:
                started = True
            else:
                if started:
                    rem_deps.append(an)

        return rem_deps

    def touch(self):
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
        return self._touch(self._path)

    def joinpath(self, suffix):
        """ Return a copy of the current crumb with the `suffix` path appended.
        If suffix has crumb arguments, the whole crumb will be updated.
        Parameters
        ----------
        suffix: str

        Returns
        -------
        cr: Crumb
        """
        return Crumb(op.join(self._path, suffix))

    def exists(self):
        """ Return True if the current crumb path is a possibly existing path,
        False otherwise.
        Returns
        -------
        exists: bool
        """
        if not self.has_crumbs(self._path):
            return op.exists(str(self)) or op.islink(str(self))

        if not op.exists(self.split()[0]):
            return False

        last, _ = self._lastarg()
        paths = self.ls(last,
                        fullpath     = True,
                        make_crumbs  = False,
                        rm_dups   = True,
                        check_exists = False)

        return all([self._split_exists(lp) for lp in paths])

    def has_files(self):
        """ Return True if the current crumb path has any file in its
        possible paths.
        Returns
        -------
        has_files: bool
        """
        if not op.exists(self.split()[0]):
            return False

        last, _ = self._lastarg()
        paths = self.ls(last,
                        fullpath     = True,
                        make_crumbs  = True,
                        rm_dups      = False,
                        check_exists = True)

        return any([op.isfile(str(lp)) for lp in paths])

    def unfold(self):
        """ Return a list of all the existing paths until the last crumb argument.
        Returns
        -------
        paths: list of pathlib.Path
        """
        return self.ls(self._lastarg()[0],
                       fullpath    = True,
                       rm_dups     = True,
                       make_crumbs = True,
                       check_exists= True)

    def __getitem__(self, arg_name):
        """ Return the existing values of the crumb argument `arg_name`
        without removing duplicates.
        Parameters
        ----------
        arg_name: str

        Returns
        -------
        values: list of str
        """
        return self.ls(arg_name,
                       fullpath    = False,
                       rm_dups     = False,
                       make_crumbs = False,
                       check_exists= True)

    def __setitem__(self, key, value):
        if key not in self._argidx:
            raise KeyError("Expected `arg_name` to be one of ({}),"
                           " got {}.".format(list(self._argidx), key))

        self._path = self._replace(self._path, **{key: value})
        self._update()

    def __ge__(self, other):
        return self._path >= str(other)

    def __le__(self, other):
        return self._path <= str(other)

    def __gt__(self, other):
        return self._path > str(other)

    def __lt__(self, other):
        return self._path < str(other)

    def __hash__(self):
        return self._path.__hash__()

    def __contains__(self, item):
        return item in self._argidx

    def __repr__(self):
        return '{}("{}")'.format(__class__.__name__, self._path)

    def __str__(self):
        return str(self._path)

    def __eq__(self, other):
        """ Return True if `self` and `other` are equal, False otherwise.
        Parameters
        ----------
        other: Crumb

        Returns
        -------
        is_equal: bool
        """
        if self._path != other._path:
            return False

        if self._argidx != other._argidx:
            return False

        if self._ignore != other._ignore:
            return False

        return True

