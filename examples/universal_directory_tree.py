"""
Universal Directory Tree
"""

from __future__ import annotations

import argparse

from textual._pathlib import PathlibImplementation as Path
from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree, Footer, Header

try:
    import upath  # noqa
except ImportError:
    raise ImportError(
        "You must install textual with the [fsspec] extra to run this example"
    )


class UniversalDirectoryTreeApp(App):
    """
    The power of upath and fsspec in a Textual app
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self, *args, path: Path | str, **kwargs):
        super().__init__(*args, **kwargs)
        self.universal_path = path

    def compose(self) -> ComposeResult:
        yield Header()
        yield DirectoryTree(path=self.universal_path)
        yield Footer()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Directory Tree")
    parser.add_argument("path", type=str, help="Path to open")
    args = parser.parse_args()
    file_path = str(Path(args.path).resolve()).rstrip("/")
    app = UniversalDirectoryTreeApp(path=file_path)
    app.run()
