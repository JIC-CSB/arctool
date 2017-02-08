"""Test the archive module."""

import os
import subprocess

from . import tmp_archive  # NOQA


def test_compress_archive(tmp_archive):  # NOQA

    from arctool.archive import compress_archive

    tar_filename, _ = tmp_archive.rsplit('.', 1)
    expected_gz_filename = tar_filename + '.gz'
    expected_gz_filename = os.path.abspath(expected_gz_filename)

    unzip_command = ["gunzip", tmp_archive]
    subprocess.call(unzip_command)
    assert os.path.isfile(tar_filename)
    assert not os.path.isfile(expected_gz_filename)

    gzip_filename = compress_archive(tar_filename)

    assert gzip_filename == expected_gz_filename
    assert os.path.isfile(expected_gz_filename)
    assert not os.path.isfile(tar_filename)


def test_archive_verify_all(tmp_archive):  # NOQA
    from arctool.archive import ArchiveFile

    archive_file = ArchiveFile.from_file(tmp_archive)
    assert archive_file.verify_all()


def test_verify_file(tmp_archive):  # NOQA
    from arctool.archive import ArchiveFile

    archive_file = ArchiveFile.from_file(tmp_archive)

    assert archive_file.verify_file('file1.txt')

    archive_file._manifest["file_list"][0]["hash"] = "nonsense"
    assert not archive_file.verify_file('file1.txt')
