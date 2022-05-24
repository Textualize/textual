from __future__ import annotations

from typing import cast, TYPE_CHECKING

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
    """Import an app from it's import name.

    Args:
        import_name (str): A name to import, such as `foo.bar`

    Raises:
        AppFail: If the app could not be found for any reason.

    Returns:
        App: A Textual application
    """

    import inspect
    import importlib
    import sys

    from textual.app import App

    sys.path.append("")

    lib, _colon, name = import_name.partition(":")
    name = name or "app"

    if lib.endswith(".py"):
        # We're assuming the user wants to load a .py file
        try:
            with open(lib) as python_file:
                py_code = python_file.read()
        except Exception as error:
            raise AppFail(str(error))

        global_vars: dict[str, object] = {}
        exec(py_code, global_vars)

        try:
            app = global_vars[name]
        except KeyError:
            raise AppFail(f"App {name!r} not found in {lib!r}")
    else:
        # Assuming the user wants to import the file
        try:
            module = importlib.import_module(lib)
        except ImportError as error:
            raise AppFail(str(error))

        try:
            app = getattr(module, name or "app")
        except AttributeError:
            raise AppFail(f"Unable to find {name!r} in {module!r}")

    if inspect.isclass(app) and issubclass(app, App):
        app = App()

    return cast(App, app)


@run.command("run")
@click.argument("import_name", metavar="FILE or FILE:APP")
@click.option("--dev", "dev", help="Enable development mode", is_flag=True)
def run_app(import_name: str, dev: bool) -> None:
    """Run a Textual app.

    The code to run may be given as a path (ending with .py) or as a Python
    import, which will load the code and run an app called "app". You may optionally
    add a colon plus the class or class instance you want to run.

    Here are some examples:

    textual run foo.py

    textual run foo.py:MyApp

    textual run module.foo

    textual run module.foo:MyApp

    """

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
