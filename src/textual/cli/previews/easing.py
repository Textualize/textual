from __future__ import annotations

from rich.console import RenderableType

from textual import layout
from textual._easing import EASING
from textual.app import ComposeResult, App
from textual.cli.previews.borders import TEXT
from textual.reactive import Reactive
from textual.scrollbar import ScrollBarRender
from textual.widget import Widget
from textual.widgets import Button, Static, Footer
from textual.widgets import TextInput
from textual.widgets._text_input import TextWidgetBase

VIRTUAL_SIZE = 100
WINDOW_SIZE = 10
START_POSITION = 0.0
END_POSITION = float(VIRTUAL_SIZE - WINDOW_SIZE)


class EasingButtons(Widget):
    def compose(self) -> ComposeResult:
        for easing in sorted(EASING, reverse=True):
            yield Button(easing, id=easing)


class Bar(Widget):
    position = Reactive.init(START_POSITION)
    animation_running = Reactive(False)

    DEFAULT_CSS = """
    
    Bar {
        background: $surface;
        color: $error;
    }

    Bar.-active {
        background: $surface;
        color: $success;
    }
    
    """

    def watch_animation_running(self, running: bool) -> None:
        self.set_class(running, "-active")

    def render(self) -> RenderableType:

        return ScrollBarRender(
            virtual_size=VIRTUAL_SIZE,
            window_size=WINDOW_SIZE,
            position=self.position,
            style=self.rich_style,
        )


class EasingApp(App):
    position = Reactive.init(START_POSITION)
    duration = Reactive.var(1.0)

    def on_load(self):
        self.bind(
            "ctrl+p", "focus('duration-input')", description="Focus: Duration Input"
        )
        self.bind("ctrl+b", "toggle_dark", description="Toggle Dark")

    def compose(self) -> ComposeResult:
        self.animated_bar = Bar()
        self.animated_bar.position = START_POSITION
        duration_input = TextInput(
            placeholder="Duration", initial="1.0", id="duration-input"
        )

        self.opacity_widget = Static(
            f"[b]Welcome to Textual![/]\n\n{TEXT}", id="opacity-widget"
        )

        yield EasingButtons()
        yield layout.Vertical(
            layout.Horizontal(
                Static("Animation Duration:", id="label"), duration_input, id="inputs"
            ),
            layout.Horizontal(
                self.animated_bar,
                layout.Container(self.opacity_widget, id="other"),
            ),
            Footer(),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.animated_bar.animation_running = True

        def _animation_complete():
            self.animated_bar.animation_running = False

        target_position = (
            END_POSITION if self.position == START_POSITION else START_POSITION
        )
        self.animate(
            "position",
            value=target_position,
            final_value=target_position,
            duration=self.duration,
            easing=event.button.id,
            on_complete=_animation_complete,
        )

    def watch_position(self, value: int):
        self.animated_bar.position = value
        self.opacity_widget.styles.opacity = 1 - value / END_POSITION

    def on_text_widget_base_changed(self, event: TextWidgetBase.Changed):
        if event.sender.id == "duration-input":
            new_duration = _try_float(event.value)
            if new_duration is not None:
                self.duration = new_duration

    def action_toggle_dark(self):
        self.dark = not self.dark


def _try_float(string: str) -> float | None:
    try:
        return float(string)
    except ValueError:
        return None


app = EasingApp(css_path="easing.css")
if __name__ == "__main__":
    app.run()
