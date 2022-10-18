from __future__ import annotations

from typing import ClassVar

from rich.console import RenderableType

from ..binding import Binding
from ..geometry import Size
from ..message import Message
from ..reactive import reactive
from ..widget import Widget
from ..scrollbar import ScrollBarRender


class Checkbox(Widget, can_focus=True):
    """A checkbox widget. Represents a boolean value. Can be toggled by clicking
    on it or by pressing the enter key or space bar while it has focus.

    Args:
        value (bool, optional): The initial value of the checkbox. Defaults to False.
        animate (bool, optional): True if the checkbox should animate when toggled. Defaults to True.
    """

    DEFAULT_CSS = """

    Checkbox {
        border: tall transparent;
        background: $panel;
        height: auto;
        width: auto;
        padding: 0 2;
    }

    Checkbox > .checkbox--switch {
        background: $panel-darken-2;
        color: $panel-lighten-2;
    }

    Checkbox:hover {
        border: tall $background;
    }

    Checkbox:focus {
        border: tall $accent;
    }

    Checkbox.-on {

    }

    Checkbox.-on > .checkbox--switch {
        color: $success;
    }
    """

    BINDINGS = [
        Binding("enter,space", "toggle", "toggle", show=False),
    ]

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "checkbox--switch",
    }

    value = reactive(False, init=False)
    slider_pos = reactive(0.0)

    def __init__(
        self,
        value: bool = None,
        *,
        animate: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes)
        if value:
            self.slider_pos = 1.0
            self._reactive_value = value
        self._should_animate = animate

    def watch_value(self, value: bool) -> None:
        target_slider_pos = 1.0 if value else 0.0
        if self._should_animate:
            self.animate("slider_pos", target_slider_pos, duration=0.3)
        else:
            self.slider_pos = target_slider_pos
        self.emit_no_wait(self.Changed(self, self.value))

    def watch_slider_pos(self, slider_pos: float) -> None:
        self.set_class(slider_pos == 1, "-on")

    def render(self) -> RenderableType:
        style = self.get_component_rich_style("checkbox--switch")
        return ScrollBarRender(
            virtual_size=100,
            window_size=50,
            position=self.slider_pos * 50,
            style=style,
            vertical=False,
        )

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return 4

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return 1

    def on_click(self) -> None:
        self.toggle()

    def action_toggle(self) -> None:
        self.toggle()

    def toggle(self) -> None:
        """Toggle the checkbox value. As a result of the value changing,
        a Checkbox.Changed message will be emitted."""
        self.value = not self.value

    class Changed(Message, bubble=True):
        """Checkbox was toggled."""

        def __init__(self, sender: Checkbox, value: bool) -> None:
            super().__init__(sender)
            self.value = value
            self.input = sender
