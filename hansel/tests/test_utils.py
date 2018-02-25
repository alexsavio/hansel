from collections import Iterable, Sized
from itertools import chain, product

import pytest

from hansel.utils import (
    rm_dups,
    ParameterGrid,
    list_intersection,
    _get_matching_items,
)


def test_remove_duplicates():
    values = list(range(3))

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

    params2 = {
        "foo": [4, 2],
        "bar": ["ham", "spam", "eggs"]
    }
    grid2 = ParameterGrid(params2)
    assert len(grid2) == 6

    # loop to assert we can iterate over the grid multiple times
    for i in range(2):
        # tuple + chain transforms {"a": 1, "b": 2} to ("a", 1, "b", 2)
        points = set(tuple(chain(*(sorted(p.items())))) for p in grid2)
        assert points == set(
            ("bar", x, "foo", y) for x, y in product(params2["bar"], params2["foo"])
        )

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
    sessions2 = ['session_{}'.format(r) for r in range(5)]
    assert list(list_intersection(sessions1, sessions2)) == sessions2


def test_get_matching_items():
    sessions1 = ['session_{}'.format(r) for r in range(10)]
    sessions2 = ['session_{}'.format(r) for r in range(5)]
    subjects2 = ['subject_{}'.format(r) for r in range(5)]

    assert list(_get_matching_items(sessions1, subjects2)) == []

    assert list(_get_matching_items(sessions1, sessions2)) == sessions2

    assert list(_get_matching_items(sessions1, sessions2, items=['session_1'])) == ['session_1']

    assert list(_get_matching_items(sessions1, sessions2, items=sessions2)) == sessions2

    assert list(_get_matching_items(sessions1, sessions2, items=['hansel'])) == []
