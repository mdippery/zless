import tarfile
import typing
import zipfile
from contextlib import contextmanager
from pathlib import Path


class BadArchive(Exception):
    pass


@typing.runtime_checkable
class FileInfo(typing.Protocol):
    @property
    def name(self) -> str:
        ...


FileEntry = typing.Union[str, FileInfo]
FilePath = typing.Union[str, Path]

Encoding = str


class Archive:
    def __new__(cls: typing.Type["Archive"], path: str) -> "Archive":
        if tarfile.is_tarfile(path):
            cls = TarArchive
        elif zipfile.is_zipfile(path):
            cls = ZipArchive
        else:
            raise BadArchive(f"Could not open archive: {path}")
        self = object.__new__(cls)
        cls.__init__(self, path)
        return self

    def __init__(self, path: str) -> None:
        raise NotImplementedError("Subclasses must implement")

    @property
    def contents(self) -> typing.Sequence[FileInfo]:
        raise NotImplementedError("Subclasses must implement")

    def read(self, entry: FileInfo, encoding: Encoding = "utf-8") -> str:
        return self.read_bytes(entry).decode(encoding)

    def read_bytes(self, entry: FileInfo) -> bytes:
        raise NotImplementedError("Subclasses must implement")


class TarArchive(Archive):
    def __init__(self, path: FilePath) -> None:
        assert tarfile.is_tarfile(path)
        self.path = path

    @property
    def contents(self) -> typing.Sequence[FileInfo]:
        with self.open() as tarball:
            return tarball.getmembers()

    @contextmanager
    def open(self) -> typing.Generator[tarfile.TarFile, None, None]:
        with tarfile.open(self.path) as tarball:
            yield tarball

    def read_bytes(self, entry: FileEntry) -> bytes:
        if not isinstance(entry, str):
            entry = entry.name
        with self.open() as tarball:
            data = tarball.extractfile(entry)
            if data is None:
                raise BadArchive(f"{self.path} has no entry: {entry}")
            return data.read()


class ZipFileInfo:
    def __init__(self, wrapped: zipfile.ZipInfo) -> None:
        self.wrapped = wrapped

    @property
    def name(self) -> str:
        return self.wrapped.filename


class ZipArchive(Archive):
    def __init__(self, path: str) -> None:
        assert zipfile.is_zipfile(path)
        self.path = path

    @property
    def contents(self) -> typing.Sequence[FileInfo]:
        with self.open() as _zip:
            return [ZipFileInfo(e) for e in _zip.infolist()]

    @contextmanager
    def open(self) -> typing.Generator[zipfile.ZipFile, None, None]:
        with zipfile.ZipFile(self.path) as zip_:
            yield zip_

    def read_bytes(self, entry: FileEntry) -> bytes:
        if isinstance(entry, FileInfo):
            entry = entry.name
        with self.open() as _zip:
            with _zip.open(entry) as entry:
                return entry.read()
