import pytest
from pathlib import Path
from tarfile import TarInfo

from zless.archive import Archive, ReadError


@pytest.fixture
def tarball(scope="module"):
    yield Path(__file__).parent / "fixtures" / "zless-22.1.dev0.tar.gz"


def test_archive_instantiation_with_gzipped_tarball(tarball):
    ar = Archive(tarball)
    assert ar.path == tarball


def test_archive_instantiation_with_nonexistent_tarball(tarball):
    tarball = tarball.name
    with pytest.raises(FileNotFoundError):
        _ = Archive(tarball)


def test_archive_instantiation_with_invalid_tarball():
    path = Path(__file__)
    with pytest.raises(ReadError):
        _ = Archive(path)


def test_archive_content_listing(tarball):
    expected = [
        "zless-22.1.dev0/README.rst",
        "zless-22.1.dev0/pyproject.toml",
        "zless-22.1.dev0/src/zless/__init__.py",
        "zless-22.1.dev0/src/zless/__main__.py",
        "zless-22.1.dev0/setup.py",
        "zless-22.1.dev0/PKG-INFO",
    ]
    actual = [e.name for e in Archive(tarball).contents]
    assert expected == actual


def test_archive_open(tarball):
    with Archive(tarball).open() as ar:
        assert ar is not None


@pytest.mark.skip(reason="not yet implemented")
def test_read_single_archive_entry(tarball):
    # TODO: Create valid TarInfo object to pass to read()
    assert False


def test_read_single_archive_entry_using_string(tarball):
    base = "PKG-INFO"
    with open(tarball.parent / base) as fh:
        expected = fh.read()
    actual = Archive(tarball).read(f"zless-22.1.dev0/{base}")
    assert actual == expected


def test_read_nonxistent_archive_entry(tarball):
    ar = Archive(tarball)
    with pytest.raises(KeyError):
        _ = ar.read("README.rst")
