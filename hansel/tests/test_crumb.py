# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:


import pytest

import os
import os.path  as op
from   copy     import copy
from   pathlib  import Path

from   six      import string_types
from   hansel   import Crumb


BASE_DIR = op.expanduser('~/data/cobre')


@pytest.fixture(scope="module")
def crumb(request):

    crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")

    def fin():
        print("teardown crumb")

    request.addfinalizer(fin)
    return crumb  # provide the fixture value


def test_replace(crumb):
    base_dir = BASE_DIR
    crumb2 = crumb.replace(base_dir=base_dir)

    assert crumb2._path == op.join(base_dir, crumb._path.replace('{base_dir}/', ''))
    assert 'base_dir' not in crumb2._argidx


def test_isabs(crumb):
    base_dir = BASE_DIR
    crumb2 = crumb.replace(base_dir=base_dir)

    assert not crumb.isabs()
    assert crumb2.isabs()


def test_argidx_order(crumb):
    base_dir = BASE_DIR
    crumb2 = crumb.replace(base_dir=base_dir)

    assert sorted(list(crumb._argidx.values()))  == list(crumb._argidx.values())
    assert sorted(list(crumb2._argidx.values())) == list(crumb2._argidx.values())


def test_abspath(crumb):
    crumb2 = crumb.abspath(first_is_basedir=False)
    assert crumb2._path == op.join(op.abspath(op.curdir), crumb._path)
    assert crumb is not crumb2
    assert crumb2.isabs()
    assert crumb != crumb2

    crumb3 = crumb.abspath(first_is_basedir=True)
    assert crumb3._path == op.join(op.abspath(op.curdir), crumb._path.replace('{base_dir}/', ''))
    assert crumb is not crumb3
    assert crumb3.isabs()

    assert crumb3 != crumb2


def test_copy(crumb):
    copy = Crumb.copy(crumb)
    assert crumb is not copy
    assert crumb == copy


def test_equal_no_copy(crumb):
    crumb2 = crumb
    assert crumb2 == crumb

    crumb2._path += '/'
    assert crumb2 == crumb

    crumb2.path == op.join(crumb._path, '{test}')
    assert crumb2 == crumb


def test_equal_copy(crumb):
    crumb2 = Crumb.copy(crumb)
    assert crumb2 == crumb

    crumb2._path += '/'
    assert crumb2 != crumb

    crumb2.path == op.join(crumb._path, '{test}')
    assert crumb2 != crumb


def test_split(crumb):
    splt = crumb.split()
    for s in splt:
        if op.isdir(s):
            assert op.exists(s)
        else:
            assert Crumb._is_crumb_arg(s) or isinstance(s, string_types)


def test_is_valid_a_bit(crumb):
    assert Crumb.is_valid(crumb)

    crumb_path = crumb._path
    crumb_path = crumb_path[:3] + Crumb._arg_start_sym + crumb_path[3:-1]
    assert not Crumb.is_valid(crumb_path)


def test_has_crumbs(crumb):
    assert Crumb.has_crumbs(crumb)

    assert not Crumb.has_crumbs('')
    assert not Crumb.has_crumbs('/home/hansel/.config')


def test_ls_raises():
    crumb = Crumb(op.join('{home}', '{user_folder}'))

    pytest.raises(ValueError, crumb.ls, 'hansel')

    pytest.raises(NotImplementedError, crumb.ls, 'home')

    pytest.raises(ValueError, crumb.ls, 'user',
                  make_crumbs=True, fullpath=False)


def test_ls1():
    base_dir = op.expanduser('~')
    crumb = Crumb(op.join(base_dir, '{user_folder}'))

    lst = crumb.ls('user_folder', fullpath=False, duplicates=True, make_crumbs=False)
    assert set(lst) == set(os.listdir(base_dir))

    crumb = Crumb(op.join(base_dir, '{user_folder}', '{files}'))
    lst = crumb.ls('user_folder', fullpath=False, duplicates=True, make_crumbs=False)
    assert set(lst) == set([d for d in os.listdir(base_dir) if op.isdir(op.join(base_dir, d))])

    flst = crumb.ls('user_folder', fullpath=True, duplicates=True, make_crumbs=False)
    assert all([isinstance(f, string_types) for f in flst])
    assert all([not op.exists(f) for f in flst])

    flst = crumb.ls('files', fullpath=True, duplicates=True, make_crumbs=False)
    assert all([isinstance(f, string_types) for f in flst])
    assert all([op.exists(f) or op.islink(f) for f in flst])

    flst = crumb.ls('files', fullpath=True, duplicates=True, make_crumbs=True)
    assert all([isinstance(f, Path) for f in flst])
    assert all([f.exists() or f.is_symlink() for f in flst])

    flst = crumb.ls('user_folder', fullpath=True, duplicates=True, make_crumbs=True)
    assert all([isinstance(f, Crumb) for f in flst])
    # TODO: check if all crumbs exist
    # assert all([f.exists() or f.is_symlink() for f in flst])

    #TODO: missing test ls with duplicates=False


def test_ls3():
    from glob import glob
    base_dir = op.expanduser('~')
    files = [d for d in glob(op.join(base_dir, '*')) if op.isfile(d)]
    crumb = Crumb(op.join(files[0], '{user_folder}', '{files}'))
    lst = crumb.ls('user_folder')
    assert not lst

    lst = crumb.ls('files')
    assert not lst


def test_rem_deps(crumb):

    values = copy(crumb._argidx)
    assert not crumb._remaining_deps(values)

    del values['base_dir']
    assert crumb._remaining_deps(values) == ['base_dir']

    del values['subject_id']
    assert crumb._remaining_deps(values) == ['subject_id', 'base_dir']

    values = copy(crumb._argidx)
    del values['base_dir']
    del values['modality']
    assert crumb._remaining_deps(values) == ['modality', 'base_dir']

    values = copy(crumb._argidx)
    del values['image']
    del values['modality']
    assert not crumb._remaining_deps(values)


def test_mktree(crumb):
    pass
#     %run crumb.py
#     values_map = {'year': [str(y) for y in range(2010, 2013)],
#                   'subject_id': ['subj_' + str(i) for i in range(3)]}
#     vm = cr._recursive_values_maps(values_map)

if __name__ == '__main__':
    import os.path as op
    from tempfile import TemporaryDirectory
    from hansel import Crumb
    from hansel.utils import ParameterGrid

    crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")
    base_dir = TemporaryDirectory()
    crumb2 = crumb.replace(base_dir=base_dir.name)

    values_map = {'session_id': ['session_' + str(i) for i in range(2)],
                  'subject_id': ['subj_' + str(i) for i in range(3)]}

    crumb2.mktree(list(ParameterGrid(values_map)))


