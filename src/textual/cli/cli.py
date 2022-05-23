from __future__ import annotations

from typing import TYPE_CHECKING

from importlib_metadata import version

import click

from textual.devtools.server import _run_devtools

if TYPE_CHECKING:
    from textual.app import App


@click.group()
@click.version_option(version("textual"))
def run():
    pass


@run.command(help="Run the Textual Devtools console")
def console():
    _run_devtools()


class AppFail(Exception):
    pass


def import_app(import_name: str) -> App:
    import inspect
    import importlib
    import sys

    from textual.app import App

    sys.path.append("")

    lib, _colon, name = import_name.partition(":")
    name = name or "app"

    try:
        module = importlib.import_module(lib)
    except ImportError as error:
        raise
        raise AppFail(str(error))

    try:
        app = getattr(module, name or "app")
    except AttributeError:
        raise AppFail(f"Unable to find {name!r} in {module!r}")

    if inspect.isclass(app) and issubclass(app, App):
        app = App()

    return app


@run.command("run")
@click.argument("import_name", metavar="IMPORT")
@click.option("--dev", "dev", help="Enable development mode", is_flag=True)
def run_app(import_name: str, dev: bool) -> None:
    """Run a Textual app."""

    import os
    import sys

    from textual.features import parse_features

    features = set(parse_features(os.environ.get("TEXTUAL", "")))
    if dev:
        features.add("debug")
        features.add("dev")

    os.environ["TEXTUAL"] = ",".join(sorted(features))

    try:
        app = import_app(import_name)
    except AppFail as error:
        from rich.console import Console

        console = Console(stderr=True)
        console.print(str(error))
        sys.exit(1)

    app.run()
