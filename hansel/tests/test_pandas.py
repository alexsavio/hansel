# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

import pytest

import os.path as op

import pandas as pd

from hansel.pandas import df_to_valuesmap, pandas_fill_crumbs


def test_values_map_from_df():
    pass
    # assert not op.exists(tmp_crumb._path)
    #
    # assert not tmp_crumb.has_files()
    #
    # values_dict = {'session_id': ['session_{:02}'.format(i) for i in range( 2)],
    #                'subject_id': ['subj_{:03}'.format(i)    for i in range( 3)],
    #                'modality':   ['anat'],
    #                'image':      ['mprage1.nii', 'mprage2.nii', 'mprage3.nii'],
    #                }
    #
    # paths = mktree(tmp_crumb, list(ParameterGrid(values_dict)))
    #
    # assert op.exists(tmp_crumb.split()[0])
    #
    # assert not tmp_crumb.has_files()
    #
    # recs   = tmp_crumb.values_map('image')
    # n_recs = len(recs)
    #
    # dicts = valuesmap_to_dict(recs)
    # for arg_name in dicts:
    #     assert len(dicts[arg_name]) == n_recs
    #
    # assert values_dict == {arg_name:rm_dups(arg_values) for arg_name, arg_values in dicts.items()}
    #

def test_pandas_fill_crumbs():
    pass
