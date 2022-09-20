from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Footer


class JustABox(App):
    BINDINGS = [
        Binding(key="t", action="text_fade_out", description="text-opacity fade out"),
        Binding(key="o", action="widget_fade_out", description="opacity fade out"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("Hello, world!", id="box1")
        yield Footer()

    def action_text_fade_out(self) -> None:
        box = self.query_one("#box1")
        self.animator.animate(box.styles, "text_opacity", value=0.0, duration=1)

    def action_widget_fade_out(self) -> None:
        box = self.query_one("#box1")
        self.animator.animate(box.styles, "opacity", value=0.0, duration=1)


app = JustABox(watch_css=True, css_path="../darren/just_a_box.css")

if __name__ == "__main__":
    app.run()
