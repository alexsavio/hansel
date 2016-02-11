# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

import pytest

import os.path as op
import tempfile
from   collections import Iterable, Sized
from   itertools import chain, product

from hansel.utils import (rm_dups,
                          ParameterGrid,
                          list_intersection,
                          intersection,
                          _get_matching_items,
                          )

from hansel import Crumb, mktree


@pytest.fixture(scope="module")
def values(request):
    return list(range(3))


def test_remove_duplicates(values):
    assert rm_dups(values * 10) == sorted(values)
    assert rm_dups(values) == sorted(values)
    assert rm_dups(values) == sorted(rm_dups(values))


def test_parameter_grid():
    # Taken from sklearn and converted to pytest
    # Test basic properties of ParameterGrid.

    def assert_grid_iter_equals_getitem(grid):
        assert list(grid) == [grid[i] for i in range(len(grid))]

    params1 = {"foo": [1, 2, 3]}
    grid1 = ParameterGrid(params1)
    assert isinstance(grid1, Iterable)
    assert isinstance(grid1, Sized)
    assert len(grid1) == 3
    assert_grid_iter_equals_getitem(grid1)

    params2 = {"foo": [4, 2],
               "bar": ["ham", "spam", "eggs"]}
    grid2 = ParameterGrid(params2)
    assert len(grid2) == 6

    # loop to assert we can iterate over the grid multiple times
    for i in range(2):
        # tuple + chain transforms {"a": 1, "b": 2} to ("a", 1, "b", 2)
        points = set(tuple(chain(*(sorted(p.items())))) for p in grid2)
        assert points == set(("bar", x, "foo", y)
                         for x, y in product(params2["bar"], params2["foo"]))

    assert_grid_iter_equals_getitem(grid2)

    # Special case: empty grid (useful to get default estimator settings)
    empty = ParameterGrid({})
    assert len(empty) == 1
    assert list(empty) == [{}]
    assert_grid_iter_equals_getitem(empty)
    pytest.raises(IndexError, lambda: empty[1])

    has_empty = ParameterGrid([{'C': [1, 10]}, {}, {'C': [.5]}])
    assert len(has_empty) == 4
    assert list(has_empty) == [{'C': 1}, {'C': 10}, {}, {'C': .5}]
    assert_grid_iter_equals_getitem(has_empty)


def test_list_intersection():
    sessions1 = ['session_{}'.format(r) for r in range(10)]
    sessions2 = ['session_{}'.format(r) for r in range( 5)]
    assert list(list_intersection(sessions1, sessions2)) == sessions2


def test_get_matching_items():
    sessions1 = ['session_{}'.format(r) for r in range(10)]
    sessions2 = ['session_{}'.format(r) for r in range( 5)]
    subjects2 = ['subject_{}'.format(r) for r in range( 5)]

    assert list(_get_matching_items(sessions1, subjects2)) == []

    assert list(_get_matching_items(sessions1, sessions2)) == sessions2

    assert list(_get_matching_items(sessions1, sessions2, items=['session_1'])) == ['session_1']

    assert list(_get_matching_items(sessions1, sessions2, items=['hansel'])) == []


def test_intersection():

    crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")
    base_dir1 = tempfile.mkdtemp(prefix='crumbtest1_')
    tmp_crumb1 = crumb.replace(base_dir=base_dir1)

    base_dir2 = tempfile.mkdtemp(prefix='crumbtest2_')
    tmp_crumb2 = crumb.replace(base_dir=base_dir2)

    assert not op.exists(tmp_crumb1._path)
    assert not op.exists(tmp_crumb2._path)

    assert not tmp_crumb1.has_files()
    assert not tmp_crumb2.has_files()

    values_dict1 = {'session_id': ['session_{:02}'.format(i) for i in range( 2)],
                    'subject_id': ['subj_{:03}'.format(i)    for i in range( 3)],
                    'modality':   ['anat'],
                    'image':      ['mprage1.nii', 'mprage2.nii', 'mprage3.nii'],
                    }

    values_dict2 = {'session_id': ['session_{:02}'.format(i) for i in range(20)],
                    'subject_id': ['subj_{:03}'.format(i)    for i in range(30)],
                    'modality':   ['anat'],
                    'image':      ['mprage1.nii', 'mprage2.nii', 'mprage3.nii'],
                    }

    _ = mktree(tmp_crumb1, list(ParameterGrid(values_dict1)))
    _ = mktree(tmp_crumb2, list(ParameterGrid(values_dict2)))

    assert op.exists(tmp_crumb1.split()[0])
    assert op.exists(tmp_crumb2.split()[0])

    assert intersection(tmp_crumb1, tmp_crumb2, on=['subject_id']) == [('subject_id', val) for val in tmp_crumb1['subject_id']]


    assert intersection(tmp_crumb1, tmp_crumb2,
                        on=['subject_id', 'modality']) == [(('subject_id', 'subj_000'), ('modality', 'anat')),
                                                           (('subject_id', 'subj_001'), ('modality', 'anat')),
                                                           (('subject_id', 'subj_002'), ('modality', 'anat'))]

    han_crumb = tmp_crumb2.replace(subject_id='hansel')
    assert intersection(tmp_crumb1, han_crumb, on=['subject_id']) == []

    s0_crumb = tmp_crumb2.replace(subject_id='subj_000')
    assert intersection(tmp_crumb1, s0_crumb, on=['subject_id']) == [('subject_id', 'subj_000')]

    assert intersection(tmp_crumb1, s0_crumb, on=['subject_id', 'modality']) == [(('subject_id', 'subj_000'), ('modality', 'anat'))]

    assert intersection(tmp_crumb1, s0_crumb, on=['subject_id', 'image']) == [(('subject_id', 'subj_000'), ('image', 'mprage1.nii')),
                                                                              (('subject_id', 'subj_000'), ('image', 'mprage2.nii')),
                                                                              (('subject_id', 'subj_000'), ('image', 'mprage3.nii'))]

    # test raises
    pytest.raises(KeyError, intersection, tmp_crumb1, tmp_crumb2, on=['hansel'])

    pytest.raises(KeyError, intersection, tmp_crumb1, tmp_crumb2, on=['subject_id', 'modality', 'hansel'])

    pytest.raises(KeyError, intersection, tmp_crumb1, Crumb(op.expanduser('~/{files}')))

    pytest.raises(KeyError, intersection, tmp_crumb1, Crumb(op.expanduser('~/{files}')), on=['files'])

