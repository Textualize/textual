from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Static


class JustABox(App):
    def compose(self) -> ComposeResult:
        yield Static("Hello, world!", classes="box1")


if __name__ == "__main__":
    app = JustABox(css_path="../darren/just_a_box.css", watch_css=True)
    app.run()
