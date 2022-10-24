import pytest
from pathlib import Path
from tarfile import TarInfo

from zless.archive import BadArchive, archive


class ArchiveTestSuite:
    def test_archive_instantiation_with_nonexistent_archive(self, path):
        path = path.name
        with pytest.raises(FileNotFoundError):
            _ = archive(path)

    def test_archive_instantiation_with_invalid_archive(self):
        path = Path(__file__)
        with pytest.raises(BadArchive):
            _ = archive(path)

    def test_archive_content_listing(self, path, contents):
        actual = [e.name for e in archive(path).contents]
        assert actual == contents

    @pytest.mark.skip(reason="not yet implemented")
    def test_read_single_archive_entry(self, path):
        # TODO: Create valid TarInfo object to pass to read()
        assert False

    def test_read_single_archive_entry_using_string(self, path, unarchived_file):
        base = unarchived_file.name
        with open(path.parent / base) as fh:
            expected = fh.read()
        actual = archive(path).read(str(unarchived_file))
        assert actual == expected

    def test_read_nonxistent_archive_entry(self, path):
        ar = archive(path)
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

    @pytest.fixture(scope="class")
    def unarchived_file(self):
        return Path("zless-22.1.dev0") / "PKG-INFO"

    def test_archive_open(self, path):
        with archive(path).open() as ar:
            assert ar is not None


class TestGzippedTarball(TarballTestSuite):
    @pytest.fixture(scope="class")
    def path(self):
        yield Path(__file__).parent / "fixtures" / "zless-22.1.dev0.tar.gz"

    def test_archive_instantiation_with_gzipped_tarball(self, path):
        ar = archive(path)
        assert ar.path == path
        assert ar.path.suffix == ".gz"


class TestTarball(TarballTestSuite):
    @pytest.fixture(scope="class")
    def path(self):
        yield Path(__file__).parent / "fixtures" / "zless-22.1.dev0.tar"

    def test_archive_instantiation_with_tarball(self, path):
        ar = archive(path)
        assert ar.path == path
        assert ar.path.suffix == ".tar"


class TestZip(ArchiveTestSuite):
    @pytest.fixture(scope="class")
    def contents(self):
        yield [
            "zless/__init__.py",
            "zless/__main__.py",
            "zless-22.1.dev0.dist-info/entry_points.txt",
            "zless-22.1.dev0.dist-info/WHEEL",
            "zless-22.1.dev0.dist-info/METADATA",
            "zless-22.1.dev0.dist-info/RECORD",
        ]

    @pytest.fixture(scope="class")
    def unarchived_file(self):
        yield Path("zless-22.1.dev0.dist-info") / "WHEEL"

    @pytest.fixture(scope="class")
    def path(self):
        yield Path(__file__).parent / "fixtures" / "zless-22.1.dev0-py3-none-any.whl"

    def test_archive_instantiation_with_zipfile(self, path):
        ar = archive(path)
        assert ar.path == path
        assert ar.path.suffix == ".whl"
