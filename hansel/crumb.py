# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Crumb class: the smart path model class.
"""
import re
import os.path     as op
from   copy        import deepcopy
from   collections import OrderedDict
from   six         import string_types
try:
    from pathlib2 import Path
except ImportError:
    from pathlib  import Path


from   .utils  import (
                       list_subpaths,
                       fnmatch_filter,
                       regex_match_filter,
                       )

#from hansel._utils import deprecated
from   ._utils import (
                       _first_txt,
                       _build_path,
                       _arg_names,
                       _find_arg_depth,
                       _check,
                       _depth_names,
                       _depth_names_regexes,
                       _is_crumb_arg,
                       _split_exists,
                       _split,
                       _touch,
                       has_crumbs,
                       is_valid,
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
        Choices: 'fnmatch', 're' or 're.ignorecase'
        If 'fnmatch' will use fnmatch regular expressions to
        match any expression you may have in a crumb argument.
        If 're' will use re.match.
        If 're.ignorecase' will use re.match and pass re.IGNORE_CASE to re.compile.

    Examples
    --------
    >>> crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")
    >>> cr = Crumb(op.join(op.expanduser('~'), '{user_folder}'))
    """
    def __init__(self, crumb_path, ignore_list=None, regex='fnmatch'):
        self._path      = _check(crumb_path)
        self._argval    = {}  # what is the value of the argument in the current path, if any has been set.
        self._re_method = regex
        self._re_args   = None

        if ignore_list is None:
            ignore_list = []

        self._ignore = ignore_list
        self._update()

    def _update(self):
        """ Clean up, parse the current crumb path and fill the internal
        members for functioning."""
        self._set_match_function()

    def _set_match_function(self):
        """ Update self._match_filter with a regular expression
        matching function depending on the value of self._re_method."""
        if self._re_method == 'fnmatch':
            self._match_filter = fnmatch_filter
        elif self._re_method == 're':
            self._match_filter = regex_match_filter
        elif self._re_method == 're.ignorecase':
            self._match_filter = regex_match_filter
            self._re_args      = (re.IGNORECASE, )
        else:
            raise ValueError('Expected regex method value to be "fnmatch", "re" or "re.ignorecase"'
                             ', got {}.'.format(self._re_method))

    def is_valid(self, crumb_path=None):
        """ Return True if the `crumb_path` is a valid crumb path, False otherwise.
        If `crumb_path` is None, will use `self.path` instead.
        """
        if crumb_path is None:
            crumb_path = self.path

        return is_valid(crumb_path)

    @property
    def patterns(self):
        """ Returns a dict with the arg_names as keys and regular expressions as values."""
        return {arg: rgx for _, (arg, rgx) in _depth_names_regexes(self.path)}

    def set_pattern(self, arg_name, arg_regex):
        """ Set the pattern `arg_regex` to the given argument `arg_name`."""
        self._path = _build_path(self._path,
                                 arg_values=self.arg_values,
                                 with_regex=True,
                                 regexes={arg_name: arg_regex})

    def clear_pattern(self, arg_name):
        """ Clear the pattern of the given argument `arg_name`."""
        self.set_pattern(arg_name, '')

    def clear(self, arg_name):
        """ Clear the value of the given argument `arg_name`."""
        del self._argval[arg_name]

    @property
    def arg_values(self):
        """ Return a dict with the arg_names and values of the already replaced crumb arguments."""
        return self._argval

    @property
    def path(self):
        """Return the current crumb path string."""
        return _build_path(self._path, arg_values=self.arg_values, with_regex=True)

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

    def has_crumbs(self, crumb_path=None):
        """ Return True if the current path has open crumb arguments, False otherwise.
        If `crumb_path` is None will test on `self.path` instead.
        """
        if crumb_path is None:
            crumb_path = self.path
        return has_crumbs(crumb_path)

    def _open_arg_items(self):
        """ Return an iterator to the crumb _argidx items in `self` that have not been replaced yet.
        In the same order as they appear in the crumb path.

        Returns
        -------
        crumb_args: set of str

        Note
        ----
        I know that there is shorter/faster ways to program this but I wanted to maintain the
        order of the arguments in argidx in the result of this function.
        """
        for depth, arg_name in _depth_names(self.path):
            yield depth, arg_name

    def _last_open_arg(self):
        """ Return the name and idx of the last (right-most) open argument."""
        open_args = list(self._open_arg_items())
        if not open_args:
            return None, None

        for dpth, arg in reversed(open_args):
            return dpth, arg

    def _first_open_arg(self):
        """ Return the name and idx of the first (left-most) open argument."""
        for dpth, arg in self._open_arg_items():
            return dpth, arg

    def _is_first_open_arg(self, arg_name):
        """ Return True if `arg_name` is the first open argument."""
        # Take into account that self._argidx is OrderedDict
        return arg_name == self._first_open_arg()[1]

    def has_set(self, arg_name):
        """ Return True if the argument `arg_name` has been set to a
        specific value, False if it is still a crumb argument."""
        return arg_name not in set(self.open_args())

    def open_args(self):
        """ Return an iterator to the crumb argument names in `self`
        that have not been replaced yet.
        In the same order as they appear in the crumb path."""
        for _, arg_name in self._open_arg_items():
            yield arg_name

    def all_args(self):
        """ Return an iterator to all the crumb argument names in `self`,
        first the open ones and then the replaced ones.

        Returns
        -------
        crumb_args: set of str
        """
        return _arg_names(self._path)

    def copy(self, crumb=None):
        """ Return a deep copy of the given `crumb`.
        If `crumb` is None will return a copy of self.

        Parameters
        ----------
        crumb: str or Crumb

        Returns
        -------
        copy: Crumb
        """
        if crumb is None:
            crumb = self

        if isinstance(crumb, Crumb):
            nucr = Crumb(crumb._path,
                         ignore_list=crumb._ignore,
                         regex=crumb._re_method)
            nucr._argval = deepcopy(crumb._argval)
            return nucr
        elif isinstance(crumb, string_types):
            return Crumb.from_path(crumb)
        else:
            raise TypeError("Expected a Crumb or a str to copy, "
                            "got {}.".format(type(crumb)))

    def isabs(self):
        """ Return True if the current crumb path has an absolute path,
        False otherwise.
        This means that its path is valid and starts with a `op.sep` character
        or hard disk letter.
        """
        subp = _first_txt(self.path)
        return op.isabs(subp)

    def abspath(self, first_is_basedir=False):
        """ Return a copy of `self` with an absolute crumb path.
        Add as prefix the absolute path to the current directory if
        the current crumb is not absolute.
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
        nucr = self.copy()

        if not nucr.isabs():
            nucr._path = self._abspath(first_is_basedir=first_is_basedir)

        return nucr

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
        if op.isabs(self._path):
            return self._path

        splits = self._path.split(op.sep)
        basedir = [op.abspath(op.curdir)]

        if _is_crumb_arg(splits[0]):
            if first_is_basedir:
                splits.pop(0)

        basedir.extend(splits)
        return op.sep.join(basedir)

    def split(self):
        """ Return a list of sub-strings of the current crumb path where the
            first path part is separated from the crumb arguments.

        Returns
        -------
        crumbs: list of str
        """
        return _split(self.path)

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
        if isinstance(crumb_path, Crumb):
            return crumb_path.copy()
        elif isinstance(crumb_path, Path):
            return cls(str(crumb_path))
        elif isinstance(crumb_path, string_types):
            return cls(crumb_path)
        else:
            raise TypeError("Expected a `val` to be a `str`, got {}.".format(type(crumb_path)))

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

        AttributeError: if the path is not absolute

        IOError: if this crosses to any path that is non-existing.
        """
        if arg_values is None and not self._is_first_open_arg(arg_name):
            raise ValueError("Cannot get the list of values for {} if"
                             " the previous arguments are not filled"
                             " in `paths`.".format(arg_name))

        # check if the path is absolute, if not raise an AttributeError
        # this shouldn't really happen because this is a private function.
        # This check is going to be here temporarily: TODO
        if not self.isabs():
            raise AttributeError("Expected an absolute crumb path but got {}.".format(self.path))

        path = self.path
        dpth, arg_name, arg_regex = _find_arg_depth(path, arg_name)
        splt = path.split(op.sep)

        if dpth == len(splt) - 1:  # this means we have to list files too
            just_dirs = False
        else:  # this means we have to list folders
            just_dirs = True

        if arg_values is None:
            vals = self._arg_values_from_base(basedir=op.sep.join(splt[:dpth]),
                                              arg_name=arg_name,
                                              arg_regex=arg_regex,
                                              just_dirs=just_dirs)
        else:
            vals = self._extend_arg_values(arg_values=arg_values,
                                           arg_name=arg_name,
                                           arg_regex=arg_regex,
                                           just_dirs=just_dirs)

        return vals

    def _extend_arg_values(self, arg_values, arg_name, arg_regex, just_dirs):
        """ Return an extended copy of `arg_values` with valid values for `arg_name`."""
        path = self.path
        vals = []
        for aval in arg_values:
            #  create the part of the crumb path that is already specified
            nupath = _split(_build_path(path, arg_values=dict(aval)))[0]

            # THIS HAPPENS, LEAVE IT. TODO: make a test for this line
            if not op.exists(nupath):
                continue

            paths = list_subpaths(nupath,
                                  just_dirs=just_dirs,
                                  ignore=self._ignore,
                                  pattern=arg_regex,
                                  filter_func=self._match_filter)

            #  extend `val` tuples with the new list of values for `aval`
            vals.extend([aval + [(arg_name, sp)] for sp in paths])

        return vals

    def _arg_values_from_base(self, basedir, arg_name, arg_regex, just_dirs):
        """ Return a map of arg values for `arg_name` from the `basedir`."""
        vals = list_subpaths(basedir,
                             just_dirs=just_dirs,
                             ignore=self._ignore,
                             pattern=arg_regex,
                             filter_func=self._match_filter,
                             filter_args=self._re_args)

        return [[(arg_name, val)] for val in vals]

    def _check_args(self, arg_names, self_args):
        """ Raise a ValueError if `self_args` is empty.
            Raise a KeyError if `arg_names` is not a subset of `self_args`.
        """
        anames = set(arg_names)
        aself  = set(self_args)
        if not anames and not aself:
            return

        if not aself or aself is None:
            raise AttributeError('This Crumb has no remaining arguments: {}.'.format(self.path))

        if not anames.issubset(aself):
            raise KeyError("Expected `arg_names` to be a subset of ({}),"
                           " got {}.".format(list(aself), anames))

    def _check_open_args(self, arg_names):
        """ Raise a KeyError if any of the arguments in `arg_names` is not a crumb
        argument name in `self.path`.
        Parameters
        ----------
        arg_names: sequence of str
            Names of crumb arguments

        Raises
        ------
        KeyError
        """
        return self._check_args(arg_names, self_args=self.open_args())

    def update(self, **kwargs):
        """ Set the crumb arguments in path to the given values in kwargs and update
        self accordingly.
        Parameters
        ----------
        kwargs: strings

        Returns
        -------
        crumb: Crumb
        """
        self._check_args(kwargs.keys(), self_args=self.all_args())

        for k, v in kwargs.items():
            if not isinstance(v, string_types):
                raise ValueError("Expected a string for the value of argument {}, "
                                 "got {}.".format(k, v))

        path = _build_path(self.path, arg_values=kwargs, with_regex=True)
        _check(path)

        self._argval.update(**kwargs)
        return self

    def replace(self, **kwargs):
        """ Return a copy of self with the crumb arguments in
        `kwargs` replaced by its values.
        As an analogy to the `str.format` function this function could be called `format`.
        Parameters
        ----------
        kwargs: strings

        Returns
        -------
        crumb:
        """
        cr = self.copy(self)
        return cr.update(**kwargs)

    def _arg_parents(self, arg_name):
        """ Return a subdict with the open arguments name and index in `self._argidx`
        that come before `arg_name` in the crumb path. Include `arg_name` himself.
        Parameters
        ----------
        arg_name: str

        Returns
        -------
        arg_deps: Mapping[str, int]
        """
        dpth, _, _ = _find_arg_depth(self.path, arg_name)
        return OrderedDict([(arg, idx) for idx, arg in self._open_arg_items() if idx <= dpth])

    def _args_open_parents(self, arg_names):
        """ Return the name of the arguments that are dependencies of `arg_names`.
        Parameters
        ----------
        arg_names: Sequence[str]

        Returns
        -------
        rem_deps: Sequence[str]
        """
        started = False
        arg_dads = []
        for an in reversed(list(self.open_args())):  # take into account that argidx is ordered
            if an in arg_names:
                started = True
            else:
                if started:
                    arg_dads.append(an)

        return list(reversed(arg_dads))

    def values_map(self, arg_name='', check_exists=False):
        """ Return a list of tuples of crumb arguments with their values from the
        first argument until `arg_name`.
        Parameters
        ----------
        arg_name: str
            If empty will pick the arg_name of the last open argument of the Crumb.

        check_exists: bool

        Returns
        -------
        values_map: list of lists of 2-tuples
            I call values_map what is called `record` in pandas.
            It is a list of lists of 2-tuples, where each 2-tuple
            has the shape (arg_name, arg_value).
        """
        if not arg_name:
            _, arg_name = self._last_open_arg()

        if arg_name is None:
            return [list(self.arg_values.items())]

        arg_deps   = self._arg_parents(arg_name)
        values_map = None
        for arg in arg_deps:
            values_map = self._arg_values(arg, values_map)

        return sorted(self._build_and_check(values_map) if check_exists else values_map)

    def _build_and_check(self, values_map):
        """ Return a values_map of arg_values that lead to existing crumb paths."""
        paths = [cr for cr in self.build_paths(values_map, make_crumbs=True)]
        return [args for args, path in zip(values_map, paths) if path.exists()]

    def build_paths(self, values_map, make_crumbs=True):
        """ Return a list of paths from each tuple of args from `values_map`
        Parameters
        ----------
        values_map: list of sequences of 2-tuple
            Example: [[('subject_id', 'haensel'), ('candy', 'lollipop.png')],
                      [('subject_id', 'gretel'),  ('candy', 'jujube.png')],
                     ]

        make_crumbs: bool
            If `make_crumbs` is True will create a Crumb for
            each element of the result.
            Default: True.

        Returns
        -------
        paths: list of str or list of Crumb
        """
        if make_crumbs:
            return (self.replace(**dict(val)) for val in values_map)
        else:
            return (_build_path(self.path, arg_values=dict(val)) for val in values_map)

    def ls(self, arg_name='', fullpath=True, make_crumbs=True, check_exists=True):
        """ Return the list of values for the argument crumb `arg_name`.
        This will also unfold any other argument crumb that appears before in the
        path.
        Parameters
        ----------
        arg_name: str
            Name of the argument crumb to be unfolded.
            If empty will pick the arg_name of the last open argument of the Crumb.
            `arg_name` can also contain file patterns in the same syntax as
            the `regex` argument type used in the `__init__` of the object.

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
        values: list of Crumb or str

        Examples
        --------
        >>> cr = Crumb(op.join(op.expanduser('~'), '{user_folder}'))
        >>> user_folders = cr.ls('user_folder',fullpath=True,make_crumbs=True)
        """
        if not arg_name:
            _, arg_name = self._last_open_arg()

        if arg_name is None:
            arg_name = ''

        # check if there is any regex in the arg_name, if True, set the pattern
        # later check if the arg_name is correct
        arg_regex = False
        if arg_name:
            _, (arg_name, arg_regex) = tuple(_depth_names_regexes('{' + arg_name + '}'))[0]
            if arg_regex:
                old_regex = self.patterns[arg_name]
                self.set_pattern(arg_name=arg_name, arg_regex=arg_regex)

            self._check_args([arg_name], self.all_args())

        # build the paths or value maps
        self._check_ls_params(make_crumbs, fullpath)
        values_map = self.values_map(arg_name, check_exists=check_exists)
        if fullpath:
            paths = self.build_paths(values_map, make_crumbs=make_crumbs)
        else:
            paths = (dict(val)[arg_name] for val in values_map)

        # clear and set the old the pattern if it was set for this query
        if arg_regex:
            self.clear_pattern(arg_name=arg_name)
            if old_regex:
                self.set_pattern(arg_name=arg_name, arg_regex=old_regex)

        return sorted(paths)

    def _check_ls_params(self, make_crumbs, fullpath):
        """ Raise errors if the arguments are not good for ls function."""
        # if the first chunk of the path is a parameter, I am not interested in this (for now)
        # check if the path is absolute, if not raise an NotImplementedError
        if not self.isabs():
            raise NotImplementedError("Cannot list paths that start with an argument. "
                                      "If this is a relative path, use the `abspath()` "
                                      "member function.")

        if make_crumbs and not fullpath:
            raise ValueError("`make_crumbs` can only work if `fullpath` is also True.")

    def touch(self, exist_ok=True):
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
        return _touch(self.path, exist_ok=exist_ok)

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
        return Crumb(op.join(self.path, suffix))

    def exists(self):
        """ Return True if the current crumb path is a possibly existing path,
        False otherwise.
        Returns
        -------
        exists: bool
        """
        if not has_crumbs(self.path):
            return op.exists(str(self)) or op.islink(str(self))

        if not op.exists(self.split()[0]):
            return False

        _, last = self._last_open_arg()
        paths = self.ls(last,
                        fullpath=True,
                        make_crumbs=False,
                        check_exists=False)

        return any((_split_exists(lp) for lp in paths))

    def has_files(self):
        """ Return True if the current crumb path has any file in its
        possible paths.
        Returns
        -------
        has_files: bool
        """
        if not op.exists(self.split()[0]):
            return False

        _, last = self._last_open_arg()
        paths = self.ls(last,
                        fullpath=True,
                        make_crumbs=True,
                        check_exists=True)

        return any((op.isfile(str(lp)) for lp in paths))

    def unfold(self):
        """ Return a list of all the existing paths until the last crumb argument.
        If there are no remaining open arguments,
        Returns
        -------
        paths: list of pathlib.Path
        """
        if list(self.open_args()):
            return self.ls(self._last_open_arg()[1],
                           fullpath=True,
                           make_crumbs=True,
                           check_exists=True)
        else:
            return [self]

    def get_first(self, arg_name):
        """ Return the first existing value of the crumb argument `arg_name`.
        Parameters
        ----------
        arg_name: str

        Returns
        -------
        values: str
        """
        return self[arg_name][0]

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
            return [self._argval[arg_name]]
        else:
            return self.ls(arg_name,
                           fullpath=False,
                           make_crumbs=False,
                           check_exists=True)

    def __setitem__(self, key, value):
        _ = self.update(**{key: value})

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

    def __contains__(self, arg_name):
        return arg_name in self.all_args()

    def __repr__(self):
        return '{}("{}")'.format(type(self).__name__, self.path)

    def __str__(self):
        return self.path

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

        if self._argval != other._argval:
            return False

        if self._ignore != other._ignore:
            return False

        return True
