"""Provides a Textual welcome widget."""

from rich.markdown import Markdown

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets._button import Button
from textual.widgets._static import Static

WELCOME_MD = """\
# Welcome!

Textual is a TUI, or *Text User Interface*, framework for Python inspired by modern web development. **We hope you enjoy using Textual!**

## Dune quote

> "I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."
"""


class Welcome(Static):
    """A Textual welcome widget.

    This widget can be used as a form of placeholder within a Textual
    application; although also see
    [Placeholder][textual.widgets._placeholder.Placeholder].
    """

    DEFAULT_CSS = """
        Welcome {
            width: 100%;
            height: 100%;
            background: $surface;
        }

        Welcome Container {
            padding: 1;
            background: $panel;
            color: $text;
        }

        Welcome #text {
            margin:  0 1;
        }

        Welcome #close {
            dock: bottom;
            width: 100%;
        }
    """

    def compose(self) -> ComposeResult:
        yield Container(Static(Markdown(WELCOME_MD), id="text"), id="md")
        yield Button("OK", id="close", variant="success")
