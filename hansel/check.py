# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Helper functions to check crumbs or paths.
"""

from .crumb import Crumb
from ._utils import has_crumbs


def check_path(path):
    """ Return a Crumb if `path` has crumb arguments, a str otherwise.

    Parameters
    ----------
    path: str

    Returns
    -------
    path: str or Crumb
    """
    if has_crumbs(path):
        return Crumb(path)
    else:
        return path

