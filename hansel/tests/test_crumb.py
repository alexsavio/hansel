# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:


import pytest

import os
import os.path  as op
import shutil
from   copy     import copy
from   pathlib  import Path
from   tempfile import TemporaryDirectory

from   six      import string_types
from   hansel   import Crumb
from   hansel.utils import ParameterGrid


BASE_DIR = op.expanduser('~/data/cobre')


@pytest.fixture
def crumb(request):

    crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")

    def fin():
        print("teardown crumb")

    request.addfinalizer(fin)
    return crumb  # provide the fixture value


@pytest.fixture(scope="module")
def tmp_crumb(request):
    from tempfile import TemporaryDirectory

    crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")
    base_dir = TemporaryDirectory(prefix='crumbtest_')
    crumb2 = crumb.replace(base_dir=base_dir.name)

    def fin():
        print("teardown tmp_crumb")
        shutil.rmtree(base_dir.name)
        #os.removedirs(base_dir.name)

    request.addfinalizer(fin)
    return crumb2  # provide the fixture value


def test__get_path(tmp_crumb):
    pytest.raises(TypeError, tmp_crumb._get_path, {})
    pytest.raises(TypeError, tmp_crumb._get_path, [])

def test_path_property(crumb):

    assert crumb.path == crumb._path

    base_dir = BASE_DIR
    crumb2 = crumb.replace(base_dir=base_dir)

    assert crumb2.path == crumb2._path
    assert crumb.path != crumb2._path
    assert crumb._argidx != crumb2._argidx

    crumb.path = crumb2.path

    assert crumb.path == crumb.path
    assert crumb._argidx == crumb2._argidx


def test_replace_and_setitem(crumb):
    base_dir = BASE_DIR
    crumb.path = op.join(crumb.path, '{hansel}', '{gretel}')

    # use replace
    crumb2 = crumb.replace(base_dir=base_dir)

    assert crumb2._path == op.join(base_dir, crumb._path.replace('{base_dir}/', ''))
    assert 'base_dir' not in crumb2._argidx

    # use setitem
    crumb3 = crumb.copy(crumb)
    crumb3['base_dir'] = base_dir

    assert crumb3._replace1(**dict()) == crumb3._path
    assert crumb3._replace2(**dict()) == crumb3._path

    assert crumb3 is not crumb2
    assert crumb3 == crumb2
    assert crumb3._path == crumb2._path
    assert 'base_dir' not in crumb3._argidx

    assert crumb3.replace(**{})._path == crumb3._path

    pytest.raises(KeyError, crumb2.replace, grimm='brothers')
    pytest.raises(KeyError, crumb2._replace1, grimm='brothers')
    pytest.raises(KeyError, crumb2._replace2, grimm='brothers')
    pytest.raises(KeyError, crumb2.__setitem__, 'grimm', 'brothers')


def test_firstarg(crumb):
    an, ai = crumb._firstarg()
    assert an == 'base_dir'
    assert ai == 0

    base_dir = BASE_DIR
    crumb2 = crumb.replace(base_dir=base_dir)

    an, ai = crumb2._firstarg()
    assert an == 'subject_id'
    assert ai == len(base_dir.split(op.sep)) + 1


def test_lastarg(crumb):
    an, ai = crumb._lastarg()
    assert an == 'image'
    assert ai == len(crumb._path_split()) - 1

    base_dir = BASE_DIR
    crumb2 = crumb.replace(base_dir=base_dir)

    an, ai = crumb2._lastarg()
    assert an == 'image'
    assert ai == len(crumb2._path_split()) - 1


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
    assert 'base_dir' in crumb2._argidx

    crumb3 = crumb.abspath(first_is_basedir=True)
    assert crumb3._path == op.join(op.abspath(op.curdir), crumb._path.replace('{base_dir}/', ''))
    assert crumb is not crumb3
    assert crumb3.isabs()

    assert crumb3 != crumb2

    assert Crumb(op.expanduser('~'))._abspath() == op.expanduser('~')

    base_dir = BASE_DIR
    crumb2 = crumb.replace(base_dir=base_dir)
    crumbc = crumb2.abspath(first_is_basedir=False)
    assert crumbc == crumb2
    assert crumbc is not crumb2


def test_copy(crumb):
    copy = Crumb.copy(crumb)
    assert crumb is not copy
    assert crumb == copy

    pytest.raises(TypeError, crumb.copy, {})


def test_equal_no_copy(crumb):
    crumb2 = crumb
    assert crumb2 == crumb

    crumb2._path += '/'
    assert crumb2 == crumb

    crumb2.path == op.join(crumb._path, '{test}')
    assert crumb2 == crumb

    crumb2._argidx['hansel'] = []
    assert crumb2 == crumb


def test_equal_copy(crumb):
    crumb2 = Crumb.copy(crumb)
    assert crumb2 == crumb

    crumb2._path += '/'
    assert crumb2 != crumb

    crumb2._path == op.join(crumb._path, '{test}')
    assert crumb2 != crumb

    crumb2._argidx['hansel'] = []
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

    assert isinstance(Crumb.from_path(Path(crumb_path)), Path)
    pytest.raises(ValueError, Crumb.from_path, crumb_path)
    pytest.raises(TypeError, crumb.from_path, {})

    assert not Crumb.is_valid(crumb_path)
    assert Crumb.is_valid(op.expanduser('~'))

    crumb._path = crumb_path
    pytest.raises(ValueError, crumb._check)
    pytest.raises(ValueError, crumb.isabs)
    pytest.raises(ValueError, crumb.abspath)


def test_arg_name(crumb):
    pytest.raises(ValueError, crumb._arg_name, 'hansel')


def test_has_crumbs(crumb):
    assert Crumb.has_crumbs(crumb)

    assert not Crumb.has_crumbs('')
    assert not Crumb.has_crumbs('/home/hansel/.config')


def test_str(crumb):
    assert crumb._path == str(crumb)


def test_ls_raises():
    crumb = Crumb(op.join('{home}', '{user_folder}'))

    pytest.raises(ValueError, crumb.ls, 'hansel')

    pytest.raises(NotImplementedError, crumb.ls, 'home')

    pytest.raises(ValueError, crumb.ls, 'user',
                  make_crumbs=True, fullpath=False)


def test_ls_and_getitem():
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

    flst1 = crumb.ls('files', fullpath=False, duplicates=False, make_crumbs=False)
    flst2 = crumb['files']
    assert all([isinstance(f, str) for f in flst1])
    assert flst1 == flst2

    flst = crumb.ls('user_folder', fullpath=True, duplicates=True, make_crumbs=True)
    assert all([isinstance(f, Crumb) for f in flst])
    # check if all crumbs exist
    assert all([c.exists() for c in flst])

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


# def test_remdeps2(tmp_crumb):
#     values_dict = {'session_id': ['session_' + str(i) for i in range(2)],
#                    'subject_id': ['subj_' + str(i) for i in range(3)],
#                    'modality':   ['anat', 'rest', 'pet'],
#                    'image':      ['mprage.nii', 'rest.nii', 'pet.nii'],
#                    }
#
#     del values_dict['subject_id']
#     del values_dict['image']
#     values_map = list(ParameterGrid(values_dict))
#
#     assert tmp_crumb._remaining_deps(['image']) == ['modality', 'base_dir']


def test_touch(tmp_crumb):
    assert not op.exists(tmp_crumb._path)
    path = tmp_crumb.touch()
    assert path == tmp_crumb.split()[0]
    assert op.exists(path)


def test__touch():
    base_dir = TemporaryDirectory()
    path = op.join(base_dir.name, 'hansel')

    assert not op.exists(path)

    nupath = Crumb._touch(path)
    assert nupath == path
    assert op.exists(nupath)

    pytest.raises(IOError, Crumb._touch, nupath, exist_ok=False)

    #pytest.raises(IOError, Crumb._touch, path + '\\', exist_ok=False)


def test_mktree1(tmp_crumb):

    assert not op.exists(tmp_crumb._path)

    nupaths = tmp_crumb.mktree(None)

    assert all([op.exists(npath) for npath in nupaths])

    pytest.raises(TypeError, tmp_crumb.mktree, 'hansel')


def test_mktree_dicts(tmp_crumb):

    assert not op.exists(tmp_crumb._path)

    values_map = {'session_id': ['session_' + str(i) for i in range(2)],
                  'subject_id': ['subj_' + str(i) for i in range(3)]}

    nupaths = tmp_crumb.mktree(list(ParameterGrid(values_map)))

    assert all([op.exists(npath) for npath in nupaths])

    values_map['grimm'] = ['Jacob', 'Wilhelm']
    pytest.raises(ValueError, tmp_crumb.mktree, list(ParameterGrid(values_map)))


def test_mktree_tuples(tmp_crumb):

    assert not op.exists(tmp_crumb._path)

    values_dict = {'session_id': ['session_' + str(i) for i in range(2)],
                   'subject_id': ['subj_' + str(i) for i in range(3)]}

    values_map = list(ParameterGrid(values_dict))
    values_tups = [tuple(d.items()) for d in values_map]

    nupaths = tmp_crumb.mktree(values_tups)

    assert all([op.exists(npath) for npath in nupaths])


def test_mktree_raises(tmp_crumb):
    assert not op.exists(tmp_crumb._path)

    values_dict = {'session_id': ['session_' + str(i) for i in range(2)],
                   'subject_id': ['subj_' + str(i) for i in range(3)],
                   'modality':   ['anat', 'rest', 'pet'],
                   'image':      ['mprage.nii', 'rest.nii', 'pet.nii'],
                   }

    del values_dict['session_id']
    del values_dict['modality']
    pytest.raises(KeyError, tmp_crumb.mktree, list(ParameterGrid(values_dict)))


def test_arg_values(tmp_crumb):
    # the most of _arg_values is being tested in test_ls
    pytest.raises(ValueError, tmp_crumb._arg_values, 'session_id')


def test_exists(tmp_crumb):
    assert not op.exists(tmp_crumb._path)

    values_map = {'session_id': ['session_' + str(i) for i in range(2)],
                  'subject_id': ['subj_' + str(i) for i in range(3)]}

    shutil.rmtree(tmp_crumb.split()[0])

    pytest.raises(IOError, tmp_crumb._arg_values, 'subject_id')
    assert not tmp_crumb.exists()

    _ = tmp_crumb.mktree(list(ParameterGrid(values_map)))

    assert tmp_crumb.exists()

    assert not Crumb._exists('/_/asdfasdfasdf?/{hansel}')


def test_repr(crumb):
    assert crumb.__repr__() == 'Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")'

if __name__ == '__main__':
    import os.path as op
    from tempfile import TemporaryDirectory
    from hansel import Crumb
    from hansel.utils import ParameterGrid

    crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")
    base_dir = TemporaryDirectory()
    crumb2 = crumb.replace(base_dir=base_dir.name)

    values_map = {'session_id': ['session_' + str(i) for i in range(2)],
                  'subject_id': ['subj_' + str(i) for i in range(3)],
                  'modality':   ['anat', 'rest', 'pet'],
                  }

    nupaths = crumb2.mktree(list(ParameterGrid(values_map)))

    assert all([op.exists(npath) for npath in nupaths])

    anat_crumb = crumb2.replace(modality='anat')

    anat_crumb.ls('subject_id')


