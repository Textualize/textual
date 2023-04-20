import os
import platform
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


def run(
    import_name: str, args: list[str], environment: dict[str, str] | None = None
) -> NoReturn:
    """Run a textual app.

    Note:
        The current process is abandoned.

    Args:
        import_name: Path or import:App of Textual app.
        args: Arguments to pass to the Textual app.
        environment: Environment variables, or None to use current process.
    """
    if environment is None:
        app_environment = dict(os.environ)
    else:
        app_environment = environment

    if _is_python_path(import_name):
        # If it is a Python path we can exec it now
        path = import_name
        exec_python([path, *args], app_environment)
    else:
        # Otherwise it is assumed to be a Python import
        exec_import(import_name, args, app_environment)


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
    return first_line.startswith("#!") and "python" in first_line


def exec_python(args: list[str], environment: dict[str, str]) -> NoReturn:
    """Execute the app.

    Args:
        path: Path to the Python file.
        args: CLI arguments.
        environment: Environment variables.

    """
    os.execvpe(sys.executable, ["python", *args], environment)


def exec_import(
    import_name: str, args: list[str], environment: dict[str, str]
) -> NoReturn:
    """Import and execute an app.

    Args:
        import_name: The Python import.
        args: Command line arguments.
        environment: Environment variables.

    """
    module, _colon, app = import_name.partition(":")
    script = EXEC_SCRIPT.substitute(MODULE=module, APP=app or "app")
    exec_python(["-c", script], environment)
