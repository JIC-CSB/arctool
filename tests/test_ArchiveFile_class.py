"""Tests for arctool.archive.ArchiveFile class."""

import os
import subprocess

from . import tmp_archive  # NOQA

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "basic", "input")


def test_archive_header_file_order():
    from arctool.archive import ArchiveFile
    assert ArchiveFile.header_file_order == ('.dtool/dtool',
                                             '.dtool/manifest.json',
                                             'README.yml')


def test_initialise_ArchiveFile():
    from arctool.archive import ArchiveFile
    archive = ArchiveFile()
    assert archive._tar_path is None
    assert archive._name is None


# Functional tests.


def test_from_tar(tmp_archive):  # NOQA
    from arctool.archive import ArchiveFile

    unzip_command = ["gunzip", tmp_archive]
    subprocess.call(unzip_command)

    tar_filename, _ = tmp_archive.rsplit('.', 1)

    archive_file = ArchiveFile.from_file(tar_filename)

    assert isinstance(archive_file, ArchiveFile)
    assert archive_file._tar_path == tar_filename

    assert 'dtool_version' in archive_file.admin_metadata
    assert archive_file.admin_metadata['name'] == 'brassica_rnaseq_reads'
    assert len(archive_file.admin_metadata['uuid']) == 36
    assert 'file_list' in archive_file.manifest


def test_from_tar_gz(tmp_archive):  # NOQA
    from arctool.archive import ArchiveFile

    archive_file = ArchiveFile.from_file(tmp_archive)

    assert isinstance(archive_file, ArchiveFile)
    assert archive_file._tar_path == tmp_archive

    assert 'dtool_version' in archive_file.admin_metadata
    assert archive_file.admin_metadata['name'] == 'brassica_rnaseq_reads'
    assert len(archive_file.admin_metadata['uuid']) == 36
    assert 'file_list' in archive_file.manifest


def test_archive_calculate_hash(tmp_archive):  # NOQA
    from arctool.archive import ArchiveFile

    archive = ArchiveFile.from_file(tmp_archive)

    actual = archive.calculate_file_hash('file1.txt')
    expected = 'a250369afb3eeaa96fb0df99e7755ba784dfd69c'

    assert actual == expected


def test_summarise_archive(tmp_archive):  # NOQA

    from arctool.archive import ArchiveFile

    archive_file = ArchiveFile.from_file(tmp_archive)
    summary = archive_file.summarise()

    assert isinstance(summary, dict)

    assert summary['n_files'] == 2
