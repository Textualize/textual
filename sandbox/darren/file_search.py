from __future__ import annotations

from pathlib import Path
from typing import Iterable

from rich.console import RenderableType
from rich.table import Table
from rich.text import Text

from textual.app import App
from textual.geometry import Size
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets.text_input import TextInput, TextWidgetBase


def get_files() -> list[Path]:
    files = list(Path.cwd().iterdir())
    return files


class FileTable(Widget):
    filter = Reactive("", layout=True)

    def __init__(self, *args, files: Iterable[Path] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = files if files is not None else []

    @property
    def filtered_files(self) -> list[Path]:
        return [
            file
            for file in self.files
            if self.filter == "" or (self.filter and self.filter in file.name)
        ]

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return len(self.filtered_files)

    def render(self) -> RenderableType:
        grid = Table.grid()
        grid.add_column()
        for file in self.filtered_files:
            file_text = Text(f" {file.name}")
            if self.filter:
                file_text.highlight_regex(self.filter, "black on yellow")
            grid.add_row(file_text)
        return grid


class FileSearchApp(App):
    dark = True

    def on_mount(self) -> None:
        self.file_table = FileTable(id="file_table", files=list(Path.cwd().iterdir()))
        self.search_bar = TextInput(placeholder="Search for files...")
        self.search_bar.focus()
        self.mount(file_table_wrapper=Widget(self.file_table))
        self.mount(search_bar=self.search_bar)

    def on_text_input_changed(self, event: TextInput.Changed) -> None:
        self.file_table.filter = event.value


app = FileSearchApp(css_path="file_search.scss", watch_css=True)

if __name__ == "__main__":
    result = app.run()
