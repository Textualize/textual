from __future__ import annotations

import os
import runpy
import shlex
from pathlib import Path
from typing import cast, TYPE_CHECKING


if TYPE_CHECKING:
    from textual.app import App


class AppFail(Exception):
    pass


def import_app(import_name: str) -> App:
    """Import an app from a path or import name.

    Args:
        import_name (str): A name to import, such as `foo.bar`, or a path ending with .py.

    Raises:
        AppFail: If the app could not be found for any reason.

    Returns:
        App: A Textual application
    """

    import inspect
    import importlib
    import sys

    from textual.app import App, WINDOWS

    import_name, *argv = shlex.split(import_name, posix=not WINDOWS)
    lib, _colon, name = import_name.partition(":")

    if lib.endswith(".py"):
        path = os.path.abspath(lib)
        sys.path.append(str(Path(path).parent))
        try:
            global_vars = runpy.run_path(path, {})
        except Exception as error:
            raise AppFail(str(error))

        if "sys" in global_vars:
            global_vars["sys"].argv = [path, *argv]

        if name:
            # User has given a name, use that
            try:
                app = global_vars[name]
            except KeyError:
                raise AppFail(f"App {name!r} not found in {lib!r}")
        else:
            # User has not given a name
            if "app" in global_vars:
                # App exists, lets use that
                try:
                    app = global_vars["app"]
                except KeyError:
                    raise AppFail(f"App {name!r} not found in {lib!r}")
            else:
                # Find a App class or instance that is *not* the base class
                apps = [
                    value
                    for value in global_vars.values()
                    if (
                        isinstance(value, App)
                        or (inspect.isclass(value) and issubclass(value, App))
                        and value is not App
                    )
                ]
                if not apps:
                    raise AppFail(
                        f'Unable to find app in {lib!r}, try specifying app with "foo.py:app"'
                    )
                if len(apps) > 1:
                    raise AppFail(
                        f'Multiple apps found {lib!r}, try specifying app with "foo.py:app"'
                    )
                app = apps[0]
        app._BASE_PATH = path

    else:
        # Assuming the user wants to import the file
        sys.path.append("")
        try:
            module = importlib.import_module(lib)
        except ImportError as error:
            raise AppFail(str(error))

        try:
            app = getattr(module, name or "app")
        except AttributeError:
            raise AppFail(f"Unable to find {name!r} in {module!r}")

    if inspect.isclass(app) and issubclass(app, App):
        app = app()

    return cast(App, app)
