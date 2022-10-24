from pathlib import Path
from typing import Union


Pathlike = Union[str, Path]


def to_path(path: Pathlike) -> Path:
    """Converts a path represented by a string into a Path object."""
    if isinstance(path, str):
        return Path(path)
    return path


def output_path(source: Pathlike, dest: Pathlike) -> Path:
    source, dest = to_path(source), to_path(dest)
    if dest.is_dir():
        dest = dest / source.name
    return dest
