# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:


import pytest

import re
import importlib
import os.path  as op


def test_version():
    version_py = op.abspath(op.join(op.dirname(__file__), op.pardir, 'version.py'))

    mod = importlib.machinery.SourceFileLoader('version', 'hansel/version.py').load_module()

    assert isinstance(mod.__version__, str)
    assert re.match(r'[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,2}', mod.__version__)
    assert all(isinstance(val, int) for val in mod.VERSION)
