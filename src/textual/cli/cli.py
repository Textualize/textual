from __future__ import annotations


import click
from importlib_metadata import version

from textual.pilot import Pilot
from textual._import_app import import_app, AppFail


@click.group()
@click.version_option(version("textual"))
def run():
    pass


@run.command(help="Run the Textual Devtools console.")
@click.option("-v", "verbose", help="Enable verbose logs.", is_flag=True)
@click.option("-x", "--exclude", "exclude", help="Exclude log group(s)", multiple=True)
def console(verbose: bool, exclude: list[str]) -> None:
    """Launch the textual console."""
    from rich.console import Console
    from textual.devtools.server import _run_devtools

    console = Console()
    console.clear()
    console.show_cursor(False)
    try:
        _run_devtools(verbose=verbose, exclude=exclude)
    finally:
        console.show_cursor(True)


@run.command(
    "run",
    context_settings={
        "ignore_unknown_options": True,
    },
)
@click.argument("import_name", metavar="FILE or FILE:APP")
@click.option("--dev", "dev", help="Enable development mode", is_flag=True)
@click.option("--press", "press", help="Comma separated keys to simulate press")
def run_app(import_name: str, dev: bool, press: str) -> None:
    """Run a Textual app.

    The code to run may be given as a path (ending with .py) or as a Python
    import, which will load the code and run an app called "app". You may optionally
    add a colon plus the class or class instance you want to run.

    Here are some examples:

        textual run foo.py

        textual run foo.py:MyApp

        textual run module.foo

        textual run module.foo:MyApp

    If you are running a file and want to pass command line arguments, wrap the filename and arguments
    in quotes:

        textual run "foo.py arg --option"

    """

    import os
    import sys

    from textual.features import parse_features

    features = set(parse_features(os.environ.get("TEXTUAL", "")))
    if dev:
        features.add("debug")
        features.add("devtools")

    os.environ["TEXTUAL"] = ",".join(sorted(features))
    try:
        app = import_app(import_name)
    except AppFail as error:
        from rich.console import Console

        console = Console(stderr=True)
        console.print(str(error))
        sys.exit(1)

    press_keys = press.split(",") if press else None

    async def run_press_keys(pilot: Pilot) -> None:
        if press_keys is not None:
            await pilot.press(*press_keys)

    result = app.run(auto_pilot=run_press_keys)

    if result is not None:
        from rich.console import Console
        from rich.pretty import Pretty

        console = Console()
        console.print("[b]The app returned:")
        console.print(Pretty(result))


@run.command("borders")
def borders():
    """Explore the border styles available in Textual."""
    from textual.cli.previews import borders

    borders.app.run()


@run.command("easing")
def easing():
    """Explore the animation easing functions available in Textual."""
    from textual.cli.previews import easing

    easing.app.run()


@run.command("colors")
def colors():
    """Explore the design system."""
    from textual.cli.previews import colors

    colors.app.run()
