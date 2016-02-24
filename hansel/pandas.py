# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Utilities to fill crumbs with data from pandas DataFrames.
#TODO: add tests
"""
from hansel.utils import _get_matching_items


def _pandas_rename_cols(df, col_map):
    """ Return a copy of `df` with the columns renamed as in `col_map`.
    Parameters
    ----------
    df: pandas.DataFrame

    col_map: dict[str] -> str
        This is a "DataFrame column name" to "crumb argument name" relation
        dictionary.
        Example: {'Subject ID': 'subject_id'}

    Returns
    -------
    renamed: pandas.DataFrame
    """
    renamed = df.copy()
    renamed.columns = [col_map.get(col_name, col_name) for col_name in df.columns]
    return renamed


def df_to_valuesmap(df, crumb_arg_names, arg_names=None):
    """ Return a values_map from data in `df` and
    the matching column and arguments names from `df`, `crumb_arg_names`
    and `arg_names`.
    Parameters
    ----------
    df: pandas.DataFrame

    crumb: hansel.Crumb

    arg_names: sequence of str
        A list of the crumb arguments and DataFrame columns to extract
        the info to fill the crumbs.
        Both must match, or use _pandas_rename_cols to rename the columns.
        If None, will look for all the arguments that match in both
        `df` and `arg_names`.
        Example: ['subject_id']


    Returns
    -------
    values_map: list of sequences of 2-tuple
    """
    crumb_names = _get_matching_items(df.columns,
                                      crumb_arg_names,
                                      arg_names)

    # get the columns of df that have been matched
    return (list(rec.items()) for rec in df[crumb_names].to_dict(orient='records'))


def pandas_fill_crumbs(df, crumb, names_map=None):
    """ Create a generator of crumbs filled with the `df` column names and `crumb`
    arguments that match or the ones indicated in `names_map`.
    Parameters
    ----------
    df: pandas.DataFrame

    crumb: hansel.Crumb

    names_map: sequence of sequences of 2-tuple or dict[str] -> str
        This is a "DataFrame column name" to "crumb argument name" relation
        dictionary.
        Example: {'Subject ID': 'subject_id'}
        If None will make a dictionary from the open crumbs arguments, e.g.,
        {'subject_id': 'subject_id'}.

        The values of this dict will be used to filter the columns
        in `df` and the crumb arguments in `crumb`.

        You may need to rename the columns of `df` before using this.

    Returns
    -------
    crumbs: generator of crumbs
        Crumbs filled with the data in `df`.
    """
    if names_map is None:
        names_map = {arg_name: arg_name for arg_name in crumb.open_args()}

    nmap = names_map
    if not isinstance(nmap, dict):
        nmap = dict(nmap)

    values_map = (df
                    .pipe(_pandas_rename_cols, nmap)
                    .pipe(df_to_valuesmap, list(crumb.all_args()),
                          arg_names=list(nmap.values()))
                  )

    return (crumb.replace(**dict(argvals)) for argvals in values_map)
