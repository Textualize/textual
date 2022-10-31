from __future__ import annotations

import os
import shlex
from typing import Iterable

from textual.app import App
from textual.pilot import Pilot
from textual._import_app import import_app


# This module defines our "Custom Fences", powered by SuperFences
# @link https://facelessuser.github.io/pymdown-extensions/extensions/superfences/#custom-fences
def format_svg(source, language, css_class, options, md, attrs, **kwargs) -> str:
    """A superfences formatter to insert an SVG screenshot."""

    try:
        cmd: list[str] = shlex.split(attrs["path"])
        path = cmd[0]

        _press = attrs.get("press", None)
        press = [*_press.split(",")] if _press else []
        title = attrs.get("title")

        print(f"screenshotting {path!r}")

        cwd = os.getcwd()
        try:
            rows = int(attrs.get("lines", 24))
            columns = int(attrs.get("columns", 80))
            svg = take_svg_screenshot(
                None, path, press, title, terminal_size=(columns, rows)
            )
        finally:
            os.chdir(cwd)

        assert svg is not None
        return svg

    except Exception as error:
        import traceback

        traceback.print_exception(error)


def take_svg_screenshot(
    app: App | None = None,
    app_path: str | None = None,
    press: Iterable[str] = (),
    title: str | None = None,
    terminal_size: tuple[int, int] = (80, 24),
) -> str:
    """

    Args:
        app: An app instance. Must be supplied if app_path is not.
        app_path: A path to an app. Must be supplied if app is not.
        press: Key presses to run before taking screenshot. "_" is a short pause.
        title: The terminal title in the output image.
        terminal_size: A pair of integers (rows, columns), representing terminal size.

    Returns:
        str: An SVG string, showing the content of the terminal window at the time
            the screenshot was taken.

    """

    if app is None:
        assert app_path is not None
        app = import_app(app_path)

    assert app is not None

    if title is None:
        title = app.title

    async def auto_pilot(pilot: Pilot) -> None:
        app = pilot.app
        await pilot.press(*press)
        svg = app.export_screenshot(title=title)
        app.exit(svg)

    svg = app.run(
        headless=True,
        auto_pilot=auto_pilot,
        size=terminal_size,
    )
    assert svg is not None

    return svg


def rich(source, language, css_class, options, md, attrs, **kwargs) -> str:
    """A superfences formatter to insert an SVG screenshot."""

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
