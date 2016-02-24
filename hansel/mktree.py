# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Crumb class: the smart path model class.
"""

from collections import Mapping


def mktree(crumb, values_map):
    """ Create the tree of folders given the values for the crumb arguments
    of the current crumb path.
    Parameters
    ----------
    crumb: Crumb

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
        return [crumb.touch()]

    if not isinstance(values_map, (list, dict)):
        raise TypeError("Expected keys in `values_map` to be a Sequence, "
                         "got {}.".format(type(values_map)))

    paths = []
    for idx, aval in enumerate(values_map):
        if not isinstance(aval, Mapping):
            aval = dict(aval)

        if not set(aval.keys()).issubset(set(crumb.all_args())):
            raise ValueError("Expected keys in `values_map` item to be a subset of {}, "
                             "got {}.".format(crumb.all_args(), aval.keys()))

        rem_deps = crumb._args_open_parents(list(aval.keys()))
        if rem_deps:
            raise KeyError("Expected `values_map` item to not leave crumbs alone,"
                           " you forgot to add: {} in item {}".format(rem_deps, idx))

        paths.append(crumb.replace(**aval))

    _ = [path.touch() for path in paths]

    return paths
