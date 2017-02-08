"""Tests for dtool.archive.ArchiveFileBuilder class."""

import os
from distutils.dir_util import copy_tree
import json
import shutil
import subprocess
import tempfile

import pytest

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "basic", "input")


@pytest.fixture
def tmp_dir(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d


def test_archive_header_file_order():
    from dtool.archive import ArchiveFileBuilder
    assert ArchiveFileBuilder.header_file_order == ('.dtool/dtool',
                                                    '.dtool/manifest.json',
                                                    'README.yml')

# Functional tests.


def test_ArchiveFileBuilder_from_path(tmp_dir):
    from dtool.archive import ArchiveDataSet, ArchiveFileBuilder

    archive_ds = ArchiveDataSet("my_archive")
    archive_ds.persist_to_path(tmp_dir)

    archive_builder = ArchiveFileBuilder.from_path(tmp_dir)
    assert archive_ds == archive_builder._archive_dataset


def test_create_archive(tmp_dir):
    from dtool.archive import ArchiveDataSet, ArchiveFileBuilder

    # Create separate directory for archive so that tarball
    # is created outside of it.
    archive_directory_path = os.path.join(tmp_dir, "input")
    os.mkdir(archive_directory_path)

    archive_ds = ArchiveDataSet("my_archive")
    archive_ds.persist_to_path(archive_directory_path)

    # Move some data into the archive.
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(archive_directory_path, 'archive')
    copy_tree(archive_input_path, archive_output_path)

    archive_builder = ArchiveFileBuilder.from_path(archive_directory_path)
    tar_path = archive_builder.persist_to_tar(tmp_dir)

    expected_tar_file_path = os.path.join(tmp_dir, "my_archive.tar")
    assert expected_tar_file_path == archive_builder._tar_path
    assert expected_tar_file_path == tar_path

    assert os.path.isfile(expected_tar_file_path)

    # Move the original input data into a new directory.
    reference_data_path = os.path.join(tmp_dir, "expected")
    os.rename(archive_directory_path, reference_data_path)
    assert not os.path.isdir(archive_directory_path)

    # Untar the tarball just created.
    cmd = ["tar", "-xf", expected_tar_file_path]
    subprocess.check_call(cmd, cwd=tmp_dir)

    # Test that the archive has been re-instated by untaring.
    assert os.path.isdir(archive_directory_path)

    # Test order of files in tarball.

    cmd = ["tar", "-tf", expected_tar_file_path]
    output = subprocess.check_output(cmd)

    split_output = output.split()

    expected_first_header_file = os.path.join(
        'input',
        ArchiveFileBuilder.header_file_order[0])

    assert split_output[0].decode("utf-8") == expected_first_header_file

    for n, filename in enumerate(ArchiveFileBuilder.header_file_order):
        expected_filename = os.path.join('input', filename)
        assert split_output[n].decode("utf-8") == expected_filename

    from dtool import generate_relative_paths
    untarred_file_set = set(generate_relative_paths(archive_directory_path))
    reference_file_set = set(generate_relative_paths(reference_data_path))
    assert untarred_file_set == reference_file_set

    # Test correctness of manifest

    manifest_path = os.path.join(
        archive_directory_path, '.dtool', 'manifest.json')
    with open(manifest_path) as fh:
        manifest = json.load(fh)

    assert len(manifest['file_list']) == 2
