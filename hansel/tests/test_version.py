# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:


import pytest

import re
import os.path  as op
import sys


def import_pyfile(pathname, mod_name=''):
    """Import the contents of filepath as a Python module.
    Parameters
    ----------
    pathname: str
        Path to the .py file to be imported as a module
    mod_name: str
        Name of the module when imported
    Returns
    -------
    mod
        The imported module
    Raises
    ------
    IOError
        If file is not found
    """
    if not op.isfile(pathname):
        raise IOError('File {0} not found.'.format(pathname))

    if sys.version_info[0] == 3 and sys.version_info[1] > 2: # Python >= 3.3
        import importlib.machinery
        loader = importlib.machinery.SourceFileLoader('', pathname)
        mod = loader.load_module(mod_name)
    else: #  2.6 >= Python <= 3.2
        import imp
        mod = imp.load_source(mod_name, pathname)
    return mod


def test_version():
    version_py = op.abspath(op.join(op.dirname(__file__), op.pardir, 'version.py'))

    mod = import_pyfile('hansel/version.py')

    assert isinstance(mod.__version__, str)
    assert re.match(r'[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,2}', mod.__version__)
    assert all(isinstance(val, int) for val in mod.VERSION)
