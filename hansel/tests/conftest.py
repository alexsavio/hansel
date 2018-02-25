import os
import tempfile
import shutil
from typing import Dict

import pytest

from hansel import Crumb, mktree
from hansel.utils import ParameterGrid, CrumbArgsSequences


@pytest.fixture
def crumb():
    yield Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")


@pytest.fixture
def tmp_crumb(base_dir):
    crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")
    yield crumb.replace(base_dir=base_dir)


@pytest.fixture
def base_dir():
    yield tempfile.mkdtemp(prefix='crumbtest_')


@pytest.fixture
def brain_data_crumb_args():
    crumb_path = "{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}"

    values_dict = {
        'session_id': ['session_{:02}'.format(i) for i in range(2)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(3)],
        'modality': ['anat'],
        'image': ['mprage1.nii', 'mprage2.nii', 'mprage3.nii'],
    }
    yield crumb_path, values_dict


def make_tree_from_crumb(base_path, crumb_path, crumb_args: [Dict, CrumbArgsSequences]):
    crumb = Crumb(crumb_path)
    crumb2 = crumb.replace(base_dir=base_path)

    assert not os.path.exists(crumb2._path)
    assert not crumb2.has_files()

    if isinstance(crumb_args, dict):
        values_map = list(ParameterGrid(crumb_args))
    elif isinstance(crumb_args, list):
        values_map = crumb_args
    else:
        raise TypeError('Expected `crumb_args` to be dict or list, got {}.'.format(type(crumb_args)))

    mktree(crumb2, values_map)
    assert os.path.exists(crumb2.split()[0])
    assert not crumb2.has_files()
    return crumb2


@pytest.fixture
def tmp_tree_crumb(base_dir, brain_data_crumb_args):
    crumb_path, values_dict = brain_data_crumb_args
    yield make_tree_from_crumb(base_dir, crumb_path, values_dict)
    shutil.rmtree(base_dir)
