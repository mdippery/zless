import sys
from typing import NoReturn

import click
from simple_term_menu import TerminalMenu

from zless.archive import Archive, ReadError


def die(msg: str, code: int) -> NoReturn:
    click.echo(msg, err=True)
    sys.exit(code)


@click.command()
@click.argument("file")
def zless(file: str) -> None:
    try:
        archive = Archive(file)
    except FileNotFoundError as exc:
        die(f"No such file: {file!r}", 1)
    except ReadError as exc:
        die(str(exc), 1)
    else:
        contents = archive.contents
        menu = TerminalMenu([entry.name for entry in archive.contents])
        idx = menu.show()
        entry = contents[idx]
        click.echo_via_pager(archive.read(entry))


if __name__ == "__main__":
    zless()
