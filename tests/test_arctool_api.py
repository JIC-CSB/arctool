"""Test the archtool module api."""

import os
import json
from distutils.dir_util import copy_tree
import tarfile

import yaml
import magic

from arctool.archive import ArchiveFileBuilder

from . import TEST_INPUT_DATA
from . import TEST_DESCRIPTIVE_METADATA
from . import tmp_dir_fixture  # NOQA
from . import tmp_archive  # NOQA


def create_archive(path):
    """Create archive from path using tar.

    :param path: path to archive in staging area
    :returns: path to created tarball
    """

    archive_builder = ArchiveFileBuilder.from_path(path)
    output_path = os.path.join(path, "..")
    return archive_builder.persist_to_tar(output_path)


def test_archive_fixture(tmp_archive):  # NOQA

    mimetype = magic.from_file(tmp_archive, mime=True)

    assert mimetype == 'application/x-gzip'


def test_new_archive_dataset(tmp_dir_fixture):  # NOQA
    from arctool.utils import new_archive_dataset

    dataset, dataset_path, _ = new_archive_dataset(tmp_dir_fixture,
                                                   TEST_DESCRIPTIVE_METADATA)

    expected_path = os.path.join(tmp_dir_fixture,
                                 "brassica_rnaseq_reads")
    expected_path = os.path.abspath(expected_path)
    assert dataset_path == expected_path
    assert os.path.isdir(dataset_path)

    expected_dataset_file = os.path.join(dataset_path, ".dtool", "dtool")
    assert os.path.isfile(expected_dataset_file)

    readme_yml_path = os.path.join(tmp_dir_fixture,
                                   "brassica_rnaseq_reads",
                                   "README.yml")
    assert os.path.isfile(readme_yml_path)

    readme_txt_path = os.path.join(tmp_dir_fixture,
                                   "brassica_rnaseq_reads",
                                   "archive",
                                   "README.txt")
    assert os.path.isfile(readme_txt_path)

    # Test that .dtool-dataset file is valid
    with open(expected_dataset_file, 'r') as fh:
        dataset_info = json.load(fh)

    assert "dtool_version" in dataset_info
    assert "uuid" in dataset_info
    assert "creator_username" in dataset_info
    assert dataset_info["manifest_root"] == "archive"
    assert dataset_info['name'] == 'brassica_rnaseq_reads'

    # Test that yaml is valid.
    with open(readme_yml_path, "r") as fh:
        readme_data = yaml.load(fh)
    assert readme_data["dataset_name"] == "brassica_rnaseq_reads"

    # Also assert that confidential and personally_identifiable_information
    # are set to False by default.
    assert not readme_data["confidential"]
    assert not readme_data["personally_identifiable_information"]


def test_readme_yml_is_valid(mocker):
    from arctool.utils import readme_yml_is_valid
    # Not that the log function get imported into the dtool.arctool namespace
    from arctool.utils import log  # NOQA

    patched_log = mocker.patch("arctool.utils.log")

    assert not readme_yml_is_valid("")
    patched_log.assert_called_with("README.yml invalid: empty file")

    # This should be ok.
    assert readme_yml_is_valid("""---
project_name: some_project
dataset_name: data_set_1
confidential: False
personally_identifiable_information: False
owners:
  - name: Some One
    email: ones@example.com
archive_date: 2016-01-12
""")

    # Missing a project name.
    assert not readme_yml_is_valid("""---
dataset_name: data_set_1
confidential: False
personally_identifiable_information: False
owners:
  - name: Some One
    email: ones@example.com
archive_date: 2016-01-12
""")
    patched_log.assert_called_with("README.yml is missing: project_name")

    # Invalid date.
    assert not readme_yml_is_valid("""---
project_name: some_project
dataset_name: data_set_1
confidential: False
personally_identifiable_information: False
owners: NA
archive_date: some day
""")
    patched_log.assert_called_with(
        "README.yml invalid: archive_date is not a date")

    # Owners is not a list.
    assert not readme_yml_is_valid("""---
project_name: some_project
dataset_name: data_set_1
confidential: False
personally_identifiable_information: False
owners: NA
archive_date: 2016-01-12
""")
    patched_log.assert_called_with("README.yml invalid: owners is not a list")

    # An owner needs a name.
    assert not readme_yml_is_valid("""---
project_name: some_project
dataset_name: data_set_1
confidential: False
personally_identifiable_information: False
owners:
  - name: Some One
    email: ones@example.com
  - email: twos@example.com
archive_date: 2016-01-12
""")
    patched_log.assert_called_with(
        "README.yml invalid: owner is missing a name")

    # An owner needs an email.
    assert not readme_yml_is_valid("""---
project_name: some_project
dataset_name: data_set_1
confidential: False
personally_identifiable_information: False
owners:
  - name: Some One
    email: ones@example.com
  - name: Another Two
archive_date: 2016-01-12
""")
    patched_log.assert_called_with(
        "README.yml invalid: owner is missing an email")


def test_new_archive_dataset_input_descriptive_metadata(tmp_dir_fixture):  # NOQA
    from dtool import DescriptiveMetadata
    from arctool.utils import new_archive_dataset

    metadata = DescriptiveMetadata([("project_name", "some_project"),
                                    ("dataset_name", "data_set_1")])
    new_archive_dataset(tmp_dir_fixture, metadata)

    # Test file creation.
    readme_yml_path = os.path.join(tmp_dir_fixture,
                                   "data_set_1",
                                   "README.yml")
    assert os.path.isfile(readme_yml_path)

    # Test that yaml is valid.
    with open(readme_yml_path, "r") as fh:
        readme_data = yaml.load(fh)
    assert readme_data["project_name"] == "some_project"
    assert readme_data["dataset_name"] == "data_set_1"


def test_create_archive(tmp_dir_fixture):  # NOQA
    from arctool.utils import new_archive_dataset

    dataset, path, readme_path = new_archive_dataset(
        tmp_dir_fixture, TEST_DESCRIPTIVE_METADATA)
    tmp_project = os.path.join(tmp_dir_fixture, "brassica_rnaseq_reads")
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_project, 'archive')
    copy_tree(archive_input_path, archive_output_path)

    dataset.update_manifest()

    create_archive(tmp_project)

    expected_tar_filename = os.path.join(
        tmp_dir_fixture, 'brassica_rnaseq_reads.tar')
    assert os.path.isfile(expected_tar_filename)

    # Test that all expected files are present in archive
    expected = set([  # 'brassica_rnaseq_reads',
                      'brassica_rnaseq_reads/.dtool/dtool',
                      'brassica_rnaseq_reads/.dtool/manifest.json',
                      'brassica_rnaseq_reads/archive',
                      'brassica_rnaseq_reads/README.yml',
                      'brassica_rnaseq_reads/archive/README.txt',
                      'brassica_rnaseq_reads/archive/dir1',
                      'brassica_rnaseq_reads/archive/file1.txt',
                      'brassica_rnaseq_reads/archive/dir1/file2.txt'])

    actual = set()
    with tarfile.open(expected_tar_filename, 'r') as tar:
        for tarinfo in tar:
            actual.add(tarinfo.path)

    assert len(expected) == len(actual)
    assert expected == actual, (expected, actual)

    # Test that order of critical files is correct
    expected = ['brassica_rnaseq_reads/.dtool/dtool',
                'brassica_rnaseq_reads/.dtool/manifest.json',
                'brassica_rnaseq_reads/README.yml',
                ]

    actual = []
    with tarfile.open(expected_tar_filename, 'r') as tar:
        for tarinfo in tar:
            actual.append(tarinfo.path)

    for e, a in zip(expected, actual):
        assert e == a
