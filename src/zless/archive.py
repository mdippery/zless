import tarfile
from typing import IO, List, cast


class ReadError(Exception):
    pass


class Archive:
    def __init__(self, path: str) -> None:
        if not tarfile.is_tarfile(path):
            raise ReadError(f"Could not open archive: {path!r}")
        self.path = path

    @property
    def contents(self) -> List[tarfile.TarInfo]:
        with tarfile.open(self.path) as tarball:
            return tarball.getmembers()

    def read(self, entry: tarfile.TarInfo) -> str:
        with tarfile.open(self.path) as tarball:
            with cast(IO[bytes], tarball.extractfile(entry)) as e:
                return e.read().decode("utf-8")
