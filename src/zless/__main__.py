import sys
from typing import NoReturn

import click
from simple_term_menu import TerminalMenu

from zless.archive import Archive, BadArchive
from zless.paths import output_path


def die(msg: str, code: int) -> NoReturn:
    click.echo(msg, err=True)
    sys.exit(code)


# TODO: -o to output to file
@click.command()
@click.option("-o", "--output", metavar="PATH", help="Output to file instead of stdout")
@click.argument("file")
def zless(file: str, output) -> None:
    try:
        archive = Archive(file)
    except FileNotFoundError as exc:
        die(f"No such file: {file!r}", 1)
    except BadArchive as exc:
        die(str(exc), 1)
    else:
        contents = archive.contents
        menu = TerminalMenu([entry.name for entry in archive.contents])
        idx = menu.show()
        entry = contents[idx]
        if not output:
            click.echo_via_pager(archive.read(entry))
        else:
            out_path = output_path(entry.name, output)
            with open(out_path, "w") as fh:
                fh.write(archive.read(entry))


if __name__ == "__main__":
    zless()
