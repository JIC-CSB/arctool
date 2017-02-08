"""Test fixtures."""

import os
import shutil
import tempfile
from distutils.dir_util import copy_tree
import contextlib

import pytest

from dtool import DescriptiveMetadata

_HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(_HERE, "data", "basic", "input")

TEST_DESCRIPTIVE_METADATA = DescriptiveMetadata([
    ("project_name", u"my_project"),
    ("dataset_name", u"brassica_rnaseq_reads"),
    ("confidential", False),
    ("personally_identifiable_information", False),
    ("owner_name", u"Your Name"),
    ("owner_email", u"your.email@example.com"),
    ("unix_username", u"namey"),
    ("archive_date", u"2017-01-01"),
])


@contextlib.contextmanager
def remember_cwd():
    cwd = os.getcwd()
    try:
        yield
    finally:
        os.chdir(cwd)


@pytest.fixture
def chdir_fixture(request):
    d = tempfile.mkdtemp()
    curdir = os.getcwd()
    os.chdir(d)

    @request.addfinalizer
    def teardown():
        os.chdir(curdir)
        shutil.rmtree(d)


@pytest.fixture
def tmp_dir_fixture(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d


@pytest.fixture
def local_tmp_dir_fixture(request):
    d = tempfile.mkdtemp(dir=_HERE)

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d


@pytest.fixture
def tmp_archive(request):

    from arctool.archive import (
        ArchiveDataSet,
        ArchiveFileBuilder)

    from arctool.archive import compress_archive

    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)

    archive_directory_path = os.path.join(d, "brassica_rnaseq_reads")
    os.mkdir(archive_directory_path)
    archive_ds = ArchiveDataSet("brassica_rnaseq_reads")
    archive_ds.persist_to_path(archive_directory_path)

    # Move some data into the archive.
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(archive_directory_path, 'archive')
    copy_tree(archive_input_path, archive_output_path)

    archive_builder = ArchiveFileBuilder.from_path(archive_directory_path)
    tar_path = archive_builder.persist_to_tar(d)
    compress_archive(tar_path)

    return tar_path + '.gz'
