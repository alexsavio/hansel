import os
import tempfile

import pytest

from hansel import Crumb, mktree
from hansel.utils import ParameterGrid


@pytest.fixture
def crumb(request):
    crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")

    def fin():
        print("teardown crumb")

    request.addfinalizer(fin)
    return crumb  # provide the fixture value


@pytest.fixture
def tmp_crumb(request):
    crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")
    base_dir = tempfile.mkdtemp(prefix='crumbtest_')
    crumb2 = crumb.replace(base_dir=base_dir)

    def fin():
        print("teardown tmp_crumb")

    request.addfinalizer(fin)
    return crumb2  # provide the fixture value


@pytest.fixture
def tmp_tree(request):
    crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{modality}/{image}")
    base_dir = tempfile.mkdtemp(prefix='crumbtest_')
    crumb2 = crumb.replace(base_dir=base_dir)

    def fin():
        print("teardown tmp_crumb")

    request.addfinalizer(fin)

    assert not os.path.exists(crumb2._path)

    assert not crumb2.has_files()

    values_dict = {
        'session_id': ['session_{:02}'.format(i) for i in range(2)],
        'subject_id': ['subj_{:03}'.format(i) for i in range(3)],
        'modality': ['anat'],
        'image': ['mprage1.nii', 'mprage2.nii', 'mprage3.nii'],
    }

    mktree(crumb2, list(ParameterGrid(values_dict)))

    assert os.path.exists(crumb2.split()[0])

    assert not crumb2.has_files()

    return crumb2, values_dict  # provide the fixture value


@pytest.fixture(scope="module")
def values(request):
    return list(range(3))
