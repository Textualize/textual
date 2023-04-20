"""

Functions to run Textual apps with an updated environment.

Note that these methods will execute apps in a new process, and abandon the current process.
This means that they will never return.

"""

import os
import platform
import shlex
import sys
from string import Template
from typing import NoReturn

WINDOWS = platform.system() == "Windows"

EXEC_SCRIPT = Template(
    """\
from textual.app import App
from $MODULE import $APP as app;
if isinstance(app, App):
    # If we imported an app, run it
    app.run()
else:
    # Otherwise it is assumed to be a class
    app().run()
"""
)


def run_app(command_args: str, environment: dict[str, str] | None = None) -> None:
    """Run a textual app.

    Note:
        The current process is abandoned.

    Args:
        import_name: Path or import:App of Textual app.
        args: Arguments to pass to the Textual app.
        environment: Environment variables, or None to use current process.
    """
    import_name, *args = shlex.split(command_args, posix=not WINDOWS)
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
        except SyntaxError:
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


def exec_python(args: list[str], environment: dict[str, str]) -> NoReturn:
    """Execute the app.

    Args:
        path: Path to the Python file.
        args: CLI arguments.
        environment: Environment variables.

    """
    sys.stdout.flush()
    os.execvpe(sys.executable, ["python", *args], environment)


def exec_command(command: str, environment: dict[str, str]) -> NoReturn:
    """Execute a command with the given environment.

    Args:
        command: Command to execute.
        environment: Environment variables.
    """
    sys.stdout.flush()
    command, *args = shlex.split(command, posix=not WINDOWS)
    os.execvpe(command, [command, *args], environment)


def exec_import(
    import_name: str, args: list[str], environment: dict[str, str]
) -> NoReturn:
    """Import and execute an app.

    Raises:
        SyntaxError: If any imports are not valid Python symbols.

    Args:
        import_name: The Python import.
        args: Command line arguments.
        environment: Environment variables.

    """
    module, _colon, app = import_name.partition(":")
    script = EXEC_SCRIPT.substitute(MODULE=module, APP=app or "app")
    compile(script, "textual-exec", "exec")
    sys.stdout.flush()
    exec_python(["-c", script], environment)
