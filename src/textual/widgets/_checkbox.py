from __future__ import annotations

from rich.console import RenderableType


from .. import events
from ..geometry import Size
from ..reactive import reactive
from ..widget import Widget
from ..scrollbar import ScrollBarRender


class Checkbox(Widget, can_focus=True):
    DEFAULT_CSS = """
    
    Checkbox {
        border: tall transparent;
        background: $panel ;
        height: 1;
        width: 10;
        padding: 0 2;
    }


    Checkbox > .checkbox--switch {
        background: $panel-darken-2;
        color: $panel-lighten-2;
    }

    Checkbox:hover {
        border: tall $background !important;
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

    COMPONENT_CLASSES = {
        "checkbox--switch",
    }

    on = reactive(False)
    slider_pos = reactive(0.0)

    def watch_on(self, on: bool) -> None:
        self.animate("slider_pos", 1.0 if on else 0.0, duration=0.3)

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

    def on_click(self, event: events.Click) -> None:
        self.on = not self.on
