"""Textual CLI command code to print diagnostic information."""

from __future__ import annotations

import os
import platform
import sys
from functools import singledispatch
from typing import Any

from importlib_metadata import version
from rich.console import Console, ConsoleDimensions


def _section(title: str, values: dict[str, str]) -> None:
    """Print a collection of named values within a titled section.

    Args:
        title: The title for the section.
        values: The values to print out.
    """
    max_name = max(map(len, values.keys()))
    max_value = max(map(len, values.values()))
    print(f"## {title}")
    print()
    print(f"| {'Name':{max_name}} | {'Value':{max_value}} |")
    print(f"|-{'-' * max_name}-|-{'-'*max_value}-|")
    for name, value in values.items():
        print(f"| {name:{max_name}} | {value:{max_value}} |")
    print()


def _versions() -> None:
    """Print useful version numbers."""
    _section("Versions", {"Textual": version("textual"), "Rich": version("rich")})


def _python() -> None:
    """Print information about Python."""
    _section(
        "Python",
        {
            "Version": platform.python_version(),
            "Implementation": platform.python_implementation(),
            "Compiler": platform.python_compiler(),
            "Executable": sys.executable,
        },
    )


def _os() -> None:
    _section(
        "Operating System",
        {
            "System": platform.system(),
            "Release": platform.release(),
            "Version": platform.version(),
        },
    )


def _guess_term() -> str:
    """Try and guess which terminal is being used.

    Returns:
        The best guess at the name of the terminal.
    """

    # First obvious place to look is in $TERM_PROGRAM.
    term_program = os.environ.get("TERM_PROGRAM")

    if term_program is None:
        # Seems we couldn't get it that way. Let's check for some of the
        # more common terminal signatures.
        if "ALACRITTY_WINDOW_ID" in os.environ:
            term_program = "Alacritty"
        elif "KITTY_PID" in os.environ:
            term_program = "Kitty"
        elif "WT_SESSION" in os.environ:
            term_program = "Windows Terminal"
        elif "INSIDE_EMACS" in os.environ and os.environ["INSIDE_EMACS"]:
            term_program = (
                f"GNU Emacs {' '.join(os.environ['INSIDE_EMACS'].split(','))}"
            )
        elif "JEDITERM_SOURCE_ARGS" in os.environ:
            term_program = "PyCharm"

    else:
        # See if we can pull out some sort of version information too.
        term_version = os.environ.get("TERM_PROGRAM_VERSION")
        if term_version is not None:
            term_program = f"{term_program} ({term_version})"

    return "*Unknown*" if term_program is None else term_program


def _env(var_name: str) -> str:
    """Get a representation of an environment variable.

    Args:
        var_name: The name of the variable to get.

    Returns:
        The value, or an indication that it isn't set.
    """
    return os.environ.get(var_name, "*Not set*")


def _term() -> None:
    """Print information about the terminal."""
    _section(
        "Terminal",
        {
            "Terminal Application": _guess_term(),
            "TERM": _env("TERM"),
            "COLORTERM": _env("COLORTERM"),
            "FORCE_COLOR": _env("FORCE_COLOR"),
            "NO_COLOR": _env("NO_COLOR"),
        },
    )


@singledispatch
def _str_rich(value: Any) -> str:
    """Convert a rich console option to a string.

    Args:
        value: The value to convert to a string.

    Returns:
        The string version of the value for output
    """
    return str(value)


@_str_rich.register
def _(value: ConsoleDimensions) -> str:
    return f"width={value.width}, height={value.height}"


def _console() -> None:
    """Print The Rich console options."""
    _section(
        "Rich Console options",
        {k: _str_rich(v) for k, v in Console().options.__dict__.items()},
    )


def diagnose() -> None:
    """Print information about Textual and its environment to help diagnose problems."""
    print("# Textual Diagnostics")
    print()
    _versions()
    _python()
    _os()
    _term()
    _console()
    # TODO: Recommended changes. Given all of the above, make any useful
    # recommendations to the user (eg: don't use Windows console, use
    # Windows Terminal; don't use macOS Terminal.app, etc).
