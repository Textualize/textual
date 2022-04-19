import click
from importlib_metadata import version

from textual.devtools.server import _run_devtools


@click.group()
@click.version_option(version("textual"))
def run():
    pass


@run.command(help="Run the Textual Devtools console")
def console():
    _run_devtools()
