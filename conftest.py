import pathlib
import shutil

import pytest

from hansel.tests.conftest import make_tree_from_crumb
from hansel.utils import ParameterGrid


@pytest.fixture(scope='session')
def readme_base_dir():
    base_dir = pathlib.Path('/tmp/hansel/data')
    if base_dir.exists():
        shutil.rmtree(str(base_dir), ignore_errors=True)
        base_dir.mkdir()
    yield str(base_dir)
    shutil.rmtree(str(base_dir), ignore_errors=True)


def readme_brain_data_crumb_args():
    crumb_path = "{base_dir}/raw/{subject_id}/{session_id}/{image_type}/{image}"
    values_dict = {
        'session_id': ['session_1'],
        'subject_id': ['004000{}'.format(i) for i in range(10)],
        'image_type': ['anat_1', 'rest_1'],
        'image': ['mprage.nii.gz'],
    }
    return crumb_path, values_dict


def readme_proj1_data_crumb_args():
    crumb_path = "{base_dir}/proj1/{subject_id}/{session_id}/{image_type}/{image}"
    values_dict = {
        'session_id': ['session_1'],
        'subject_id': ['004000{}'.format(i) for i in range(10)],
        'image_type': ['anat_1', 'rest_1'],
        'image': ['mprage.nii.gz', 'rest.nii.gz'],
    }
    return crumb_path, values_dict


def readme_proj2_data_crumb_args():
    crumb_path = "{base_dir}/proj2/{subject_id}/{session_id}/{image_type}/{image}"
    values_dict = {
        'session_id': ['session_1'],
        'subject_id': ['00400{:02}'.format(i + 6) for i in range(10)],
        'image_type': ['anat_1', 'rest_1'],
        'image': ['mprage.nii.gz', 'rest.nii.gz'],
    }
    return crumb_path, values_dict


def readme_proj3_data_crumb_args():
    crumb_path = "{base_dir}/proj3/{subject_id}/{session_id}/{image_type}/{image}"
    values_dict = {
        'session_id': ['session_1'],
        'subject_id': ['00400{:02}'.format(i) for i in range(10)],
        'image_type': ['anat_1'],
        'image': ['mprage.nii.gz'],
    }
    return crumb_path, values_dict


def readme_proj4_data_crumb_args():
    crumb_path = "{base_dir}/proj4/{subject_id}/{session_id}/{image_type}/{image}"
    values_dict = {
        'session_id': ['session_1'],
        'subject_id': ['00400{:02}'.format(i + 1) for i in range(9)],
        'image_type': ['anat_1'],
        'image': ['mprage.nii.gz'],
    }

    subject1 = dict(
        image='anatomical.nii.gz',
        image_type='anat_1',
        session_id='session_1',
        subject_id='00400000'
    )

    values_map = [subject1]
    values_map.extend(list(ParameterGrid(values_dict)))
    return crumb_path, values_map


@pytest.fixture(scope='session')
def readme_tree_crumbs():
    return [
        readme_brain_data_crumb_args,
        readme_proj1_data_crumb_args,
        readme_proj2_data_crumb_args,
        readme_proj3_data_crumb_args,
        readme_proj4_data_crumb_args,
    ]


@pytest.fixture(scope='session')
def built_readme_tree_crumbs(readme_base_dir, readme_tree_crumbs):
    crumbs = []
    for crumb_func in readme_tree_crumbs:
        crumb_path, values_dict = crumb_func()
        make_tree_from_crumb(readme_base_dir, crumb_path, values_dict)
    yield crumbs
    shutil.rmtree(readme_base_dir)


@pytest.fixture(autouse=True)
def add_base_crumbs(doctest_namespace, built_readme_tree_crumbs):
    pass
