from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from ..app import RenderResult
from ..binding import Binding, BindingType
from ..events import Click
from ..geometry import Size
from ..message import Message
from ..reactive import reactive
from ..scrollbar import ScrollBarRender
from ..widget import Widget

if TYPE_CHECKING:
    from typing_extensions import Self


class Switch(Widget, can_focus=True):
    """A switch widget that represents a boolean value.

    Can be toggled by clicking on it or through its [bindings][textual.widgets.Switch.BINDINGS].

    The switch widget also contains [component classes][textual.widgets.Switch.COMPONENT_CLASSES]
    that enable more customization.
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter,space", "toggle_switch", "Toggle", show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | enter,space | Toggle the switch state. |
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "switch--slider",
    }
    """
    | Class | Description |
    | :- | :- |
    | `switch--slider` | Targets the slider of the switch. |
    """

    DEFAULT_CSS = """
    Switch {
        border: tall transparent;
        background: $boost;
        height: auto;
        width: auto;
        padding: 0 2;
    }

    Switch > .switch--slider {
        background: $panel-darken-2;
        color: $panel-lighten-2;
    }

    Switch:hover {
        border: tall $background;
    }

    Switch:focus {
        border: tall $accent;
    }

    Switch.-on {

    }

    Switch.-on > .switch--slider {
        color: $success;
    }
    """

    value: reactive[bool] = reactive(False, init=False)
    """The value of the switch; `True` for on and `False` for off."""

    slider_pos = reactive(0.0)
    """The position of the slider."""

    class Changed(Message):
        """Posted when the status of the switch changes.

        Can be handled using `on_switch_changed` in a subclass of `Switch`
        or in a parent widget in the DOM.

        Attributes:
            value: The value that the switch was changed to.
            switch: The `Switch` widget that was changed.
        """

        def __init__(self, switch: Switch, value: bool) -> None:
            super().__init__()
            self.value: bool = value
            self.switch: Switch = switch

        @property
        def control(self) -> Switch:
            """Alias for self.switch."""
            return self.switch

    def __init__(
        self,
        value: bool = False,
        *,
        animate: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Initialise the switch.

        Args:
            value: The initial value of the switch.
            animate: True if the switch should animate when toggled.
            name: The name of the switch.
            id: The ID of the switch in the DOM.
            classes: The CSS classes of the switch.
            disabled: Whether the switch is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        if value:
            self.slider_pos = 1.0
            self.set_reactive(Switch.value, value)
        self._should_animate = animate

    def watch_value(self, value: bool) -> None:
        target_slider_pos = 1.0 if value else 0.0
        if self._should_animate:
            self.animate(
                "slider_pos",
                target_slider_pos,
                duration=0.3,
                level="basic",
            )
        else:
            self.slider_pos = target_slider_pos
        self.post_message(self.Changed(self, self.value))

    def watch_slider_pos(self, slider_pos: float) -> None:
        self.set_class(slider_pos == 1, "-on")

    def render(self) -> RenderResult:
        style = self.get_component_rich_style("switch--slider")
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

    async def _on_click(self, event: Click) -> None:
        """Toggle the state of the switch."""
        event.stop()
        self.toggle()

    def action_toggle_switch(self) -> None:
        """Toggle the state of the switch."""
        self.toggle()

    def toggle(self) -> Self:
        """Toggle the switch value.

        As a result of the value changing, a `Switch.Changed` message will
        be posted.

        Returns:
            The `Switch` instance.
        """
        self.value = not self.value
        return self
