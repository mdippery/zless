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
    def contents(self) -> typing.Sequence[FileInfo]:
        return [ZipFileInfo(e) for e in self._zip.infolist()]

    def read_bytes(self, entry: FileEntry) -> bytes:
        if isinstance(entry, FileInfo):
            entry = entry.name
        with self._zip.open(entry) as zip_:
            return zip_.read().decode("utf-8")

    def __del__(self):
        try:
            self._zip.close()
        except AttributeError:
            pass
