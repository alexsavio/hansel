# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Utilities to make crumbs
"""
import fnmatch
import operator
import itertools
import os
import os.path as op
import re
from   collections import Mapping, defaultdict, OrderedDict
from   copy        import deepcopy
from   functools   import partial, reduce

from   six import string_types

from ._utils import _check_is_subset


def rm_dups(lst):
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


def fnmatch_filter(pattern, items, *args):
    """ Return the items from `items` that match the fnmatch expression in
    `pattern`.
    Parameters
    ----------
    pattern: str
        Regular expression

    items: list of str
        The items to be checked

    args: ignored

    Returns
    -------
    matches: list of str
        Matched items
    """
    return [item for item in items if fnmatch.fnmatch(item, pattern)]


def regex_match_filter(pattern, items, *args):
    """ Return the items from `items` that match the regular expression in
    `pattern`.
    Parameters
    ----------
    pattern: str
        Regular expression

    items: list of str
        The items to be checked

    args: re.compile arguments

    Returns
    -------
    matches: list of str
        Matched items
    """
    test = re.compile(pattern, *args)
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


def list_subpaths(path, just_dirs=False, ignore=None, pattern=None,
                  filter_func=fnmatch_filter, filter_args=None):
    """ Return the immediate elements (files and folders) within `path`.
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

    filter_args: filter func arguments
        Arguments for the filter function.

    Returns
    -------
    paths: list of str
    """
    paths = list_children(path, just_dirs=just_dirs)

    if ignore and ignore is not None:
        paths = remove_ignored(ignore, paths)

    if pattern and pattern is not None:
        if filter_args is None:
            filter_args = ()

        paths = filter_func(pattern, paths, *filter_args)

    return paths


def list_intersection(list1, list2):
    """ Return a list of elements that are the intersection between the set of
    elements of `list1` and `list2`·
    This will keep the same order of the elements in `list1`.
    """
    return (arg_name for arg_name in list1 if arg_name in list2)


def _get_matching_items(list1, list2, items=None):
    """ If `items` is None, Return a list of items that are in
    `list1` and `list2`. Otherwise will return the elements of `items` if
    they are in both lists.
    Keep the order in `list1` or in `items`.

    Returns
    -------
    arg_names: list
        The matching items.

    Raises
    ------
    ValueError:
        If an element of items does not exists in either `list1` or `list2`.
    """
    if items is None:
        arg_names = list_intersection(list1, list2)
    else:
        try:
            _check_is_subset(items, list1)
            _check_is_subset(items, list2)
        except KeyError:
            arg_names = []
        except:
            raise
        else:
            arg_names = items

    return arg_names


def joint_value_map(crumb, arg_names, check_exists=True):
    """ Return a list of tuples of crumb argument values of the given
    `arg_names`.
    Parameters
    ----------
    arg_name: str

    check_exists: bool
        If True will return only a values_map with sets of crumb arguments that
        fill a crumb to an existing path.
        Otherwise it won't check if they exist and return all possible
        combinations.

    Returns
    -------
    values_map: list of lists of 2-tuples
        I call values_map what is called `record` in pandas. It is a list of
        lists of 2-tuples, where each 2-tuple has the
        shape (arg_name, arg_value).
    """
    values_map = []
    for arg_name in arg_names:
        values_map.append(list((arg_name, arg_value)
                          for arg_value in crumb[arg_name]))

    if len(arg_names) == 1:
        return [(i, ) for i in values_map[0]]
    else:
        if not check_exists:
            values_map_checked = values_map[:]
        else:
            args_crumbs = [(args, crumb.replace(**dict(args)))
                           for args in set(itertools.product(*values_map))]

            values_map_checked = [args for args, cr in args_crumbs
                                  if cr.exists()]

    return sorted(values_map_checked)


def intersection(crumb1, crumb2, on=None):
    """ Return an 'inner join' of both given Crumbs, i.e., will return a list of
    Crumbs with common values for the common arguments of both crumbs.

    If `on` is None, will use all the common arguments names of both crumbs.
    Otherwise will use only the elements of `on`. All its items must be in
    both crumbs.

    Returns
    -------
    arg_names: list
        The matching items.

    Parameters
    ----------
    crumb1: hansel.Crumb

    crumb2: hansel.Crumb

    on: str or list of str
        Crumb argument names common to both input crumbs.

    Raises
    ------
    ValueError:
        If an element of `on` does not exists in either `list1` or `list2`.

    KeyError:
        If the result is empty.

    Returns
    -------
    inner_join: list[hansel.Crumb]

    Notes
    -----
    Use with care, ideally the argument matches should be in the same order in
    both crumbs.

    Both crumbs must have at least one matching identifier argument and one
    of those must be the one in `id_colname`.

    # TODO: this function can still be more efficient.
    """
    if isinstance(on, string_types):
        on = [on]

    arg_names = list(_get_matching_items(list(crumb1.all_args()),
                                         list(crumb2.all_args()),
                                         items=on))

    if not arg_names:
        raise KeyError("Could not find matching arguments between "
                       "{} and  {} limited by {}.".format(list(crumb1.all_args()),
                                                          list(crumb2.all_args()),
                                                          on))

    maps1 = joint_value_map(crumb1, arg_names, check_exists=True)
    maps2 = joint_value_map(crumb2, arg_names, check_exists=True)

    intersect = set(maps1) & (set(maps2))

    return sorted(list(intersect))


def valuesmap_to_dict(values_map):
    """ Converts a values_map or records type (a list of list of 2-tuple with
    shape '(arg_name, arg_value)') to a dictionary of lists of values where the
    keys are the arg_names.
    Parameters
    ----------
    values_map: list of list of 2-tuple of str

    Returns
    -------
    adict: dict
        The dictionary with the values in `values_map` in the form of a
        dictionary.

    Raises
    ------
    IndexError
        If the list_of_dicts is empty or can't be indexed.

    KeyError
        If any list inside the `values_map` doesn't have all the keys in the
        first dict.
    """
    return append_dict_values([OrderedDict(rec) for rec in values_map])


def append_dict_values(list_of_dicts, keys=None):
    """Return a dict of lists from a list of dicts with the same keys as the
    internal dicts.
    For each dict in list_of_dicts with look for the values of the given keys
    and append it to the output dict.

    Parameters
    ----------
    list_of_dicts: list of dicts
        The first dict in this list will be used as reference for the key names
        of all the other dicts.

    keys: list of str
        List of keys to create in the output dict
        If None will use all keys in the first element of list_of_dicts
    Returns
    -------
    DefaultOrderedDict of lists

    Raises
    ------
    IndexError
        If the list_of_dicts is empty or can't be indexed.

    KeyError
        If any dict inside the `list_of_dicts` doesn't have all the keys in the
        first dict.
    """
    if keys is None:
        try:
            keys = list(list_of_dicts[0].keys())
        except IndexError:
            raise IndexError('Could not get the first element of the list.')

    dict_of_lists = defaultdict(list)
    for d in list_of_dicts:
        for k in keys:
            dict_of_lists[k].append(d[k])
    return dict_of_lists


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
                for v in itertools.product(*values):
                    params = OrderedDict(zip(keys, v))
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
