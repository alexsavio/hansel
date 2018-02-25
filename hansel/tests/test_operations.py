import os
import tempfile
from functools import partial

import pytest

from hansel import Crumb, mktree
from hansel.utils import ParameterGrid, rm_dups
from hansel.operations import (
    intersection,
    difference,
    crumb_copy,
    crumb_link,
    append_dict_values,
    valuesmap_to_dict,
    groupby_pattern,
)


def test_valuesmap_to_dict_raises(tmp_tree_crumb):
    tmp_crumb = tmp_tree_crumb

    recs = tmp_crumb.values_map('image')

    recs[1] = recs[1][:-1]

    pytest.raises(KeyError, valuesmap_to_dict, recs)

    pytest.raises(IndexError, valuesmap_to_dict, {})

    pytest.raises(
        KeyError,
        append_dict_values,
        [dict(rec) for rec in recs],
        keys=['subject_id', 'session_id', 'hansel']
    )


def test_valuesmap_to_dict(tmp_tree_crumb, brain_data_crumb_args):
    tmp_crumb = tmp_tree_crumb
    values_dict = brain_data_crumb_args[1]

    recs = tmp_crumb.values_map('image')
    n_recs = len(recs)

    dicts = valuesmap_to_dict(recs)
    for arg_name in dicts:
        assert len(dicts[arg_name]) == n_recs

    assert values_dict == {arg_name: rm_dups(arg_values) for arg_name, arg_values in dicts.items()}

    key_subset = ['subject_id', 'session_id']
    dicts2 = append_dict_values([dict(rec) for rec in recs], keys=key_subset)

    for key in key_subset:
        assert dicts2[key] == dicts[key]

    assert tmp_crumb.values_map('image') == tmp_crumb.values_map()


def test_intersection():
    crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")
    base_dir1 = tempfile.mkdtemp(prefix='crumbtest1_')
    tmp_crumb1 = crumb.replace(base_dir=base_dir1)

    base_dir2 = tempfile.mkdtemp(prefix='crumbtest2_')
    tmp_crumb2 = crumb.replace(base_dir=base_dir2)

    assert not os.path.exists(tmp_crumb1._path)
    assert not os.path.exists(tmp_crumb2._path)

    assert not tmp_crumb1.has_files()
    assert not tmp_crumb2.has_files()

    values_dict1 = {
        'session_id': ['session_{:02}'.format(i) for i in range(2)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(3)],
        'modality': ['anat'],
        'image': ['mprage1.nii', 'mprage2.nii', 'mprage3.nii'],
    }

    values_dict2 = {
        'session_id': ['session_{:02}'.format(i) for i in range(20)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(30)],
        'modality': ['anat'],
        'image': ['mprage1.nii', 'mprage2.nii', 'mprage3.nii'],
    }

    mktree(tmp_crumb1, list(ParameterGrid(values_dict1)))
    mktree(tmp_crumb2, list(ParameterGrid(values_dict2)))

    assert os.path.exists(tmp_crumb1.split()[0])
    assert os.path.exists(tmp_crumb2.split()[0])

    assert intersection(tmp_crumb1, tmp_crumb2, on=['subject_id']) == [(('subject_id', val),) for val in
                                                                       tmp_crumb1['subject_id']]

    assert intersection(tmp_crumb1, tmp_crumb2, on=['subject_id', 'modality']) == [
        (('subject_id', 'subj_000'), ('modality', 'anat')),
        (('subject_id', 'subj_001'), ('modality', 'anat')),
        (('subject_id', 'subj_002'), ('modality', 'anat'))]

    han_crumb = tmp_crumb2.replace(subject_id='hansel')
    assert intersection(tmp_crumb1, han_crumb, on=['subject_id']) == []

    s0_crumb = tmp_crumb2.replace(subject_id='subj_000')
    assert intersection(tmp_crumb1, s0_crumb, on=['subject_id']) == [(('subject_id', 'subj_000'),)]

    assert intersection(tmp_crumb1, s0_crumb, on=['subject_id', 'modality']) == [
        (('subject_id', 'subj_000'), ('modality', 'anat'))]

    assert intersection(tmp_crumb1, s0_crumb, on=['subject_id', 'image']) == [
        (('subject_id', 'subj_000'), ('image', 'mprage1.nii')),
        (('subject_id', 'subj_000'), ('image', 'mprage2.nii')),
        (('subject_id', 'subj_000'), ('image', 'mprage3.nii'))]

    # test raises
    pytest.raises(KeyError, intersection, tmp_crumb1, tmp_crumb2, on=['hansel'])

    pytest.raises(KeyError, intersection, tmp_crumb1, tmp_crumb2, on=['subject_id', 'modality', 'hansel'])

    pytest.raises(KeyError, intersection, tmp_crumb1, Crumb(os.path.expanduser('~/{files}')))

    pytest.raises(KeyError, intersection, tmp_crumb1, Crumb(os.path.expanduser('~/{files}')), on=['files'])


def test_difference():
    crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")
    base_dir1 = tempfile.mkdtemp(prefix='crumbtest1_')
    tmp_crumb1 = crumb.replace(base_dir=base_dir1)

    base_dir2 = tempfile.mkdtemp(prefix='crumbtest2_')
    tmp_crumb2 = crumb.replace(base_dir=base_dir2)

    assert not os.path.exists(tmp_crumb1._path)
    assert not os.path.exists(tmp_crumb2._path)

    assert not tmp_crumb1.has_files()
    assert not tmp_crumb2.has_files()

    values_dict1 = {
        'session_id': ['session_{:02}'.format(i) for i in range(4)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(5)],
        'modality': ['anat'],
        'image': ['mprage1.nii', 'mprage2.nii', 'mprage3.nii'],
    }

    values_dict2 = {
        'session_id': ['session_{:02}'.format(i) for i in range(2)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(3)],
        'modality': ['anat'],
        'image': ['mprage1.nii', 'mprage2.nii', 'mprage3.nii'],
    }

    mktree(tmp_crumb1, list(ParameterGrid(values_dict1)))
    mktree(tmp_crumb2, list(ParameterGrid(values_dict2)))

    assert os.path.exists(tmp_crumb1.split()[0])
    assert os.path.exists(tmp_crumb2.split()[0])

    n_extra_subjs = len(values_dict1['subject_id']) - len(values_dict2['subject_id'])
    assert difference(tmp_crumb1, tmp_crumb2, on=['subject_id']) == [
        (('subject_id', val),) for val in values_dict1['subject_id'][-n_extra_subjs:]
    ]

    assert difference(tmp_crumb1, tmp_crumb2, on=['subject_id', 'modality']) == [
        (('subject_id', 'subj_003'), ('modality', 'anat')),
        (('subject_id', 'subj_004'), ('modality', 'anat')),
    ]

    han_crumb = tmp_crumb2.replace(subject_id='hansel')
    assert difference(tmp_crumb1, han_crumb, on=['subject_id']) == [
        (('subject_id', val),) for val in values_dict1['subject_id']
    ]

    s0_crumb = tmp_crumb2.replace(subject_id='subj_000')
    assert difference(tmp_crumb1, s0_crumb, on=['subject_id']) == [
        (('subject_id', val),) for val in values_dict1['subject_id'][1:]
    ]

    assert difference(tmp_crumb1, s0_crumb, on=['subject_id', 'modality']) == [
        (('subject_id', 'subj_001'), ('modality', 'anat')),
        (('subject_id', 'subj_002'), ('modality', 'anat')),
        (('subject_id', 'subj_003'), ('modality', 'anat')),
        (('subject_id', 'subj_004'), ('modality', 'anat'))
    ]

    # test raises
    pytest.raises(KeyError, difference, tmp_crumb1, tmp_crumb2, on=['hansel'])

    pytest.raises(KeyError, difference, tmp_crumb1, tmp_crumb2,
                  on=['subject_id', 'modality', 'hansel'])

    pytest.raises(KeyError, difference, tmp_crumb1,
                  Crumb(os.path.expanduser('~/{files}')))

    pytest.raises(KeyError, difference, tmp_crumb1,
                  Crumb(os.path.expanduser('~/{files}')),
                  on=['files'])


def test_group_pattern():
    crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{image}")
    base_dir1 = tempfile.mkdtemp(prefix='crumbtest1_')
    tmp_crumb1 = crumb.replace(base_dir=base_dir1)

    assert not os.path.exists(tmp_crumb1._path)
    assert not tmp_crumb1.has_files()

    values_dict1 = {
        'session_id': ['session_{:02}'.format(i) for i in range(2)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(3)],
        'image': ['mprage.nii', 'pet.nii', 'rest.nii', 'remaining'],
    }

    mktree(tmp_crumb1, list(ParameterGrid(values_dict1)))

    patterns = {'anat': 'mprage*',
                'pet': 'pet*',
                'rest': 'rest*',
                }

    matches = groupby_pattern(tmp_crumb1, 'image', patterns)

    assert patterns.keys() == matches.keys()

    for name, paths in matches.items():
        assert len(paths) == 6
        for p in paths:
            assert isinstance(p, Crumb)
            assert patterns[name] in p.patterns.values()


def _test_crumb_copy(make_links=False):
    crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{image}")
    base_dir1 = tempfile.mkdtemp(prefix='crumb_copy_test1_')
    tmp_crumb1 = crumb.replace(base_dir=base_dir1)

    assert not os.path.exists(tmp_crumb1._path)
    assert not tmp_crumb1.has_files()

    values_dict1 = {
        'session_id': ['session_{:02}'.format(i) for i in range(2)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(3)],
        'image': ['mprage.nii', 'pet.nii', 'rest.nii', 'remaining'],
    }

    mktree(tmp_crumb1, list(ParameterGrid(values_dict1)))

    base_dir2 = tempfile.mkdtemp(prefix='crumb_copy_test2_')
    tmp_crumb2 = crumb.replace(base_dir=base_dir2)

    if make_links:
        copy_func = crumb_link
    else:
        copy_func = crumb_copy

    # make first copy
    copy_func(tmp_crumb1, tmp_crumb2)
    assert all([cr.exists() for cr in tmp_crumb2.ls()])

    # copy again without exist_ok
    pytest.raises(IOError, copy_func, tmp_crumb1, tmp_crumb2)
    assert all([cr.exists() for cr in tmp_crumb2.ls()])

    # copy again with exist_ok
    copy_func(tmp_crumb1, tmp_crumb2, exist_ok=True)
    assert all([cr.exists() for cr in tmp_crumb2.ls()])

    if make_links:
        assert all([os.path.islink(cr.path) for cr in tmp_crumb2.ls()])


test_crumb_copy = partial(_test_crumb_copy, make_links=False)
test_crumb_copy_make_link_dirs = partial(_test_crumb_copy, make_links=True)
