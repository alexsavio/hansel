# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Utilities to make crumbs
"""
import re
import os
import os.path as op
import operator
import fnmatch
from   copy        import deepcopy
from   collections import Mapping
from   functools   import partial, reduce
from   itertools   import product


def remove_duplicates(lst):
    """ Return a sorted lst of non-duplicated elements from `lst`.

    Parameters
    ----------
    lst: sequence of any

    Returns
    -------
    fslst:
        Filtered and sorted `lst` with non duplicated elements of `lst`.
    """
    return sorted(list(set(lst)))


def remove_ignored(ignore, strs):
    """ Remove from `strs` the matches to the `fnmatch` (glob) patterns and
    return the result in a list."""
    nustrs = deepcopy(strs)
    for ign in ignore:
        nustrs = [item for item in nustrs if not fnmatch.fnmatch(item, ign)]

    return nustrs


def fnmatch_filter(pattern, items):
    """ Return the items from `items` that match the fnmatch expression in `pattern`.
    Parameters
    ----------
    pattern: str
        Regular expression

    items: list of str
        The items to be checked

    Returns
    -------
    matches: list of str
        Matched items
    """
    return [item for item in items if fnmatch.fnmatch(item, pattern)]


def regex_match_filter(pattern, items):
    """ Return the items from `items` that match the regular expression in `pattern`.
    Parameters
    ----------
    pattern: str
        Regular expression

    items: list of str
        The items to be checked

    Returns
    -------
    matches: list of str
        Matched items
    """
    test = re.compile(pattern)
    return [s for s in items if test.match(s)]


def list_children(path, just_dirs=False):
    """ Return the immediate elements (files and folders) in `path`.
    Parameters
    ----------
    path: str

    just_dirs: bool
        If True will return only folders.

    ignore: sequence of str
        Sequence of glob patterns to ignore from the listing.

    re: str
        Regular expression that the result items must match.

    Returns
    -------
    paths: list of str
    """
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


def list_subpaths(path, just_dirs=False, ignore=None, pattern=None, filter_func=fnmatch_filter):
    """ Return the immediate elements (files and folders) in `path`.
    Parameters
    ----------
    path: str

    just_dirs: bool
        If True will return only folders.

    ignore: sequence of str
        Sequence of glob patterns to ignore from the listing.

    pattern: str
        Regular expression that the result items must match.

    filter_func: func
        The function to match the patterns.
        Must have as arguments: (pattern, paths) and return
        a subset of paths.

    Returns
    -------
    paths: list of str
    """
    paths = list_children(path, just_dirs=just_dirs)

    if ignore and ignore is not None:
        paths = remove_ignored(ignore, paths)

    if pattern and pattern is not None:
        paths = filter_func(pattern, paths)

    return paths


class ParameterGrid(object):
    """
    Picked from sklearn: https://github.com/scikit-learn/scikit-learn

    Grid of parameters with a discrete number of values for each.
    Can be used to iterate over parameter value combinations with the
    Python built-in function iter.

    Read more in the :ref:`User Guide <grid_search>`.
    Parameters
    ----------
    param_grid : dict of string to sequence, or sequence of such
        The parameter grid to explore, as a dictionary mapping estimator
        parameters to sequences of allowed values.
        An empty dict signifies default parameters.
        A sequence of dicts signifies a sequence of grids to search, and is
        useful to avoid exploring parameter combinations that make no sense
        or have no effect. See the examples below.
    Examples
    --------
    >>> from sklearn.grid_search import ParameterGrid
    >>> param_grid = {'a': [1, 2], 'b': [True, False]}
    >>> list(ParameterGrid(param_grid)) == (
    ...    [{'a': 1, 'b': True}, {'a': 1, 'b': False},
    ...     {'a': 2, 'b': True}, {'a': 2, 'b': False}])
    True
    >>> grid = [{'kernel': ['linear']}, {'kernel': ['rbf'], 'gamma': [1, 10]}]
    >>> list(ParameterGrid(grid)) == [{'kernel': 'linear'},
    ...                               {'kernel': 'rbf', 'gamma': 1},
    ...                               {'kernel': 'rbf', 'gamma': 10}]
    True
    >>> ParameterGrid(grid)[1] == {'kernel': 'rbf', 'gamma': 1}
    True
    """

    def __init__(self, param_grid):
        if isinstance(param_grid, Mapping):
            # wrap dictionary in a singleton list to support either dict
            # or list of dicts
            param_grid = [param_grid]
        self.param_grid = param_grid

    def __iter__(self):
        """Iterate over the points in the grid.
        Returns
        -------
        params : iterator over dict of string to any
            Yields dictionaries mapping each estimator parameter to one of its
            allowed values.
        """
        for p in self.param_grid:
            # Always sort the keys of a dictionary, for reproducibility
            items = sorted(p.items())
            if not items:
                yield {}
            else:
                keys, values = zip(*items)
                for v in product(*values):
                    params = dict(zip(keys, v))
                    yield params

    def __len__(self):
        """Number of points on the grid."""
        # Product function that can handle iterables (np.product can't).
        product = partial(reduce, operator.mul)
        return sum(product(len(v) for v in p.values()) if p else 1
                   for p in self.param_grid)

    def __getitem__(self, ind):
        """Get the parameters that would be ``ind``th in iteration
        Parameters
        ----------
        ind : int
            The iteration index
        Returns
        -------
        params : dict of string to any
            Equal to list(self)[ind]
        """
        # This is used to make discrete sampling without replacement memory
        # efficient.
        for sub_grid in self.param_grid:
            # XXX: could memoize information used here
            if not sub_grid:
                if ind == 0:
                    return {}
                else:
                    ind -= 1
                    continue

            # Reverse so most frequent cycling parameter comes first
            keys, values_lists = zip(*sorted(sub_grid.items())[::-1])
            sizes = [len(v_list) for v_list in values_lists]
            product = partial(reduce, operator.mul)
            total = product(sizes)

            if ind >= total:
                # Try the next grid
                ind -= total
            else:
                out = {}
                for key, v_list, n in zip(keys, values_lists, sizes):
                    ind, offset = divmod(ind, n)
                    out[key] = v_list[offset]
                return out

        raise IndexError('ParameterGrid index out of range')
