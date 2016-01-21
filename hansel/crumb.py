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

from   .utils  import list_subpaths, fnmatch_filter, regex_match_filter
from   ._utils import (_get_path,
                       _is_crumb_arg,
                       _replace,
                       _split_exists,
                       _split,
                       _touch,
                       _arg_params,
                       _dict_popitems,
                       has_crumbs,
                       is_valid,
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

    regex: str
        Choices: 'fnmatch' or 're'
        If 'fnmatch' will use fnmatch regular expressions to
        match any expression you may have in a crumb argument.
        If 're' will use re.match.

    Examples
    --------
    >>> crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")
    >>> cr = Crumb(op.join(op.expanduser('~'), '{user_folder}'))
    """
    # symbols indicating start and end of a crumb argument
    _start_end_syms = ('{', '}')
    _regex_sym = ':'

    # specify partial functions from _utils with _arg_start_sym and _arg_end_sym
    # everything would be much simpler if I hardcoded these symbols but I still
    # feel that this flexibility is nice to have.
    _is_crumb_arg = partial(_is_crumb_arg, start_end_syms=_start_end_syms)
    _arg_params   = partial(_arg_params,   start_end_syms=_start_end_syms, reg_sym=_regex_sym)
    is_valid      = partial(is_valid,      start_end_syms=_start_end_syms)
    has_crumbs    = partial(has_crumbs,    start_end_syms=_start_end_syms)
    _replace      = partial(_replace,      start_end_syms=_start_end_syms) # this is set inside the class
    _split        = partial(_split,        start_end_syms=_start_end_syms)
    _touch        = partial(_touch,        start_end_syms=_start_end_syms)
    _split_exists = partial(_split_exists, start_end_syms=_start_end_syms)

    def __init__(self, crumb_path, ignore_list=None, regex='fnmatch'):
        self._path   = _get_path(crumb_path)
        self._argidx = OrderedDict()  # in which order the crumb argument appears
        self._argval = {}  # what is the value of the argument in the current path, if any has been set.
        self._argreg = {}  # what is the regex of the argument
        self._re_method = regex

        if ignore_list is None:
            ignore_list = []

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
        self._set_argdicts()
        self._set_match_function()
        self._set_replace_function()

    def _set_replace_function(self):
        """ Set self._replace function as a partial function, adding regex=self._argreg."""
        self._replace = partial(self._replace, regexes=self._argreg)

    def _set_match_function(self):
        """ Update self._match_filter with a regular expression
        matching function depending on the value of self._re_method."""
        if self._re_method == 'fnmatch':
            self._match_filter = fnmatch_filter
        elif self._re_method == 're':
            self._match_filter = regex_match_filter
        else:
            raise ValueError('Expected regex method value to be `fnmatch`'
                             ' or `re`, got {}.'.format(self._re_method))

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
            nucr = cls(crumb._path, ignore_list=crumb._ignore)
            nucr._argval = deepcopy(crumb._argval)
            return nucr
        elif isinstance(crumb, string_types):
            return cls.from_path(crumb)
        else:
            raise TypeError("Expected a Crumb or a str to copy, got {}.".format(type(crumb)))

    def _set_argdicts(self):
        """ Initialize the self._argidx dict. It holds arg_name -> index.
        The index is the position in the whole `_path.split(op.sep)` where each argument is.
        """
        fs = self._path_split()
        for idx, f in enumerate(fs):
            if self._is_crumb_arg(f):
                arg_name, arg_regex = self._arg_params(f)
                self._argidx[arg_name] = idx

                if arg_regex is not None:
                    self._argreg[arg_name] = arg_regex

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

        start_sym, _ = self._start_end_syms
        subp = self._path.split(start_sym)[0]
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

        return Crumb(self._abspath(first_is_basedir=first_is_basedir),
                     ignore_list=self._ignore)

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
            return cls.copy(crumb_path)

        if isinstance(crumb_path, string_types):
            return cls(crumb_path)
        else:
            raise TypeError("Expected a `val` to be a `str`, got {}.".format(type(crumb_path)))

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
            vals = list_subpaths(base,
                                 just_dirs=just_dirs,
                                 ignore=self._ignore,
                                 pattern=self._argreg.get(arg_name, ''),
                                 filter_func=self._match_filter)

            vals = [[(arg_name, val)] for val in vals]
        else:
            for aval in arg_values:
                #  create the part of the crumb path that is already specified
                path = self._split(self._replace(self._path,
                                                 **dict(aval)))[0]

                paths = list_subpaths(path,
                                      just_dirs=just_dirs,
                                      ignore=self._ignore,
                                      pattern=self._argreg.get(arg_name, ''),
                                      filter_func=self._match_filter)

                #  extend `val` tuples with the new list of values for `aval`
                vals.extend([aval + [(arg_name, sp)] for sp in paths])

        return vals

    def _check_argidx(self, arg_names):
        """ Raise a KeyError if any of the arguments in arg_names is not a crumb
        argument name in self path.
        Parameters
        ----------
        arg_names: sequence of str
            Names of crumb arguments

        Raises
        ------
        KeyError
        """
        if not set(arg_names).issubset(set(self._argidx.keys())):
            raise KeyError("Expected `arg_names` to be a subset of ({}),"
                           " got {}.".format(list(self._argidx.keys()), arg_names))

    def setitems(self, **kwargs):
        """ Set the crumb arguments in path to the given values in kwargs and update
        self accordingly.
        Parameters
        ----------
        kwargs: strings

        Returns
        -------
        crumb: Crumb
        """
        self._check_argidx(kwargs.keys())

        self.path = self._replace(self._path, **kwargs)
        _dict_popitems(self._argreg, **kwargs)

        self._update()
        self._argval.update(**kwargs)
        return self

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
        cr = self.copy(self)
        return cr.setitems(**kwargs)

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

    def _build_paths(self, values_map, make_crumbs=False):
        """ Return a list of paths from each tuple of args from `values_map`
        Parameters
        ----------
        values_map: list of sequences of 2-tuple

        make_crumbs: bool
            If `make_crumbs` is True will create a Crumb for
            each element of the result.

        Returns
        -------
        paths: list of str or list of Crumb
        """
        if make_crumbs:
            return [self.replace(**dict(val)) for val in values_map]
        else:
            return [self._replace(self._path, **dict(val)) for val in values_map]

    def ls(self, arg_name, fullpath=True, make_crumbs=True, check_exists=False):
        """ Return the list of values for the argument crumb `arg_name`.
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
        >>> user_folders = cr.ls('user_folder',fullpath=True,make_crumbs=True)
        """
        self._check_argidx([arg_name])

        start_sym, _ = self._start_end_syms

        # if the first chunk of the path is a parameter, I am not interested in this (for now)
        if self._path.startswith(start_sym):
            raise NotImplementedError("Can't list paths that start with an argument.")

        if make_crumbs and not fullpath:
            raise ValueError("`make_crumbs` can only work if `fullpath` is also True.")

        values_map = self.values_map(arg_name, check_exists=check_exists)

        if fullpath:
            paths = self._build_paths(values_map, make_crumbs=make_crumbs)

        else:
            paths = [dict(val)[arg_name] for val in values_map]

        return sorted(paths)

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
        """ Create a leaf directory and all intermediate ones using the non
        crumbed part of `crumb_path`.
        If the target directory already exists, raise an IOError if exist_ok
        is False. Otherwise no exception is raised.
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

        paths = self.ls(last, fullpath=True, make_crumbs=False, check_exists=False)

        return any([self._split_exists(lp) for lp in paths])

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
        paths = self.ls(last, fullpath=True, make_crumbs=True, check_exists=True)

        return any([op.isfile(str(lp)) for lp in paths])

    def unfold(self):
        """ Return a list of all the existing paths until the last crumb argument.
        Returns
        -------
        paths: list of pathlib.Path
        """
        return self.ls(self._lastarg()[0], fullpath=True, make_crumbs=True, check_exists=True)

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
        if arg_name in self._argval:
            return self._argval[arg_name]
        else:
            return self.ls(arg_name, fullpath=False, make_crumbs=False, check_exists=True)

    def __setitem__(self, key, value):
        if key not in self._argidx:
            raise KeyError("Expected `arg_name` to be one of ({}),"
                           " got {}.".format(list(self._argidx), key))
        _ = self.setitems(**{key: value})

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
        return item in self._argidx or item in self._argval

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

        if self._argval != other._argval:
            return False

        if self._ignore != other._ignore:
            return False

        return True

