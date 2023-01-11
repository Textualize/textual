"""Textual CLI command code to print diagnostic information."""

import os
import sys
import platform
from importlib_metadata import version
from rich.console import Console


def _section(title: str, values: dict[str, str]) -> None:
    """Print a collection of named values within a titled section.

    Args:
        title (str): The title for the section.
        values (dict[str, str]): The values to print out.
    """
    max_name = len(max(list(values.keys()), key=len))
    max_value = len(max(list(values.values()), key=len))
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
    """Try and guess which terminal is being used."""

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
        elif "INSIDE_EMACS" in os.environ and os.environ["INSIDE_EMACS"].endswith(
            "eshell"
        ):
            term_program = "GNU Emacs (eshell)"
        elif "JEDITERM_SOURCE_ARGS" in os.environ:
            term_program = "PyCharm"

    else:
        # See if we can pull out some sort of version information too.
        term_version = os.environ.get("TERM_PROGRAM_VERSION")
        if term_version is not None:
            term_program = f"{term_program} ({term_version})"

    return "*Unknown*" if term_program is None else term_program


def _term() -> None:
    """Print information about the terminal."""
    _section(
        "Terminal",
        {
            "Terminal Application": _guess_term(),
            "TERM": os.environ.get("TERM", "*Not set*"),
            "COLORTERM": os.environ.get("COLORTERM", "*Not set*"),
            "FORCE_COLOR": os.environ.get("FORCE_COLOR", "*Not set*"),
            "NO_COLOR": os.environ.get("NO_COLOR", "*Not set*"),
        },
    )


def _console() -> None:
    """Print The Rich console options."""
    _section(
        "Rich Console options",
        {k: str(v) for k, v in Console().options.__dict__.items()},
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
