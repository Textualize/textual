from __future__ import annotations

import sys

try:
    import click
except ImportError:
    print("Please install 'textual[dev]' to use the 'textual' command")
    sys.exit(1)

from importlib_metadata import version

from textual._import_app import AppFail, import_app
from textual.pilot import Pilot


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


def _post_run_warnings() -> None:
    """Look for and report any issues with the environment.

    This is the right place to add code that looks at the terminal, or other
    environmental issues, and if a problem is seen it should be printed so
    the developer can see it easily.
    """
    import os
    import platform

    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    # Add any test/warning pair here. The list contains a tuple where the
    # first item is `True` if a problem situation is detected, and the
    # second item is a message to show the user on exit from `textual run`.
    warnings = [
        (
            platform.system() == "Darwin"
            and os.environ.get("TERM_PROGRAM") == "Apple_Terminal",
            "The default terminal app on macOS is limited to 256 colors. See our FAQ for more details:\n\n"
            "https://github.com/Textualize/textual/blob/main/FAQ.md#why-doesn't-textual-look-good-on-macos",
        )
    ]

    for concerning, concern in warnings:
        if concerning:
            console.print(Panel.fit(f"⚠️ [bold green] {concern}[/]", style="cyan"))


@run.command(
    "run",
    context_settings={
        "ignore_unknown_options": True,
    },
)
@click.argument("import_name", metavar="FILE or FILE:APP")
@click.option("--dev", "dev", help="Enable development mode", is_flag=True)
@click.option("--press", "press", help="Comma separated keys to simulate press")
@click.option(
    "--screenshot",
    type=int,
    default=None,
    metavar="DELAY",
    help="Take screenshot after DELAY seconds",
)
def run_app(import_name: str, dev: bool, press: str, screenshot: int | None) -> None:
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
    from asyncio import sleep

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
        if screenshot is not None:
            await sleep(screenshot)
            filename = pilot.app.save_screenshot()
            pilot.app.exit(message=f"Saved {filename!r}")

    result = app.run(auto_pilot=run_press_keys)

    if result is not None:
        from rich.console import Console
        from rich.pretty import Pretty

        console = Console()
        console.print("[b]The app returned:")
        console.print(Pretty(result))

    _post_run_warnings()


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


@run.command("keys")
def keys():
    """Show key events."""
    from textual.cli.previews import keys

    keys.app.run()


@run.command("diagnose")
def run_diagnose():
    """Print information about the Textual environment"""
    from textual.cli.tools.diagnose import diagnose

    diagnose()
