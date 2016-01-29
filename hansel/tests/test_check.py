# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:


from six import string_types
from hansel.check import check_path
from hansel.crumb import Crumb


def test_check():

    assert isinstance(check_path('/home/hansel/{files}'), Crumb)

    assert isinstance(check_path('/home/hansel'), string_types)
