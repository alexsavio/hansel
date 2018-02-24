import pytest

import os

from hansel import mktree
from hansel.utils import ParameterGrid


def test_mktree1(tmp_crumb):
    assert not os.path.exists(tmp_crumb.split()[0])

    nupaths = mktree(tmp_crumb, None)

    assert all([os.path.exists(npath) for npath in nupaths])

    pytest.raises(TypeError, mktree, tmp_crumb, 'hansel')


def test_mktree_dicts(tmp_crumb):
    assert not os.path.exists(tmp_crumb.split()[0])

    values_map = {
        'session_id': ['session_{}'.format(i) for i in range(2)],
        'subject_id': ['subj_{}'.format(i) for i in range(3)],
        'modality': ['anat'],
        'image': ['mprage1.nii'],
    }

    nupaths = mktree(tmp_crumb, list(ParameterGrid(values_map)))

    assert all([os.path.exists(npath.split()[0]) for npath in nupaths])
    assert all([npath.exists() for npath in nupaths])

    values_map['grimm'] = ['Jacob', 'Wilhelm']
    pytest.raises(ValueError, mktree, tmp_crumb, list(ParameterGrid(values_map)))


def test_mktree_tuples(tmp_crumb):
    assert not os.path.exists(tmp_crumb.split()[0])

    values_dict = {'session_id': ['session_{:02}'.format(i) for i in range(2)],
                   'subject_id': ['subj_{:03}'.format(i) for i in range(3)],
                   'modality': ['anat'],
                   'image': ['mprage1.nii', 'mprage2.nii', 'mprage3.nii'],
                   }

    values_map = list(ParameterGrid(values_dict))
    values_tups = [tuple(d.items()) for d in values_map]

    nupaths = mktree(tmp_crumb, values_tups)

    for path in nupaths:
        for k in values_dict:
            assert k in path

    assert all([os.path.exists(npath.split()[0]) for npath in nupaths])
    assert all([npath.exists() for npath in nupaths])

    ls_session_ids = tmp_crumb.ls('session_id', fullpath=False, make_crumbs=False, check_exists=False)
    assert set(ls_session_ids) == set(values_dict['session_id'])

    ls_subj_ids = tmp_crumb.ls('subject_id', fullpath=False, make_crumbs=False, check_exists=False)
    assert set(ls_subj_ids) == set(values_dict['subject_id'])


def test_mktree_raises(tmp_crumb):
    assert not os.path.exists(tmp_crumb.split()[0])

    values_dict = {
        'session_id': ['session_' + str(i) for i in range(2)],
        'subject_id': ['subj_' + str(i) for i in range(3)],
        'modality': ['anat', 'rest', 'pet'],
        'image': ['mprage.nii', 'rest.nii', 'pet.nii'],
    }

    del values_dict['session_id']
    del values_dict['modality']
    pytest.raises(KeyError, mktree, tmp_crumb, list(ParameterGrid(values_dict)))
