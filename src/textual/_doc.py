from __future__ import annotations

import os
import runpy
import shlex
from typing import TYPE_CHECKING, cast

from textual._import_app import AppFail, import_app

if TYPE_CHECKING:
    from textual.app import App

# This module defines our "Custom Fences", powered by SuperFences
# @link https://facelessuser.github.io/pymdown-extensions/extensions/superfences/#custom-fences
def format_svg(source, language, css_class, options, md, attrs, **kwargs) -> str:
    """A superfences formatter to insert a SVG screenshot."""

    try:
        cmd: list[str] = shlex.split(attrs["path"])
        path = cmd[0]

        _press = attrs.get("press", None)
        press = [*_press.split(",")] if _press else ["_"]
        title = attrs.get("title")

        os.environ["COLUMNS"] = attrs.get("columns", "80")
        os.environ["LINES"] = attrs.get("lines", "24")

        print(f"screenshotting {path!r}")

        cwd = os.getcwd()
        try:
            app = import_app(path)
            app.run(
                quit_after=5,
                press=press or ["ctrl+c"],
                headless=True,
                screenshot=True,
                screenshot_title=title,
            )
            svg = app._screenshot
        finally:
            os.chdir(cwd)

        assert svg is not None
        return svg

    except Exception as error:
        import traceback

        traceback.print_exception(error)


def rich(source, language, css_class, options, md, attrs, **kwargs) -> str:
    """A superfences formatter to insert a SVG screenshot."""

    import io

    from rich.console import Console

    title = attrs.get("title", "Rich")

    console = Console(
        file=io.StringIO(),
        record=True,
        force_terminal=True,
        color_system="truecolor",
    )
    error_console = Console(stderr=True)

    globals: dict = {}
    try:
        exec(source, globals)
    except Exception:
        error_console.print_exception()
        # console.bell()

    if "output" in globals:
        console.print(globals["output"])
    output_svg = console.export_svg(title=title)
    return output_svg
