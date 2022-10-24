import tarfile
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Generator, Optional, Protocol, Sequence, Union, cast


class ReadError(Exception):
    pass


FileEntry = Union[tarfile.TarInfo, str]
FilePath = Union[str, Path]


class FileInfo(Protocol):
    @property
    def name(self) -> str:
        ...


class WrappedArchive(Protocol):
    def getmembers(self) -> Sequence[FileInfo]:
        ...

    def extractfile(self, entry: FileEntry) -> IO[bytes]:
        ...


class WrappedTarArchive:
    def __init__(self, wrapped: tarfile.TarFile):
        self.wrapped = wrapped

    def getmembers(self) -> Sequence[FileInfo]:
        return self.wrapped.getmembers()

    def extractfile(self, entry: FileEntry) -> IO[bytes]:
        data = self.wrapped.extractfile(entry)
        if data is None:
            raise ReadError(f"Could not extract file: {entry}")
        return data


class Archive:
    def __init__(self, path: FilePath) -> None:
        if not tarfile.is_tarfile(path):
            raise ReadError(f"Could not open archive: {path!r}")
        self.path = path

    @property
    def contents(self) -> Sequence[FileInfo]:
        with self.open() as tarball:
            return tarball.getmembers()

    @contextmanager
    def open(self) -> Generator[WrappedArchive, None, None]:
        with tarfile.open(self.path) as tarball:
            yield WrappedTarArchive(tarball)

    # TODO: Handle attempt to read binary file
    def read(self, entry: FileEntry) -> str:
        with self.open() as tarball:
            with tarball.extractfile(entry) as e:
                return e.read().decode("utf-8")
