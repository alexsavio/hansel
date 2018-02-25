import itertools
import os
import shutil
from collections import defaultdict, OrderedDict
from typing import Iterator, List, Tuple, Dict

import hansel
from hansel.utils import _get_matching_items

CrumbArgsMap = Iterator[List[Tuple[str, str]]]


def joint_value_map(crumb: hansel.Crumb, arg_names: Iterator[str], check_exists: bool = True) -> CrumbArgsMap:
    """Return a list of tuples of crumb argument values of the given
    `arg_names`.

    Parameters
    ----------
    crumb: hansel.Crumb

    arg_names: List[str]

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
        return [(i,) for i in values_map[0]]
    else:
        if not check_exists:
            values_map_checked = values_map[:]
        else:
            args_crumbs = [(args, crumb.replace(**dict(args)))
                           for args in set(itertools.product(*values_map))]

            values_map_checked = [args for args, cr in args_crumbs
                                  if cr.exists()]

    return sorted(values_map_checked)


def intersection(crumb1: hansel.Crumb, crumb2: hansel.Crumb, on: Iterator[str]=None) -> List[str]:
    """Return an 'inner join' of both given Crumbs, i.e., will return a list of
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
    of those must be the one in `on`.
    """
    if isinstance(on, str):
        on = [on]

    arg_names = list(_get_matching_items(list(crumb1.all_args()), list(crumb2.all_args()), items=on))

    if not arg_names:
        raise KeyError("Could not find matching arguments between {} and  {} limited by {}.".format(
            list(crumb1.all_args()),
            list(crumb2.all_args()),
            on)
        )

    maps1 = joint_value_map(crumb1, arg_names, check_exists=True)
    maps2 = joint_value_map(crumb2, arg_names, check_exists=True)

    intersect = set(maps1) & (set(maps2))

    return sorted(list(intersect))


def difference(crumb1: 'hansel.Crumb', crumb2: 'hansel.Crumb', on: Iterator[str] = None) -> List[str]:
    """Return the difference `crumb1` - `crumb2`, i.e., will return a list of
    Crumbs that are in `crumb1` but not in `crumb2`.

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
    """
    if isinstance(on, str):
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

    diff = set(maps1).difference(set(maps2))

    return sorted(list(diff))


def valuesmap_to_dict(values_map: CrumbArgsMap) -> Dict[str, List[str]]:
    """Converts a values_map or records type (a list of list of 2-tuple with
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


def append_dict_values(list_of_dicts: Iterator[Dict[str, str]], keys: Iterator[str]=None) -> Dict[str, List[str]]:
    """Return a dict of lists from a list of dicts with the same keys as the
    internal dicts.
    For each dict in list_of_dicts will look for the values of the given keys
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


def copy_args(src_crumb: hansel.Crumb, dst_crumb: hansel.Crumb):
    """Will copy the argument values of `src_crumb` to the open arguments of
    `dst_crumb`.
    """
    for arg_name in dst_crumb.open_args():
        dst_crumb[arg_name] = src_crumb[arg_name][0]


def _remove_if_ok_and_exists(path: str, exist_ok: bool):
    """ Raise FileExistError if the path exists and exist_ok is False."""
    if not exist_ok and os.path.exists(path):
        raise FileExistsError('Path {} already exists.'.format(path))

    if os.path.exists(path):
        os.remove(path)


def copy_all_files(src_path: str, dst_path: str, exist_ok: bool=True, verbose: bool=False):
    """Will copy everything from `src_path` to `dst_path`.
    Both can be a folder path or a file path.
    """
    copy_func = shutil.copy2
    if verbose:
        print("Copying {} -> {}".format(src_path, dst_path))

    if os.path.isdir(src_path):
        if exist_ok:
            shutil.rmtree(dst_path)

        shutil.copytree(src_path, dst_path, copy_function=copy_func)
    elif os.path.isfile(src_path):
        os.makedirs(os.path.dirname(dst_path), exist_ok=exist_ok)
        try:
            copy_func(src_path, dst_path, follow_symlinks=True)
        except shutil.SameFileError:
            os.remove(dst_path)
            copy_func(src_path, dst_path, follow_symlinks=True)


def link_all_files(src_path: str, dst_path: str, exist_ok: bool=True, verbose: bool=False):
    """Make link from src_path to dst_path."""
    if not os.path.isabs(src_path):
        src_path = os.path.relpath(src_path, os.path.dirname(dst_path))

    if verbose:
        print("Linking {} -> {}".format(src_path, dst_path))

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

    _remove_if_ok_and_exists(dst_path, exist_ok=exist_ok)
    os.symlink(src_path, dst_path)


def _crumb_fill_dst(src_crumb: hansel.Crumb, dst_crumb: hansel.Crumb) -> Iterator[Tuple[hansel.Crumb, hansel.Crumb]]:
    """ Will list `src_crumb` and copy the resulting item arguments into
    `dst_crumb`.
    All the defined arguments of `src_crumb.ls()[0]` must define `dst_crumb`
    entirely and create a path to a file or folder.
    """
    for src in src_crumb.ls():
        dst = dst_crumb.copy()
        copy_args(src, dst)
        if dst.has_crumbs():
            raise AttributeError("Destination crumb still has open arguments, "
                                 "expected to fill it. Got {}.".format(str(dst)))
        yield src, dst


def crumb_copy(src_crumb: hansel.Crumb, dst_crumb: hansel.Crumb, exist_ok: bool=False, verbose: bool=False):
    """Will copy the content of `src_crumb` into `dst_crumb` folder.
    For this `src_crumb` and `dst_crumb` must have similar set of argument
    names.
    All the defined arguments of `src_crumb.ls()[0]` must define `dst_crumb`
    entirely and create a path to a file or folder.
    """
    for src, dst in _crumb_fill_dst(src_crumb, dst_crumb):
        copy_all_files(src.path, dst.path, exist_ok=exist_ok, verbose=verbose)


def crumb_link(src_crumb: hansel.Crumb, dst_crumb: hansel.Crumb, exist_ok: bool=False, verbose: bool=False):
    """Will link the content of `src_crumb` into `dst_crumb` folder.
    For this `src_crumb` and `dst_crumb` must have similar set of argument
    names.
    All the defined arguments of `src_crumb.ls()[0]` must define `dst_crumb`
    entirely and create a path to a file or folder.
    It will create the folder structure in the base of `dst_crumb` and link
    exclusively the leaf nodes.
    """
    for src, dst in _crumb_fill_dst(src_crumb, dst_crumb):
        link_all_files(src.path, dst.path, exist_ok=exist_ok, verbose=verbose)


def groupby_pattern(
    crumb: hansel.Crumb,
    arg_name: str,
    groups: Dict[str, List[hansel.Crumb]]
) -> Dict[str, List[hansel.Crumb]]:
    """Return a dictionary with the matches of `groups` values in the
    crumb argument `arg_name` in `crumb`.

    Parameters
    ----------
    crumb: Crumb
        Crumb to the folder tree.

    arg_name: str
        Name of the crumb argument in `crumb` that must be matched with the
        values of the `groups` dict.

    groups: dict[str]->str
        A dict where the keys are group names and the values are regular
        expressions (fnmatch xor re).

    Returns
    -------
    grouped: dict[str] -> list[Crumb]
        Map of paths from groups to the corresponding path matches.
    """
    if arg_name not in crumb:
        raise KeyError('Crumb {} has no argument {}.'.format(crumb, arg_name))

    paths_matched = set()
    mods = defaultdict(list)
    for mod_name, pattern in groups.items():
        crumb.set_pattern(arg_name, pattern)
        paths = crumb.ls(arg_name)
        if paths:
            mods[mod_name] = paths
            paths_matched = paths_matched.union(paths)

        crumb.clear_pattern(arg_name)

    return mods
