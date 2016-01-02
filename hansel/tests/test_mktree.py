# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

import pytest

import os.path  as op

from   hansel   import mktree
from   hansel.utils import ParameterGrid

from test_crumb import tmp_crumb


def test_mktree1(tmp_crumb):

    assert not op.exists(tmp_crumb.split()[0])

    nupaths = mktree(tmp_crumb, None)

    assert all([op.exists(npath) for npath in nupaths])

    pytest.raises(TypeError, mktree, tmp_crumb, 'hansel')


def test_mktree_dicts(tmp_crumb):

    assert not op.exists(tmp_crumb.split()[0])

    values_map = {'session_id': ['session_' + str(i) for i in range(2)],
                  'subject_id': ['subj_' + str(i) for i in range(3)]}

    nupaths = mktree(tmp_crumb, list(ParameterGrid(values_map)))

    assert all([op.exists(npath) for npath in nupaths])

    values_map['grimm'] = ['Jacob', 'Wilhelm']
    pytest.raises(ValueError, mktree, tmp_crumb, list(ParameterGrid(values_map)))


def test_mktree_tuples(tmp_crumb):

    assert not op.exists(tmp_crumb.split()[0])

    session_ids = ['session_' + str(i) for i in range(2)]
    subj_ids = ['subj_' + str(i) for i in range(3)]
    values_dict = {'session_id': session_ids,
                   'subject_id': subj_ids}

    values_map = list(ParameterGrid(values_dict))
    values_tups = [tuple(d.items()) for d in values_map]

    nupaths = mktree(tmp_crumb, values_tups)

    assert all([op.exists(npath) for npath in nupaths])

    ls_session_ids = tmp_crumb.ls('session_id',
                                  fullpath     = False,
                                  rm_dups      = True,
                                  make_crumbs  = False,
                                  check_exists = False)
    assert ls_session_ids == session_ids

    ls_subj_ids = tmp_crumb.ls('subject_id',
                               fullpath     = False,
                               rm_dups      = True,
                               make_crumbs  = False,
                               check_exists = False)
    assert ls_subj_ids == subj_ids


def test_mktree_raises(tmp_crumb):
    assert not op.exists(tmp_crumb.split()[0])

    values_dict = {'session_id': ['session_' + str(i) for i in range(2)],
                   'subject_id': ['subj_' + str(i) for i in range(3)],
                   'modality':   ['anat', 'rest', 'pet'],
                   'image':      ['mprage.nii', 'rest.nii', 'pet.nii'],
                   }

    del values_dict['session_id']
    del values_dict['modality']
    pytest.raises(KeyError, mktree, tmp_crumb, list(ParameterGrid(values_dict)))

