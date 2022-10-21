import click
from simple_term_menu import TerminalMenu
from zless.archive import Archive


@click.command()
@click.argument("file")
def zless(file: str) -> None:
    archive = Archive(file)
    contents = archive.contents
    menu = TerminalMenu([entry.name for entry in archive.contents])
    idx = menu.show()
    entry = contents[idx]
    click.echo_via_pager(archive.read(entry))


if __name__ == "__main__":
    zless()
