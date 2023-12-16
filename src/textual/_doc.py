from __future__ import annotations

import hashlib
import inspect
import os
import shlex
from pathlib import Path
from typing import Awaitable, Callable, Iterable, cast

from textual._import_app import import_app
from textual.app import App
from textual.pilot import Pilot

SCREENSHOT_CACHE = ".screenshot_cache"


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
            hover = attrs.get("hover", "")
            svg = take_svg_screenshot(
                None,
                path,
                press,
                hover=hover,
                title=title,
                terminal_size=(columns, rows),
                wait_for_animation=False,
            )
        finally:
            os.chdir(cwd)

        assert svg is not None
        return svg

    except Exception as error:
        import traceback

        traceback.print_exception(error)
        return ""


def take_svg_screenshot(
    app: App | None = None,
    app_path: str | None = None,
    press: Iterable[str] = (),
    hover: str = "",
    title: str | None = None,
    terminal_size: tuple[int, int] = (80, 24),
    run_before: Callable[[Pilot], Awaitable[None] | None] | None = None,
    wait_for_animation: bool = True,
) -> str:
    """

    Args:
        app: An app instance. Must be supplied if app_path is not.
        app_path: A path to an app. Must be supplied if app is not.
        press: Key presses to run before taking screenshot. "_" is a short pause.
        hover: Hover over the given widget.
        title: The terminal title in the output image.
        terminal_size: A pair of integers (rows, columns), representing terminal size.
        run_before: An arbitrary callable that runs arbitrary code before taking the
            screenshot. Use this to simulate complex user interactions with the app
            that cannot be simulated by key presses.
        wait_for_animation: Wait for animation to complete before taking screenshot.

    Returns:
        An SVG string, showing the content of the terminal window at the time
            the screenshot was taken.
    """

    if app is None:
        assert app_path is not None
        app = import_app(app_path)

    assert app is not None

    if title is None:
        title = app.title

    def get_cache_key(app: App) -> str:
        hash = hashlib.md5()
        file_paths = [app_path] + app.css_path
        for path in file_paths:
            assert path is not None
            with open(path, "rb") as source_file:
                hash.update(source_file.read())
        hash.update(f"{press}-{hover}-{title}-{terminal_size}".encode("utf-8"))
        cache_key = f"{hash.hexdigest()}.svg"
        return cache_key

    if app_path is not None and run_before is None:
        screenshot_cache = Path(SCREENSHOT_CACHE)
        screenshot_cache.mkdir(exist_ok=True)

        screenshot_path = screenshot_cache / get_cache_key(app)
        if screenshot_path.exists():
            return screenshot_path.read_text()

    async def auto_pilot(pilot: Pilot) -> None:
        app = pilot.app
        if run_before is not None:
            result = run_before(pilot)
            if inspect.isawaitable(result):
                await result
        await pilot.pause()
        await pilot.press(*press)
        if hover:
            await pilot.hover(hover)
            await pilot.pause(0.5)
        if wait_for_animation:
            await pilot.wait_for_scheduled_animations()
            await pilot.pause()
        await pilot.pause()
        await pilot.wait_for_scheduled_animations()
        svg = app.export_screenshot(title=title)

        app.exit(svg)

    svg = cast(
        str,
        app.run(
            headless=True,
            auto_pilot=auto_pilot,
            size=terminal_size,
        ),
    )

    if app_path is not None and run_before is None:
        screenshot_path.write_text(svg)

    assert svg is not None

    return svg


def rich(source, language, css_class, options, md, attrs, **kwargs) -> str:
    """A superfences formatter to insert an SVG screenshot."""

    import io

    from rich.console import Console

    title = attrs.get("title", "Rich")

    rows = int(attrs.get("lines", 24))
    columns = int(attrs.get("columns", 80))

    console = Console(
        file=io.StringIO(),
        record=True,
        force_terminal=True,
        color_system="truecolor",
        width=columns,
        height=rows,
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
