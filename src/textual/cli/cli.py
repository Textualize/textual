import click

from textual.devtools.server import _run_devtools


@click.group()
def run():
    pass


@run.command(help="Run the Textual Devtools console")
def console():
    _run_devtools()
