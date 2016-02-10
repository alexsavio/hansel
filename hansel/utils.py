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
import warnings
import functools

from   copy        import deepcopy
from   collections import Mapping
from   functools   import partial, reduce
from   itertools   import product

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
    """ Return the items from `items` that match the fnmatch expression in `pattern`.
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
    """ Return the items from `items` that match the regular expression in `pattern`.
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
    """ Return a list of elements that are the intersection between the set of elements
    of `list1` and `list2`·
    This will keep the same order of the elements in `list1`.
    """
    return (arg_name for arg_name in list1 if arg_name in list2)


def _intersect_crumb_args(crumb1, crumb2):
    """ Return a list of `arg_names` that are the intersection between the arguments
    of `crumb1` and `crumb2`·
    This will keep the same order as the arguments are in `all_args` function from `crumb1`.
    """
    return list_intersection(crumb1.all_args(), crumb2.all_args())


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

    KeyError:
        If the result is empty.
    """
    if items is None:
        arg_names = list_intersection(list1, list2)
    else:
        _check_is_subset(items, list1)
        _check_is_subset(items, list2)
        arg_names = items

    if not arg_names:
        raise KeyError("Could not find matching arguments in "
                       "{} and {}.".format(list1, list2))

    return arg_names


def intersection(crumb1, crumb2, on=None):
    """ Return an 'inner join' of both given Crumbs, i.e., will return a list of
    Crumbs with common values for the common arguments of both crumbs.

    If `on` is None, will use all the common arguments names of both crumbs.
    Otherwise will use only the elements of `on`. All its items must be in both crumbs.

    Returns
    -------
    arg_names: list
        The matching items.

    Parameters
    ----------
    crumb1: hansel.Crumb

    crumb2: hansel.Crumb

    on: list of str
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
    Use with care, ideally the argument matches should be in the same order in both crumbs.

    Both crumbs must have at least one matching identifier argument and one
    of those must be the one in `id_colname`.
    """
    arg_names = _get_matching_items(crumb1.all_args(), crumb2.all_args(), items=on)



#
# def copy_matching_df_subjects(df, src_crumb, dst_crumb, src_crumb_cols,
#                               dst_crumb_cols, overwrite=False):
#     """ Copy the tree of the matching src_crumb to dst_crumb.
#     The crumb values are taked from `df`.
#
#     Parameters
#     ----------
#     df: pandas.DataFrame
#
#     src_crumb: hansel.Crumb
#         Example: Crumb("/home/alexandre/data/ftlad/data/{year:2*}/{subj_id}")
#
#     dst_crumb: hansel.Crumb
#         Example: Crumb('/home/alexandre/data/dti_ftlad.git/raw/{diagnosis}/{subj_id}')
#
#     src_crumb_cols: list of 2-tuples
#         A `df` to `src_crumb` column/argument name mapping.
#         Example: [('NUK Pseudonym', 'subj_id')]
#
#     dst_crumb_cols: list of 2-tuples
#         A `df` to `dst_crumb` column/argument name mapping.
#         Example: [('NUK Pseudonym', subj_id'),
#                   ('Diagnosis', 'diagnosis'),
#                  ]
#
#     overwrite: bool
#
#
#     Returns
#     -------
#     missing_rows: pandas.DataFrame
#
#     Notes
#     -----
#     - both crumbs must have at least one matching identifier argument and one
#     of those must be the one in `id_colname`.
#     - the dst_crumb must be fully defined by the arguments in dst_crumb_cols.
#     """
#     # get the crumb arguments of the name column maps
#     src_crumb_args = [item[1] for item in src_crumb_cols]
#     dst_crumb_args = [item[1] for item in dst_crumb_cols]
#
#     # TODO: get the values maps for all the args
#     def pandas_fill_crumbs(df, crumb, arg_names=None):
#         """Use `df` row values to fill `crumb` and return a list of each
#         filled `crumb`."""
#         arg_names = _get_matching_items(df.columns, crumb.all_args(), arg_names)
#         return (crumb.replace(**rec) for rec in df[arg_names].to_dict(orient='records'))
#
#
#     # I copy=False to not copy the whole data because I am using the `df` read-only
#     src_df = _pandas_rename_cols(df, src_crumb_cols)
#     dst_df = _pandas_rename_cols(df, dst_crumb_cols)
#
#     # get the filled crumbs
#     src_crumbs = pandas_fill_crumbs(src_df, src_crumb, arg_names=src_crumb_args)
#     dst_crumbs = pandas_fill_crumbs(dst_df, dst_crumb, arg_names=dst_crumb_args)
#
#     # loop through the crumb lists
#     for idx, (src, dst) in enumerate(zip(src_crumbs, dst_crumbs)):
#         if dst.has_crumbs():
#             raise AttributeError('The destination crumb still has open '
#                                  'arguments: {}, expected a fully specified
#                                  'Crumb.'.format(dst))
#
#         src_paths = src.unfold()
#         if len(src_paths) != 1:
#             raise KeyError('The source crumb {} unfolds in {} '
#                            'paths.'.format(src, len(src_paths)))
#
#         src_path = src_paths[0].path
#
#         if not op.exists(src_path):
#             missing = missing_rows.append(df.irow(idx))
#             continue
#
#         if copy_tree(src_path, dst.path, overwrite=overwrite):
#             copied = copied.append(df.irow(idx))
#
#     return missing, copied
#


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
