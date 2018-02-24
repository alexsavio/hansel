import pytest

import os
import shutil
import tempfile

try:
    from pathlib2 import Path
except ImportError:
    from pathlib import Path

from hansel import Crumb, mktree
from hansel.utils import ParameterGrid
from hansel._utils import (
    _get_path,
    _arg_names,
    _depth_names,
    _check,
    _touch,
    _split,
    _is_crumb_arg,
    _split_exists,
)

from hansel.tests.conftest import tmp_crumb


BASE_DIR = os.path.expanduser('~/data/cobre')


def test__get_path(tmp_crumb):
    pytest.raises(TypeError, _get_path, {})
    pytest.raises(TypeError, _get_path, [])

    assert _get_path(tmp_crumb) == tmp_crumb._path
    assert tmp_crumb._path != tmp_crumb.path


def test_path_property(crumb):
    assert crumb.path == crumb._path

    base_dir = BASE_DIR
    crumb2 = crumb.replace(base_dir=base_dir)

    assert crumb._path == crumb2._path
    assert crumb.path == crumb2._path
    assert crumb.path != crumb2.path
    assert list(crumb.open_args()) != list(crumb2.open_args())
    assert set(crumb.all_args()) == set(crumb2.all_args())

    crumb.path = crumb2.path
    assert crumb.path == crumb.path
    assert list(crumb.open_args()) == list(crumb2.open_args())
    assert list(crumb.all_args()) != list(crumb2.all_args())


def test_copy_string(crumb):
    crumb2 = crumb.copy(crumb._path)
    assert crumb2 == crumb


def test_copy_equal(crumb):
    crumb2 = crumb.copy(crumb._path)
    assert crumb2 == crumb

    crumb3 = crumb.copy(crumb)
    assert crumb3 == crumb

    crumb3.set_pattern('image', 'anat*')
    assert crumb3 != crumb

    crumb4 = crumb3.copy()
    assert crumb4 == crumb3
    assert crumb4.patterns == crumb3.patterns

    crumb4['image'] = 'anat.nii.gz'
    crumb5 = crumb4.copy(crumb4.path)
    assert crumb5 != crumb4
    assert crumb5.patterns != crumb4.patterns

    crumb6 = crumb4.copy(crumb4._path)
    assert crumb6 != crumb4
    assert crumb6.patterns == crumb4.patterns


def test_replace_and_setitem(crumb):
    # crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")
    args = list(_arg_names(crumb.path))
    assert list(crumb.open_args()) == args
    assert list(crumb.all_args()) == args

    base_dir = BASE_DIR
    crumb.path = os.path.join(crumb.path, '{hansel}', '{gretel}')
    args.extend(['hansel', 'gretel'])

    assert not crumb.has_set('base_dir')

    # use replace
    crumb2 = crumb.replace(base_dir=base_dir)
    assert list(crumb2.open_args()) == args[1:]
    args.pop(0)
    assert list(crumb2.open_args()) == args
    assert list(crumb2.all_args()) != args

    assert crumb2.path == os.path.join(base_dir, crumb._path.replace('{base_dir}/', ''))
    assert 'base_dir' not in crumb2.open_args()
    assert 'base_dir' in crumb2.all_args()
    assert 'base_dir' in crumb2._argval

    assert crumb2['base_dir'][0] == base_dir
    assert crumb2.has_set('base_dir')

    # use setitem
    crumb3 = crumb.copy(crumb)
    crumb3['base_dir'] = base_dir

    assert crumb3.replace(**dict()).path == crumb3.path
    # assert crumb3._replace1(**dict()) == crumb3._path
    # assert crumb3._replace2(**dict()) == crumb3._path

    assert crumb3 is not crumb2
    assert crumb3 == crumb2
    assert crumb3.path == crumb2.path
    assert crumb3.has_set('base_dir')

    assert crumb3.replace(**{}).path == crumb3.path

    pytest.raises(KeyError, crumb2.replace, grimm='brothers')
    pytest.raises(KeyError, crumb2.__setitem__, 'grimm', 'brothers')
    pytest.raises(ValueError, crumb2.replace, subject_id=[])


def test_firstarg(crumb):
    ai, an = crumb._first_open_arg()
    assert an == 'base_dir'
    assert ai == 0

    base_dir = BASE_DIR
    crumb2 = crumb.replace(base_dir=base_dir)

    ai, an = crumb2._first_open_arg()
    assert an == 'subject_id'
    assert ai == len(base_dir.split(os.path.sep)) + 1


def test_lastarg(crumb):
    ai, an = crumb._last_open_arg()
    assert an == 'image'
    assert ai == len(crumb.path.split('/')) - 1

    base_dir = BASE_DIR
    crumb2 = crumb.replace(base_dir=base_dir)

    ai, an = crumb2._last_open_arg()
    assert an == 'image'
    assert ai == len(crumb2.path.split('/')) - 1


def test_isabs(crumb):
    base_dir = BASE_DIR
    crumb2 = crumb.replace(base_dir=base_dir)

    assert not crumb.isabs()
    assert crumb2.isabs()


def test_argnames_order(crumb):
    base_dir = BASE_DIR
    crumb2 = crumb.replace(base_dir=base_dir)

    assert sorted(list(_depth_names(crumb.path))) == list(_depth_names(crumb.path))
    assert sorted(list(_depth_names(crumb2.path))) == list(_depth_names(crumb2.path))

    assert [arg_name for depth, arg_name in sorted(list(_depth_names(crumb2.path)))] == list(_arg_names(crumb2.path))


def test_abspath(crumb):
    crumb2 = crumb.abspath(first_is_basedir=False)
    assert crumb2._path == os.path.join(os.path.abspath(os.path.curdir), crumb._path)
    assert crumb is not crumb2
    assert crumb2.isabs()
    assert crumb != crumb2
    assert 'base_dir' in set(_arg_names(crumb2.path))

    crumb3 = crumb.abspath(first_is_basedir=True)
    assert crumb3._path == os.path.join(os.path.abspath(os.path.curdir), crumb._path.replace('{base_dir}/', ''))
    assert crumb is not crumb3
    assert crumb3.isabs()

    assert crumb3 != crumb2

    home_crumb = Crumb(os.path.expanduser('~'), ignore_list=['a*'])
    assert home_crumb._abspath() == os.path.expanduser('~')

    abs_home_crumb = home_crumb.abspath()
    assert abs_home_crumb._ignore == ['a*']
    assert abs_home_crumb._ignore == home_crumb._ignore

    abs_home_crumb = home_crumb.abspath()
    assert abs_home_crumb._ignore == ['a*']
    assert abs_home_crumb._ignore == home_crumb._ignore

    base_dir = BASE_DIR
    crumb2 = crumb.replace(base_dir=base_dir)
    crumbc = crumb2.abspath(first_is_basedir=False)
    assert crumbc == crumb2
    assert crumbc is not crumb2


def test_abspath2():
    # do a real test with user folder and ignore_list
    import getpass
    username = getpass.getuser()
    user_folder = os.path.join('{base}', username)
    old_dir = os.getcwd()
    os.chdir(os.path.join(os.path.expanduser('~'), '..'))
    home_crumb = Crumb(user_folder, ignore_list=['a*'])
    assert home_crumb._abspath(first_is_basedir=True) == os.path.expanduser('~')

    abs_home_crumb = home_crumb.abspath()
    assert abs_home_crumb._ignore == ['a*']
    assert abs_home_crumb._ignore == home_crumb._ignore

    os.chdir(old_dir)


def test_copy(crumb):
    copy = Crumb.copy(crumb)
    assert crumb is not copy
    assert crumb == copy

    copy2 = crumb.copy()
    assert crumb is not copy2
    assert crumb == copy2

    assert copy is not copy2

    pytest.raises(TypeError, crumb.copy, {})


def test_equal_no_copy(crumb):
    crumb2 = crumb
    assert crumb2 == crumb

    crumb2._path += '/'
    assert crumb2 == crumb

    crumb2.path == os.path.join(crumb._path, '{test}')
    assert crumb2 == crumb

    crumb2._argval['hansel'] = 'hello'
    assert crumb2 == crumb


def test_equal_copy(crumb):
    crumb2 = Crumb.copy(crumb)
    assert crumb2 == crumb

    crumb2._argval['hansel'] = 'hello'
    assert crumb2 != crumb

    crumb2._path += '/'
    assert crumb2 != crumb

    crumb2._path == os.path.join(crumb._path, '{test}')
    assert crumb2 != crumb

    crumb2._argval['hansel'] = 'hello'
    assert crumb2 != crumb

    crumb3 = Crumb(crumb.path, ignore_list=['.*'])
    assert crumb3 != crumb


def test_split(crumb):
    splt = crumb.split()
    for s in splt:
        if os.path.isdir(s):
            assert os.path.exists(s)
        else:
            assert _is_crumb_arg(s) or isinstance(s, str)


def test_split2():
    cr = Crumb('/home/hansel/data/{subj}/{session}/anat.nii')
    assert cr.split() == ('/home/hansel/data', '{subj}/{session}/anat.nii')

    cr = Crumb('{base}/home/hansel/data/{subj}/{session}/anat.nii')
    assert cr.split() == ('', cr.path)

    cr = Crumb('/home/hansel/data/subj/session/anat.nii')
    assert cr.split() == (cr.path, '')

    notvalid_crumb = '/home/hansel/data/{subj_notvalidcrumb/{session}/anat.nii'
    pytest.raises(ValueError, _split, notvalid_crumb)


def test_from_path(crumb):
    cr = Crumb.copy(crumb)
    assert cr is not crumb
    assert cr == crumb

    cr2 = crumb.from_path(crumb)
    assert cr2 is not crumb
    assert cr2 == crumb

    assert cr2 is not cr
    assert cr2 == cr

    cr2 = Crumb.from_path(Path(crumb.path))
    assert cr2 is not crumb
    assert cr2 == crumb

    assert cr2 is not cr
    assert cr2 == cr


def test_is_valid_a_bit(crumb):
    assert crumb.is_valid()

    crumb_path = crumb._path
    crumb_path = crumb_path[:3] + '{' + crumb_path[3:-1]

    pytest.raises(ValueError, Crumb.from_path, crumb_path)
    pytest.raises(TypeError, crumb.from_path, {})

    assert not crumb.is_valid(crumb_path)
    assert crumb.is_valid(os.path.expanduser('~'))

    crumb._path = crumb_path
    pytest.raises(ValueError, _check, crumb_path)
    pytest.raises(ValueError, crumb.isabs)
    pytest.raises(ValueError, crumb.abspath)

    pytest.raises(TypeError, _check, tmp_crumb)
    pytest.raises(TypeError, _check, {})
    pytest.raises(TypeError, _check, None)


def test_arg_name():
    assert not _is_crumb_arg(Path(os.path.expanduser('~')))


def test_has_crumbs(crumb):
    assert crumb.has_crumbs()

    assert not crumb.has_crumbs('')
    assert not crumb.has_crumbs('/home/hansel/.config')


def test_str(crumb):
    assert crumb._path == str(crumb)


def test_ls_raises():
    crumb = Crumb(os.path.join('{home}', '{user_folder}'))

    pytest.raises(KeyError, crumb.ls, 'hansel')

    pytest.raises(NotImplementedError, crumb.ls, 'home')

    crumb['home'] = os.path.expanduser('~')

    pytest.raises(ValueError, crumb.ls, '', fullpath=False)


def test_ls_and_getitem():
    base_dir = os.path.expanduser('~')
    crumb = Crumb(os.path.join(base_dir, '{user_folder}'))

    lst = crumb.ls('user_folder', fullpath=False, make_crumbs=False, check_exists=False)
    assert set(lst) == set(os.listdir(base_dir))

    crumb = Crumb(os.path.join(base_dir, '{user_folder}', '{files}'))
    lst = crumb.ls('user_folder', fullpath=False, make_crumbs=False, check_exists=False)
    assert set(lst) == set([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))])

    flst = crumb.ls('user_folder', fullpath=True, make_crumbs=False, check_exists=False)
    assert all([isinstance(f, str) for f in flst])
    assert all([not os.path.exists(f) for f in flst])

    flst = crumb.ls('files', fullpath=True, make_crumbs=False, check_exists=False)
    assert all([isinstance(f, str) for f in flst])
    assert all([os.path.exists(f) or os.path.islink(f) for f in flst])

    flst = crumb.ls('files', fullpath=True, make_crumbs=True, check_exists=False)
    assert all([f.exists() or f.is_symlink() for f in flst])

    flst1 = crumb.ls('files', fullpath=False, make_crumbs=False, check_exists=True)
    flst2 = crumb['files']
    assert all([isinstance(f, str) for f in flst1])
    assert flst1 == flst2


def test_ls3():
    from glob import glob
    base_dir = os.path.expanduser('~')
    files = [d for d in glob(os.path.join(base_dir, '*')) if os.path.isfile(d)]
    crumb = Crumb(os.path.join(files[0], '{user_folder}', '{files}'))
    lst = crumb.ls('user_folder')
    assert not lst

    lst = crumb.ls('files')
    assert not lst


def test_ignore_lst():
    import fnmatch

    base_dir = os.path.expanduser('~')
    crumb = Crumb(os.path.join(base_dir, '{user_folder}', '{files}'))

    folders = crumb['user_folder']  # set(fnmatch.filter(crumb['user_folder'], '.*'))

    ign_crumb = Crumb(os.path.join(base_dir, '{user_folder}', '{files}'), ignore_list=('.*',))
    ign_folders = ign_crumb['user_folder']
    assert set(ign_folders) == set([item for item in folders if not fnmatch.fnmatch(item, '.*')])
    assert set(folders) > set(ign_folders)

    uign_crumb = ign_crumb.unfold()
    assert ign_crumb._re_method == uign_crumb[0]._re_method
    assert ign_crumb._ignore == uign_crumb[0]._ignore


def test_rem_deps(crumb):
    values = {arg: dpth for dpth, arg in _depth_names(crumb.path)}
    assert not crumb._args_open_parents(values)

    del values['base_dir']
    assert crumb._args_open_parents(values) == ['base_dir']

    del values['subject_id']
    assert crumb._args_open_parents(values) == ['base_dir', 'subject_id']

    values = {arg: dpth for dpth, arg in _depth_names(crumb.path)}
    del values['base_dir']
    del values['modality']
    assert crumb._args_open_parents(values) == ['base_dir', 'modality']

    values = {arg: dpth for dpth, arg in _depth_names(crumb.path)}
    del values['image']
    del values['modality']
    assert not crumb._args_open_parents(values)


def test_touch(tmp_crumb):
    assert not os.path.exists(tmp_crumb.split()[0])
    path = tmp_crumb.touch()
    assert path == tmp_crumb.split()[0]
    assert os.path.exists(path)


def test_touch2():
    base_dir = tempfile.mkdtemp()
    path = os.path.join(base_dir, 'hansel')

    assert not os.path.exists(path)

    nupath = _touch(path)
    assert nupath == path
    assert os.path.exists(nupath)

    assert _touch(nupath, exist_ok=True) == nupath

    pytest.raises(IOError, _touch, nupath, exist_ok=False)

    pytest.raises(Exception, _touch, '/usr/lib/hansel_will_be_here_sometime', exist_ok=True)


def test_arg_values(tmp_crumb):
    # the most of _arg_values is being tested in test_ls
    pytest.raises(ValueError, tmp_crumb._arg_values, 'session_id')


def test_exists(tmp_crumb):
    assert not os.path.exists(tmp_crumb.split()[0])

    values_dict = {
        'session_id': ['session_{:02}'.format(i) for i in range(2)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(3)],
        'modality': ['anat'],
        'image': ['mprage1.nii', 'mprage2.nii', 'mprage3.nii'],
    }

    assert not tmp_crumb.exists()

    mktree(tmp_crumb, list(ParameterGrid(values_dict)))

    assert tmp_crumb.exists()

    assert not _split_exists('/_/asdfasdfasdf?/{hansel}')


def test_exists2(tmp_crumb):
    assert not os.path.exists(tmp_crumb.split()[0])

    values_dict = {
        'session_id': ['session_{:02}'.format(i) for i in range(2)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(3)],
    }

    mktree(tmp_crumb, list(ParameterGrid(values_dict)))

    assert not tmp_crumb.exists()


def test_setitem(tmp_crumb):
    assert not os.path.exists(tmp_crumb.split()[0])

    values_dict = {
        'session_id': ['session_{:02}'.format(i) for i in range(2)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(3)],
        'modality': ['anat'],
        'image': ['mprage1.nii', 'mprage2.nii', 'mprage3.nii'],
    }

    assert not tmp_crumb.exists()

    mktree(tmp_crumb, list(ParameterGrid(values_dict)))

    cr = list(tmp_crumb.ls())[0]

    assert not list(cr.open_args())

    assert cr['image'] == [values_dict['image'][0]]

    cr['image'] = 'mprage2.nii'

    assert cr['image'] == ['mprage2.nii']

    assert 'mprage2.nii' in cr.path
    assert 'mprage2.nii' in cr.ls()[0].path

    cr.clear('image')
    assert 'image' in list(cr.open_args())
    assert 'mprage2.nii' not in cr.path
    assert 'mprage2.nii' not in cr.ls()[0].path


def test_contains(tmp_crumb):
    assert 'modality' in tmp_crumb
    assert 'subject_id' in tmp_crumb
    assert 'image' in tmp_crumb
    assert 'raw' not in tmp_crumb

    tmp_crumb['image'] = 'image'

    assert 'image' in tmp_crumb.all_args()
    assert 'image' not in dict(_depth_names(tmp_crumb.path))
    assert 'image' not in tmp_crumb.open_args()
    assert tmp_crumb.has_set('image')


def test_ls_with_check(tmp_crumb):
    assert not os.path.exists(tmp_crumb._path)

    values_dict = {
        'session_id': ['session_{:02}'.format(i) for i in range(2)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(3)],
        'modality': ['anat'],
        'image': ['mprage1.nii', 'mprage2.nii', 'mprage3.nii'],
    }

    paths = mktree(tmp_crumb, list(ParameterGrid(values_dict)))

    sbj_crumb = tmp_crumb.replace(subject_id='subj_000')
    assert sbj_crumb.ls('subject_id', make_crumbs=False, fullpath=False) == ['subj_000']

    assert os.path.exists(tmp_crumb.split()[0])

    assert all([os.path.exists(p.path) for p in paths])
    assert all([p.exists() for p in paths])

    images = tmp_crumb.ls('image', fullpath=True, make_crumbs=True, check_exists=True)

    modalities = tmp_crumb.ls('modality', fullpath=True, make_crumbs=True, check_exists=True)

    assert all([img.exists() for img in images])
    assert all([mod.exists() for mod in modalities])

    Path(str(images[0])).rmdir()

    images2 = tmp_crumb.ls('image', fullpath=True, make_crumbs=True, check_exists=True)

    assert images != images2
    assert len(images) == len(images2) + 1
    assert not all([img.exists() for img in images])
    assert all([img.exists() for img in images2])

    Path(str(images[1])).rmdir()
    Path(str(images[2])).rmdir()

    images2 = tmp_crumb.ls('image', fullpath=True, make_crumbs=True, check_exists=True)

    assert tmp_crumb.ls('image') == tmp_crumb.ls()
    assert tmp_crumb.ls() == tmp_crumb.unfold()

    assert not all([img.exists() for img in images])
    assert all([img.exists() for img in images2])

    modalities2 = tmp_crumb.ls('modality', fullpath=True, make_crumbs=True, check_exists=True)

    str_modalities2 = tmp_crumb.ls('modality', fullpath=True, make_crumbs=False, check_exists=True)

    assert images != images2
    assert len(images) == len(images2) + 3

    assert modalities != modalities2
    assert not all([mod.exists() for mod in modalities])
    assert all([mod.exists() for mod in modalities2])

    assert all([isinstance(smod, str) for smod in str_modalities2])
    assert all([isinstance(mod, Crumb) for mod in modalities2])
    assert all([mod.path == smod for mod, smod in zip(sorted(modalities2), sorted(str_modalities2))])

    shutil.rmtree(modalities2[0].split()[0], ignore_errors=True)

    modalities3 = tmp_crumb.ls('modality', fullpath=True, make_crumbs=True, check_exists=True)

    assert modalities2 != modalities3
    assert not all([mod.exists() for mod in modalities2])
    assert all([mod.exists() for mod in modalities3])

    assert tmp_crumb.unfold() == tmp_crumb.ls('image', fullpath=True, make_crumbs=True, check_exists=True)

    pytest.raises(IOError, modalities2[0].__getitem__, 'image')

    img_crumb = tmp_crumb.replace(image='mprage1.nii')
    assert 'image' in img_crumb._argval
    assert img_crumb['image'] == ['mprage1.nii']

    assert img_crumb['image'][0] == img_crumb.get_first('image')

    img_crumb['modality'] = 'anat'
    assert 'modality' in img_crumb._argval
    assert img_crumb['modality'] == ['anat']
    assert img_crumb.has_set('modality')

    assert img_crumb['session_id'].count('session_01') == img_crumb['session_id'].count('session_00')

    img_crumb['session_id'] = 'session_00'
    assert 'session_id' in img_crumb._argval
    assert img_crumb['session_id'] == ['session_00']

    assert 'subj_000' not in img_crumb['subject_id']

    unfolded_crumbs = tmp_crumb.unfold()
    assert list(unfolded_crumbs[0].open_args()) == []
    assert unfolded_crumbs[0].unfold() == [unfolded_crumbs[0]]

    pytest.raises(AttributeError, unfolded_crumbs[0]._check_open_args, ['subject_id'])


def test_regex(tmp_crumb):
    assert not os.path.exists(tmp_crumb.path)

    values_dict = {
        'session_id': ['session_{:02}'.format(i) for i in range(2)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(100)],
        'modality': ['anat'],
        'image': ['mprage1.nii'],
    }

    mktree(tmp_crumb, list(ParameterGrid(values_dict)))

    crumb = Crumb(tmp_crumb.path.replace('{subject_id}', '{subject_id:^subj_02.*$}'), regex='re')  # re.match

    re_subj_ids = crumb['subject_id']

    assert re_subj_ids == ['subj_{:03}'.format(i) for i in range(20, 30)]
    assert crumb.ls('subject_id:^subj_02.*$') == crumb.ls('subject_id')

    crumb = Crumb(tmp_crumb.path.replace('{subject_id}', '{subject_id:subj_02*}'), regex='fnmatch')  # fnmatch

    fn_subj_ids = crumb['subject_id']

    assert fn_subj_ids == re_subj_ids
    cr_bkp = crumb.copy()
    assert crumb.ls('subject_id:subj_02*') == crumb.ls('subject_id')
    assert crumb['subject_id'][0] == crumb.get_first('subject_id')
    assert crumb.patterns['subject_id'] == cr_bkp.patterns['subject_id']

    assert not crumb.ls('subject_id:subj_03*') == crumb.ls('subject_id')
    assert crumb.patterns['subject_id'] == cr_bkp.patterns['subject_id']

    pytest.raises(ValueError,
                  Crumb,
                  tmp_crumb.path.replace('{subject_id}', '{subject_id:subj_02*}'),
                  regex='hansel')

    crumb2 = Crumb.copy(crumb)
    assert crumb2._re_method == crumb._re_method
    assert crumb2._re_args == crumb._re_args
    assert crumb2.patterns == crumb.patterns

    assert len(crumb2.patterns) == 1
    assert 'subject_id' in crumb2.patterns.keys()


def test_regex_ignorecase(tmp_crumb):
    assert not os.path.exists(tmp_crumb._path)

    values_dict = {
        'session_id': ['session_{:02}'.format(i) for i in range(2)],
        'subject_id': ['SUBJ_{:03}'.format(i) for i in range(100)],
        'modality': ['anat'],
        'image': ['mprage1.nii'],
    }

    mktree(tmp_crumb, list(ParameterGrid(values_dict)))

    crumb = Crumb(tmp_crumb.path.replace('{subject_id}', '{subject_id:^subj_02.*$}'), regex='re')  # re.match

    assert len(crumb['subject_id']) == 0
    assert crumb._re_method == crumb.replace(subject_id='haensel')._re_method
    assert crumb._ignore == crumb.replace(subject_id='haensel')._ignore

    assert not crumb.unfold()

    crumb = Crumb(tmp_crumb.path.replace('{subject_id}', '{subject_id:^subj_02.*$}'), regex='re.ignorecase')  # re.match
    assert crumb._re_method == crumb.replace(subject_id='haensel')._re_method
    assert crumb._ignore == crumb.replace(subject_id='haensel')._ignore

    ucrumb = crumb.unfold()[0]
    assert crumb._re_method == ucrumb._re_method
    assert crumb._ignore == ucrumb._ignore

    re_subj_ids = crumb['subject_id']

    assert re_subj_ids == ['SUBJ_{:03}'.format(i) for i in range(20, 30)]


def test_regex_replace(tmp_crumb):
    assert not os.path.exists(tmp_crumb._path)

    values_dict = {
        'session_id': ['session_{:02}'.format(i) for i in range(2)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(100)],
        'modality': ['anat'],
        'image': ['mprage1.nii'],
    }

    mktree(tmp_crumb, list(ParameterGrid(values_dict)))

    crumb = Crumb(tmp_crumb.path.replace('{subject_id}', '{subject_id:subj_02*}'), regex='fnmatch')  # fnmatch

    assert tmp_crumb.ls('subject_id:subj_02*', make_crumbs=False) == crumb.ls('subject_id', make_crumbs=False)

    anat_crumb = crumb.replace(modality='anat')
    assert anat_crumb.exists()

    fn_subj_ids = {cr['subject_id'][0] for cr in anat_crumb.ls('session_id', check_exists=True)}

    assert fn_subj_ids == set(['subj_{:03}'.format(i) for i in range(20, 30)])

    sessions = {cr['session_id'][0] for cr in anat_crumb.ls('session_id', check_exists=True)}
    assert sessions == set(values_dict['session_id'])


def test_regex_replace2(tmp_crumb):
    assert not os.path.exists(tmp_crumb.path)

    values_dict = {
        'session_id': ['session_{:02}'.format(i) for i in range(2)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(100)],
        'modality': ['anat'],
        'image': ['mprage1.nii'],
    }

    mktree(tmp_crumb, list(ParameterGrid(values_dict)))

    # a crumb with the pattern
    crumb = Crumb(tmp_crumb.path.replace('{subject_id}', '{subject_id:subj_02*}'),
                  regex='fnmatch')  # fnmatch

    # a crumb without the pattern, the pattern is added later
    crumb2 = Crumb(tmp_crumb.path, regex='fnmatch')

    crumb2.set_pattern('subject_id', 'subj_02*')
    assert crumb['subject_id'] == crumb2['subject_id']

    crumb2.clear_pattern('subject_id')
    assert tmp_crumb['subject_id'] == crumb2['subject_id']


def test_set_patterns(tmp_crumb):
    assert not os.path.exists(tmp_crumb.path)

    values_dict = {'session_id': ['session_{:02}'.format(i) for i in range(2)],
                   'subject_id': ['subj_{:03}'.format(i) for i in range(100)],
                   'modality': ['anat'],
                   'image': ['mprage1.nii'],
                   }

    mktree(tmp_crumb, list(ParameterGrid(values_dict)))

    # a crumb without the pattern, the pattern is added later
    crumb2 = Crumb(tmp_crumb.path, regex='fnmatch')

    crumb3 = crumb2.copy()
    crumb3.set_patterns()
    assert crumb2 == crumb3

    pytest.raises(KeyError, crumb2.set_patterns, somekey='somevalue')

    crumb3.set_pattern('subject_id', 'subj_02*')
    crumb2.set_patterns(subject_id='subj_02*')
    assert crumb2['subject_id'] == crumb3['subject_id']


def test_has_files(tmp_crumb):
    assert not os.path.exists(tmp_crumb.path)

    assert not tmp_crumb.has_files()

    values_dict = {
        'session_id': ['session_{:02}'.format(i) for i in range(2)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(3)],
        'modality': ['anat'],
        'image': ['mprage1.nii', 'mprage2.nii', 'mprage3.nii'],
    }

    paths = mktree(tmp_crumb, list(ParameterGrid(values_dict)))

    assert os.path.exists(tmp_crumb.split()[0])

    assert not tmp_crumb.has_files()

    pa = Path(str(paths[0]))
    pa.rmdir()
    pa.touch()

    assert pa.exists()
    assert pa.is_file()
    assert tmp_crumb.has_files()


def test_repr(crumb):
    assert crumb.__repr__() == 'Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")'


def test_joinpath(tmp_crumb):
    nupath = os.path.join('hansel', 'gretel')
    nucrumb = tmp_crumb.joinpath(nupath)
    assert os.path.join(tmp_crumb.path, nupath) == nucrumb.path
    assert 'hansel' not in nucrumb

    nupath = os.path.join('{hansel}', '{gretel}')
    nucrumb = tmp_crumb.joinpath(nupath)
    assert os.path.join(tmp_crumb.path, nupath) == nucrumb.path
    assert 'hansel' in nucrumb


def test_lt(tmp_crumb):
    tst1 = tmp_crumb < tmp_crumb
    tst2 = tmp_crumb.path < tmp_crumb.path
    assert (not tst1)
    assert tst1 == tst2

    tmp_crumb2 = Crumb.copy(tmp_crumb)
    tst1 = tmp_crumb2 < tmp_crumb2
    tst2 = tmp_crumb2.path < tmp_crumb2.path
    assert (not tst1)
    assert tst1 == tst2

    tmp_crumb2 = tmp_crumb2.joinpath('hansel')
    tst1 = tmp_crumb2 < tmp_crumb2
    tst2 = tmp_crumb2.path < tmp_crumb2.path
    assert (not tst1)
    assert tst1 == tst2

    tmp_crumb._path = os.path.sep + 'aaalex' + tmp_crumb2._path
    tst1 = tmp_crumb < tmp_crumb2
    tst2 = tmp_crumb._path < tmp_crumb2._path
    assert (tst1)
    assert tst1 == tst2

    tmp_crumb._path = os.path.sep + 'zealous' + tmp_crumb2._path
    tst1 = tmp_crumb < tmp_crumb2
    tst2 = tmp_crumb._path < tmp_crumb2._path
    assert (not tst1)
    assert tst1 == tst2

    assert tmp_crumb >= tmp_crumb2
    assert not tmp_crumb <= tmp_crumb2

    assert tmp_crumb > tmp_crumb2
    assert not tmp_crumb < tmp_crumb2
