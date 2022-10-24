import tarfile
import zipfile
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Generator, Optional, Protocol, Sequence, Union, cast, runtime_checkable


class BadArchive(Exception):
    pass


@runtime_checkable
class FileInfo(Protocol):
    @property
    def name(self) -> str:
        ...


FileEntry = Union[str, FileInfo]
FilePath = Union[str, Path]


class Archive:
    def __new__(cls, path):
        if tarfile.is_tarfile(path):
            cls = TarArchive
        elif zipfile.is_zipfile(path):
            cls = ZipArchive
        else:
            raise BadArchive(f"Could not open archive: {path}")
        self = object.__new__(cls)
        cls.__init__(self, path)
        return self

    @property
    def contents(self) -> Sequence[FileInfo]:
        raise NotImplementedError("Subclasses must implement")

    def read(self, entry: FileInfo) -> str:
        raise NotImplementedError("Subclasses must implement")


class TarArchive(Archive):
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


class ZipArchive(Archive):
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
