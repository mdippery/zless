import sys
from typing import NoReturn

import click
from simple_term_menu import TerminalMenu

from zless import __version__
from zless.archive import Archive, BadArchive
from zless.paths import output_path


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def die(msg: str, code: int) -> NoReturn:
    click.echo(msg, err=True)
    sys.exit(code)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__, "-V", "--version")
@click.option("-o", "--output", metavar="PATH", help="Output to file instead of stdout.")
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
        if not idx:
            sys.exit(0)
        entry = contents[idx]
        if not output:
            click.echo_via_pager(archive.read(entry))
        else:
            out_path = output_path(entry.name, output)
            with open(out_path, "w") as fh:
                fh.write(archive.read(entry))


if __name__ == "__main__":
    zless()
