# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Crumb class: the smart path model class.
"""

import os
import os.path     as op
from   copy        import deepcopy
from   collections import OrderedDict, Mapping, Sequence
from   pathlib     import Path

from   six import string_types

from   hansel.utils import remove_duplicates


class Crumb(object):
    """
    The crumb path model class.

    Parameters
    ----------
    crumb_path: str
        A file or folder path with crumb arguments. See Examples.

    Examples
    --------
    >>> crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")
    >>> cr = Crumb(op.join(op.expanduser('~'), '{user_folder}'))
    """
    _arg_start_sym = '{'
    _arg_end_sym   = '}'

    def __init__(self, crumb_path):
        self._path   = self._get_path(crumb_path)
        self._argidx = OrderedDict()
        self._update()

    @property
    def path(self):
        """ Returns the current crumb path string."""
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
        """

        Returns
        -------

        """
        self._clean()
        self._check()
        self._set_argidx()
        self._set_replace_func()

    def _clean(self):
        """ Clean up the private utility members, i.e., _argidx. """
        self._argidx = OrderedDict()

    @classmethod
    def _arg_name(cls, arg):
        """ Return the name of the argument given its crumb representation.

        Parameters
        ----------
        arg_crumb: str

        Returns
        -------
        arg_name: str
        """
        if not cls._is_crumb_arg(arg):
            raise ValueError("Expected an well formed crumb argument, "
                             "got {}.".format(arg))
        return arg[1:-1]

    def _arg_format(self, arg_name):
        """ Return the argument for its string `format()` representation.

        Parameters
        ----------
        arg_name: str

        Returns
        -------
        arg_format: str
        """
        return '{' + arg_name + '}'

    def __eq__(self, other):
        if self._path != other._path:
            return False

        if self._argidx != other._argidx:
            return False

        return True

    @classmethod
    def copy(cls, crumb):
        if isinstance(crumb, cls):
            return cls(crumb._path)
        elif isinstance(crumb, string_types):
            return cls.from_path(crumb)
        else:
            raise ValueError("Expected a Crumb or a str to copy, got {}.".format(type(crumb)))

    def _set_argidx(self):
        """ Initialize the self._argidx dict. It holds arg_name -> index.
        The index is the position in the whole `_path.split(op.sep)` where each argument is.
        """
        fs = self._path_split()
        for idx, f in enumerate(fs):
            if self._is_crumb_arg(f):
                self._argidx[self._arg_name(f)] = idx

    def _set_replace_func(self):
        """ Set the fastest replace algorithm depending on how
        many arguments the path has."""
        self._replace = self._replace2
        if len(self._argidx) > 5:
            self._replace = self._replace1

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

    def _default_map(self):
        """ Return the dict with the default format values of the
            crumb arguments."""
        return {v: self._arg_format(v) for v in self._argidx}

    @classmethod
    def _split(cls, crumb_path):
        """ Return a list of sub-strings of `crumb_path` where the
            path parts are separated from the crumb arguments.
        """
        crumb_path = cls._get_path(crumb_path)

        splt = []
        tmp = '/' if crumb_path.startswith(op.sep) else ''
        for i in crumb_path.split(op.sep):
            if i.startswith(cls._arg_start_sym):
                splt.append(tmp)
                tmp = ''
                splt.append(i)
            else:
                tmp = op.join(tmp, i)

        return splt

    @classmethod
    def is_valid(cls, crumb_path):
        """ Return True if `crumb_path` is a well formed path with crumb arguments,
        False otherwise.

        Parameters
        ----------
        crumb_path: str

        Returns
        -------
        is_valid: bool
        """
        crumb_path = cls._get_path(crumb_path)

        splt = crumb_path.split(op.sep)
        for crumb in splt:
            if op.isdir(crumb):
                continue

            if cls._is_crumb_arg(crumb):
                crumb = cls._arg_name(crumb)

            if cls._arg_start_sym in crumb or cls._arg_end_sym in crumb:
                return False

        return True

    @classmethod
    def _is_crumb_arg(cls, crumb_arg):
        """ Returns True if `crumb_arg` is a well formed
        crumb argument.

        Parameters
        ----------
        crumb_arg: str
            The string representing a crumb argument, e.g., "{sample_id}"

        Returns
        -------
        is_crumb_arg: bool
        """
        if not isinstance(crumb_arg, string_types):
            return False

        return crumb_arg.startswith(cls._arg_start_sym) and crumb_arg.endswith(cls._arg_end_sym)

    @classmethod
    def has_crumbs(cls, crumb_path):
        """ Return True if the `crumb_path.split(op.sep)` has item which is a crumb argument
        that starts with '{' and ends with '}'."""
        crumb_path = cls._get_path(crumb_path)

        splt = crumb_path.split(op.sep)
        for i in splt:
            if cls._is_crumb_arg(i):
                return True

        return False

    @classmethod
    def _get_path(cls, crumb_path):
        if isinstance(crumb_path, cls):
            crumb_path = crumb_path._path

        if not isinstance(crumb_path, string_types):
            raise ValueError("Expected `crumb_path` to be a {}, got {}.".format(string_types, type(crumb_path)))

        return crumb_path

    @classmethod
    def from_path(cls, crumb_path):
        """ Create an instance of Crumb or pathlib.Path out of `crumb_path`.
        It will return a Crumb if `crumb_path` has crumbs or

        Parameters
        ----------
        val: str, Crumb or pathlib.Path

        Returns
        -------
        path: Crumb or pathlib.Path
        """
        if isinstance(crumb_path, (cls, Path)):
            return crumb_path

        if isinstance(crumb_path, string_types):
            if cls.has_crumbs(crumb_path):
                return cls(crumb_path)
            else:
                return Path(crumb_path)
        else:
            raise ValueError("Expected a `val` to be a `str`, got {}.".format(type(crumb_path)))

    def _replace1(self, **kwargs):
        if not kwargs:
            return self._path

        args = self._default_map()
        for k in kwargs:
            if k not in args:
                raise KeyError("Could not find argument {}"
                               " in `path` {}.".format(k, self._path))

            args[k] = kwargs[k]

        return self._path.format_map(args)

    def _replace2(self, **kwargs):
        if not kwargs:
            return self._path

        path = self._path
        for k in kwargs:
            karg = self._arg_format(k)
            if k not in path:
                raise KeyError("Could not find argument {} in"
                               " `path` {}.".format(k, self._path))

            path = path.replace(karg, kwargs[k])

        return path

    def _lastarg(self):
        """ Return the name and idx of the last argument."""
        for arg, idx in reversed(list(self._argidx.items())):
            return arg, idx

    def _firstarg(self):
        """Return the name and idx of the first argument."""
        for arg, idx in self._argidx.items():
            return arg, idx

    def _is_firstarg(self, arg_name):
        """
        """
        argidx = self._find_arg(arg_name)
        for an in self._argidx:
            if self._find_arg(an) < argidx:
                return False
        return True

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

        def list_children(path, just_dirs=False):
            if not op.exists(path):
                raise IOError("Expected an existing path, but could not"
                              " find {}.".format(path))

            if op.isfile(path):
                if just_dirs:
                    vals = []
                else:
                    vals = [path]
            else:
                if just_dirs: # this means we have to list only folders
                    vals = [d for d in os.listdir(path) if op.isdir(op.join(path, d))]
                else:   # this means we have to list files
                    vals = os.listdir(path)

            return vals

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
            vals = [[(arg_name, val)] for val in list_children(base, just_dirs=just_dirs)]
        else:
            for aval in arg_values:
                #  create the part of the crumb path that is already specified
                path = self._split(self._replace(**dict(aval)))[0]

                #  list the children of `path`
                subpaths = list_children(path, just_dirs=just_dirs)

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
        cr._path = cr._replace(**kwargs)
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

    def ls(self, arg_name, fullpath=True, duplicates=True, make_crumbs=True):
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

        duplicates: bool
            If False will remove and sort the duplicate values from the result.
            Otherwise it will leave it as it is.

        make_crumbs: bool
            If `fullpath` and `make_crumbs` is True will create a Crumb or a pathlib.Path
            for each element of the result. This will depende if the result item still has
            crumb arguments or not.

        Returns
        -------
        values: list of str or Crumb

        Examples
        --------
        >>> cr = Crumb(op.join(op.expanduser('~'), '{user_folder}'))
        >>> user_folders = cr.ls('user_folder', fullpath=True, duplicates=True, make_crumbs=True)
        """
        if arg_name not in self._argidx:
            raise ValueError("Expected `arg_name` to be one of ({}),"
                             " got {}.".format(list(self._argidx), arg_name))

        # if the first chunk of the path is a parameter, I am not interested in this (for now)
        if self._path.startswith(self._arg_start_sym):
            raise NotImplementedError("Can't list paths that starts"
                                      " with an argument.")

        #if make_crumbs and not fullpath:
        #    raise ValueError("`make_crumbs` can only work if `fullpath` is also True.")
        if not fullpath:
            make_crumbs = False

        arg_deps = self._arg_deps(arg_name)
        args_vals = None
        for arg in arg_deps:
            args_vals = self._arg_values(arg, args_vals)

        if not fullpath:  # this means we can return the list of crumbs directly
            values = [dict(val)[arg_name] for val in args_vals]
        else:  # this means we have to build the full paths
            values = [self._replace(**dict(val)) for val in args_vals]

        if not duplicates:
            values = remove_duplicates(values)

        if fullpath and make_crumbs:
            values = [self.from_path(val) for val in values]

        return values

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
        If the target directory already exists, raise an OSError
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

    @classmethod
    def _touch(cls, crumb_path, exist_ok=True):
        """ Create a leaf directory and all intermediate ones
        using the non crumbed part of `crumb_path`.
        If the target directory already exists, raise an OSError
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
        if cls.has_crumbs(crumb_path):
            nupath = cls._split(crumb_path)[0]
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

    def mktree(self, values_map):
        """ Create the tree of folders given the values for the crumb arguments
        of the current crumb path.

        Parameters
        ----------
        values_map: Sequence[Sequence[2-Tuple[str, str]]] or Sequence[Dict[str, str]]
            The lists of values to substitute each crumb argument that you want.
            Do not leave dependent arguments alone.
            Example: [[('subject_id', 'pat_0001'), ('session_id', 'session_1')],
                      [('subject_id', 'pat_0002'), ('session_id', 'session_1')],
                      ....
                     ]

            Example: [{'subject_id': 'pat_0001', 'session_id': 'session_1'},
                      {'subject_id': 'pat_0002', 'session_id': 'session_1'},
                      ....
                     ]

        Returns
        -------
        paths: list of Paths
            The paths that have been created.
        """
        if values_map is None:
            return [self.touch()]

        if not isinstance(values_map, (Sequence, Mapping)):
            raise ValueError("Expected keys in `values_map` to be a Sequence, "
                             "got {}.".format(type(values_map)))

        paths = []
        for idx, aval in enumerate(values_map):
            if not isinstance(aval, Mapping):
                aval = dict(aval)

            if not set(aval.keys()).issubset(set(self._argidx.keys())):
                raise ValueError("Expected keys in `values_map` item to be a subset of {}, "
                                 "got {}.".format(self._argidx.keys(), values_map.keys()))

            rem_deps = self._remaining_deps(list(aval.keys()))
            if rem_deps:
                raise KeyError("Expected `values_map` item to not leave crumbs alone,"
                               " you forgot to add: {} in item {}".format(rem_deps, idx))

            paths.append(self.replace(**aval))

        return [self._touch(str(path)) for path in paths]

    def exists(self):
        """ Return True if the current crumb path is a possibly existing path,
        False otherwise.

        Returns
        -------
        exists: bool
        """
        if not op.exists(self.split()[0]):
            return False

        last, _ = self._lastarg()
        paths = self.ls(last, fullpath=True, make_crumbs=False, duplicates=True)
        return all([self._exists(lp) for lp in paths])

    @classmethod
    def _exists(cls, crumb_path):
        """ Return True if the part without crumb arguments of `crumb_path`
        is an existing path or a symlink, False otherwise.

        Returns
        -------
        exists: bool
        """
        if cls.has_crumbs(crumb_path):
            rpath = cls._split(crumb_path)[0]
        else:
            rpath = crumb_path

        return op.exists(rpath) or op.islink(rpath)

    def __getitem__(self, item):
        return self.ls(item, fullpath=False, duplicates=False, make_crumbs=False)

    def __setitem__(self, key, value):
        if key not in self._argidx:
            raise KeyError("Expected `arg_name` to be one of ({}),"
                           " got {}.".format(list(self._argidx), key))

        self._path = self._replace(**{key: value})
        self._update()

    def __repr__(self):
        return '{}("{}")'.format(__class__.__name__, self._path)

    def __str__(self):
        return str(self._path)


