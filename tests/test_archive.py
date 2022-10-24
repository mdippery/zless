import pytest
from pathlib import Path
from tarfile import TarInfo

from zless.archive import Archive, ReadError


class ArchiveTestSuite:
    def test_archive_content_listing(self, path, contents):
        actual = [e.name for e in Archive(path).contents]
        assert actual == contents

    def test_archive_open(self, path):
        with Archive(path).open() as ar:
            assert ar is not None

    @pytest.mark.skip(reason="not yet implemented")
    def test_read_single_archive_entry(self, path):
        # TODO: Create valid TarInfo object to pass to read()
        assert False

    def test_read_single_archive_entry_using_string(self, path):
        base = "PKG-INFO"
        with open(path.parent / base) as fh:
            expected = fh.read()
        actual = Archive(path).read(f"zless-22.1.dev0/{base}")
        assert actual == expected

    def test_read_nonxistent_archive_entry(self, path):
        ar = Archive(path)
        with pytest.raises(KeyError):
            _ = ar.read("README.rst")


class TarballTestSuite(ArchiveTestSuite):
    @pytest.fixture(scope="class")
    def contents(self):
        yield [
            "zless-22.1.dev0/README.rst",
            "zless-22.1.dev0/pyproject.toml",
            "zless-22.1.dev0/src/zless/__init__.py",
            "zless-22.1.dev0/src/zless/__main__.py",
            "zless-22.1.dev0/setup.py",
            "zless-22.1.dev0/PKG-INFO",
        ]

    def test_archive_instantiation_with_gzipped_tarball(self, path):
        ar = Archive(path)
        assert ar.path == path

    def test_archive_instantiation_with_nonexistent_tarball(self, path):
        path = path.name
        with pytest.raises(FileNotFoundError):
            _ = Archive(path)

    def test_archive_instantiation_with_invalid_tarball(self):
        path = Path(__file__)
        with pytest.raises(ReadError):
            _ = Archive(path)


class TestGzippedTarball(TarballTestSuite):
    @pytest.fixture(scope="class")
    def path(self):
        yield Path(__file__).parent / "fixtures" / "zless-22.1.dev0.tar.gz"


class TestTarball(TarballTestSuite):
    @pytest.fixture(scope="class")
    def path(self):
        yield Path(__file__).parent / "fixtures" / "zless-22.1.dev0.tar"
