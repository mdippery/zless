import tarfile
import zipfile
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Generator, Optional, Protocol, Sequence, Union, cast


class BadArchive(Exception):
    pass


class FileInfo(Protocol):
    @property
    def name(self) -> str:
        ...


class Archive(Protocol):
    @property
    def contents(self) -> Sequence[FileInfo]:
        ...

    def read(self, entry: FileInfo) -> str:
        ...


FileEntry = Union[str, FileInfo]
FilePath = Union[str, Path]


class TarArchive:
    def __init__(self, path: FilePath) -> None:
        assert tarfile.is_tarfile(path)
        self.path = path

    @property
    def contents(self) -> Sequence[FileInfo]:
        with self.open() as tarball:
            return tarball.getmembers()

    @contextmanager
    def open(self) -> Generator[tarfile.TarFile, None, None]:
        with tarfile.open(self.path) as tarball:
            yield tarball

    # TODO: Handle attempt to read binary file
    def read(self, entry: FileEntry) -> str:
        with self.open() as tarball:
            data = tarball.extractfile(entry)
            if data is None:
                raise BadArchive(f"{self.path} has no entry: {entry}")
            return data.read().decode("utf-8")


class ZipFileInfo:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    @property
    def name(self) -> str:
        return self.wrapped.filename


class ZipArchive:
    def __init__(self, path) -> None:
        assert zipfile.is_zipfile(path)
        self.path = path
        # TODO: Use context manager
        self._zip = zipfile.ZipFile(path)

    @property
    def contents(self) -> Sequence[FileInfo]:
        return [ZipFileInfo(e) for e in self._zip.infolist()]

    def read(self, entry: FileEntry) -> str:
        if isinstance(entry, FileInfo):
            entry = entry.name
        with self._zip.open(entry) as zip_:
            return zip_.read().decode("utf-8")

    def __del__(self):
        try:
            self._zip.close()
        except AttributeError:
            pass


def archive(path: FilePath) -> Archive:
    if tarfile.is_tarfile(path):
        return TarArchive(path)
    if zipfile.is_zipfile(path):
        return ZipArchive(path)
    raise BadArchive(f"Could not open archive: {path}")
