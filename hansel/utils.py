"""
Utilities to make crumbs
"""
import fnmatch
import itertools
import operator
import os
import re
from collections import Mapping, OrderedDict
from functools import partial, reduce
from typing import Any, Iterator, List, Callable, Tuple

from hansel._utils import _check_is_subset, _is_crumb_arg

CrumbArgsSequence = Iterator[Tuple[str, str]]
CrumbArgsSequences = Iterator[CrumbArgsSequence]


def rm_dups(lst: Iterator[Any]) -> List[Any]:
    """Return a sorted lst of non-duplicated elements from `lst`.

    Parameters
    ----------
    lst: sequence of any

    Returns
    -------
    fslst:
        Filtered and sorted `lst` with non duplicated elements of `lst`.
    """
    return sorted(list(set(lst)))


def remove_ignored(ignore: [str, Iterator[str]], strs: Iterator[str]) -> Iterator[str]:
    """Remove from `strs` the matches to the `fnmatch` (glob) patterns and
    return the result in a list."""
    if isinstance(ignore, str):
        ignore = [ignore]
    yield from (item for ign in ignore for item in strs if not fnmatch.fnmatch(item, ign))


def fnmatch_filter(pattern: str, items: Iterator[str], *args) -> Iterator[str]:
    """Return the items from `items` that match the fnmatch expression in
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
    yield from (item for item in items if fnmatch.fnmatch(item, pattern))


def regex_match_filter(pattern: str, items: Iterator[str], *args) -> Iterator[str]:
    """Return the items from `items` that match the regular expression in
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
    yield from (s for s in items if test.match(s))


def list_children(path: str, just_dirs: bool = False) -> Iterator[str]:
    """Return the immediate elements (files and folders) in `path`.
    Parameters
    ----------
    path:

    just_dirs:
        If True will return only folders.

    Returns
    -------
    paths: list of str
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            'Expected an existing path, but could not find "{}".'.format(path)
        )

    if os.path.isfile(path):
        if just_dirs:
            return []
        else:
            return [path]
    else:
        if just_dirs:  # this means we have to list only folders
            yield from (d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)))
        else:  # this means we have to list files
            yield from os.listdir(path)


def list_subpaths(path: str,
                  just_dirs: bool = False,
                  ignore: Iterator[str] = None,
                  pattern: Iterator[str] = None,
                  filter_func: Callable = fnmatch_filter,
                  filter_args: Callable = None) -> Iterator[str]:
    """Return the immediate elements (files and folders) within `path`.
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
    paths
    """
    paths = list_children(path, just_dirs=just_dirs)

    if ignore and ignore is not None:
        paths = remove_ignored(ignore, paths)

    if pattern and pattern is not None:
        if filter_args is None:
            filter_args = ()

        paths = filter_func(pattern, paths, *filter_args)

    yield from paths


def list_intersection(list1: Iterator[str], list2: Iterator[str]) -> Iterator[str]:
    """Return a list of elements that are the intersection between the set of
    elements of `list1` and `list2`·
    This will keep the same order of the elements in `list1`.
    """
    yield from (arg_name for arg_name in list1 if arg_name in list2)


def _get_matching_items(list1: Iterator[str], list2: Iterator[str], items: List[str] = None) -> List[str]:
    """If `items` is None, Return a list of items that are in
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
    if not items or items is None:
        return list(list_intersection(list1, list2))

    try:
        _check_is_subset(items, list1)
        _check_is_subset(items, list2)
    except KeyError:
        return []
    else:
        return items


def is_crumb_arg(crumb_arg):
    """ Return True if `crumb_arg` is a well formed crumb argument, i.e.,
    is a string that starts with `start_sym` and ends with `end_sym`.
    False otherwise.
    """
    return _is_crumb_arg(crumb_arg)


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
    >>> from hansel.utils import ParameterGrid
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
