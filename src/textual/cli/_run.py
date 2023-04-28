"""

Functions to run Textual apps with an updated environment.

Note that these methods will execute apps in a new process, and abandon the current process.
This means that (if they succeed) they will never return.
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from string import Template
from typing import NoReturn, Sequence

WINDOWS = platform.system() == "Windows"

EXEC_SCRIPT = Template(
    """\
from textual.app import App
try:
    from $MODULE import $APP as app;
except ImportError:
    raise SystemExit("Unable to import '$APP' from module '$MODULE'") from None

if isinstance(app, App):
    # If we imported an app, run it
    app.run()
else:
    # Otherwise it is assumed to be a class
    app().run()
"""
)
"""A template script to import and run an app."""


class ExecImportError(Exception):
    """Raised if a Python import is invalid."""


def run_app(
    import_name: str, args: Sequence[str], environment: dict[str, str] | None = None
) -> None:
    """Run a textual app.

    Note:
        The current process is abandoned.

    Args:
        command_args: Arguments to pass to the Textual app.
        environment: Environment variables, or None to use current process.
    """
    if environment is None:
        app_environment = dict(os.environ)
    else:
        app_environment = environment

    if _is_python_path(import_name):
        # If it is a Python path we can exec it now
        exec_python([import_name, *args], app_environment)

    else:
        # Otherwise it is assumed to be a Python import
        try:
            exec_import(import_name, args, app_environment)
        except (SyntaxError, ExecImportError):
            print(f"Unable to import Textual app from {import_name!r}")


def _is_python_path(path: str) -> bool:
    """Does the given file look like it's run with Python?

    Args:
        path: The path to check.

    Returns:
        True if the path references Python code, False it it doesn't.
    """
    if path.endswith(".py"):
        return True
    try:
        with open(path, "r") as source:
            first_line = source.readline()
    except IOError:
        return False
    return first_line.startswith("#!") and "py" in first_line


def _flush() -> None:
    """Flush output before exec."""
    sys.stderr.flush()
    sys.stdout.flush()


def exec_python(args: Sequence[str], environment: dict[str, str]) -> None:
    """Execute a Python script.

    Args:
        args: Additional arguments.
        environment: Environment variables.
    """
    _flush()
    if WINDOWS:
        subprocess.call([sys.executable, *args], env=environment)
    else:
        os.execvpe(sys.executable, ["python", *args], environment)


def exec_command(
    command: str, args: Sequence[str], environment: dict[str, str]
) -> None:
    """Execute a command with the given environment.

    Args:
        command: Command to execute.
        environment: Environment variables.
    """
    _flush()
    if WINDOWS:
        subprocess.call([command, *args], env=environment)
    else:
        os.execvpe(command, [command, *args], environment)


def exec_import(
    import_name: str, args: Sequence[str], environment: dict[str, str]
) -> None:
    """Import and execute an app.

    Raises:
        SyntaxError: If any imports are not valid Python symbols.
        ExecImportError: If the module could not be imported.

    Args:
        import_name: The Python import.
        args: Command line arguments.
        environment: Environment variables.
    """
    module, _colon, app = import_name.partition(":")
    app = app or "app"

    script = EXEC_SCRIPT.substitute(MODULE=module, APP=app)
    # Compiling the script will raise a SyntaxError if there are any invalid symbols
    compile(script, "textual-exec", "exec")
    _flush()
    exec_python(["-c", script, *args], environment)
