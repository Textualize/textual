from __future__ import annotations

import runpy
import os
from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import App

# This module defines our "Custom Fences", powered by SuperFences
# @link https://facelessuser.github.io/pymdown-extensions/extensions/superfences/#custom-fences
def format_svg(source, language, css_class, options, md, attrs, **kwargs) -> str:
    """A superfences formatter to insert a SVG screenshot."""

    try:
        path: str = attrs["path"]
        _press = attrs.get("press", None)
        press = [*_press.split(",")] if _press else ["_"]
        title = attrs.get("title")

        os.environ["COLUMNS"] = attrs.get("columns", "80")
        os.environ["LINES"] = attrs.get("lines", "24")

        print(f"screenshotting {path!r}")

        cwd = os.getcwd()
        try:
            app_vars = runpy.run_path(path)
            app: App = cast("App", app_vars["app"])
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
