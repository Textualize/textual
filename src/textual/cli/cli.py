import click

import textual
from textual.devtools.server import _run_devtools


@click.group()
@click.version_option(textual.__version__)
def run():
    pass


@run.command(help="Run the Textual Devtools console")
def console():
    _run_devtools()
