import tarfile
from contextlib import contextmanager
from typing import IO, Generator, List, Optional, Protocol, Union, cast


class ReadError(Exception):
    pass


FileEntry = Union[tarfile.TarInfo, str]


class Archivable(Protocol):
    def getmembers(self) -> List[tarfile.TarInfo]: ...
    def extractfile(self, entry: FileEntry) -> Optional[IO[bytes]]: ...


class Archive:
    def __init__(self, path: str) -> None:
        if not tarfile.is_tarfile(path):
            raise ReadError(f"Could not open archive: {path!r}")
        self.path = path

    @property
    def contents(self) -> List[tarfile.TarInfo]:
        with self.open() as tarball:
            return tarball.getmembers()

    @contextmanager
    def open(self) -> Generator[Archivable, None, None]:
        with tarfile.open(self.path) as tarball:
            yield tarball

    def read(self, entry: FileEntry) -> str:
        with self.open() as tarball:
            with cast(IO[bytes], tarball.extractfile(entry)) as e:
                return e.read().decode("utf-8")
