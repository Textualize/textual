from __future__ import annotations

from rich.console import RenderableType
import rich.repr
from rich.style import Style


from . import events, messages, errors

from .geometry import Offset, Region
from ._compositor import Compositor
from .widget import Widget
from .renderables.gradient import VerticalGradient


@rich.repr.auto
class Screen(Widget):
    """A widget for the root of the app."""

    DEFAULT_STYLES = """

    layout: dock
    docks: _default=top;

    """

    def __init__(self, name: str | None = None, id: str | None = None) -> None:
        super().__init__(name=name, id=id)
        self._compositor = Compositor()
        self._dirty_widgets: list[Widget] = []

    @property
    def is_transparent(self) -> bool:
        return False

    def render(self) -> RenderableType:
        return VerticalGradient("red", "blue")

    def get_offset(self, widget: Widget) -> Offset:
        """Get the absolute offset of a given Widget.

        Args:
            widget (Widget): A widget

        Returns:
            Offset: The widget's offset relative to the top left of the terminal.
        """
        return self._compositor.get_offset(widget)

    def get_widget_at(self, x: int, y: int) -> tuple[Widget, Region]:
        """Get the widget at a given coordinate.

        Args:
            x (int): X Coordinate.
            y (int): Y Coordinate.

        Returns:
            tuple[Widget, Region]: Widget and screen region.
        """
        return self._compositor.get_widget_at(x, y)

    def get_style_at(self, x: int, y: int) -> Style:
        """Get the style under a given coordinate.

        Args:
            x (int): X Coordinate.
            y (int): Y Coordinate.

        Returns:
            Style: Rich Style object
        """
        return self._compositor.get_style_at(x, y)

    def get_widget_region(self, widget: Widget) -> Region:
        """Get the screen region of a Widget.

        Args:
            widget (Widget): A Widget within the composition.

        Returns:
            Region: Region relative to screen.
        """
        return self._compositor.get_widget_region(widget)

    def on_idle(self, event: events.Idle) -> None:
        # Check for any widgets marked as 'dirty' (needs a repaint)
        if self._dirty_widgets:
            for widget in self._dirty_widgets:
                # Repaint widgets
                display_update = self._compositor.update_widget(self.console, widget)
                if display_update is not None:
                    self.app.display(display_update)
            # Reset dirty list
            self._dirty_widgets.clear()

    async def refresh_layout(self) -> None:
        """Refresh the layout (can change size and positions of widgets)."""
        if not self.size:
            return
        try:
            hidden, shown, resized = self._compositor.reflow(self, self.size)

            Hide = events.Hide
            Show = events.Show
            for widget in hidden:
                widget.post_message_no_wait(Hide(self))
            for widget in shown:
                widget.post_message_no_wait(Show(self))

            send_resize = shown | resized

            for (
                widget,
                _region,
                unclipped_region,
                virtual_size,
                container_size,
            ) in self._compositor:
                widget.size_updated(unclipped_region.size, virtual_size, container_size)
                if widget in send_resize:
                    widget.post_message_no_wait(
                        events.Resize(
                            self, unclipped_region.size, virtual_size, container_size
                        )
                    )
        except Exception:
            self.app.panic()
        self.app.refresh()
        self._dirty_widgets.clear()

    async def handle_update(self, message: messages.Update) -> None:
        message.stop()
        widget = message.widget
        assert isinstance(widget, Widget)
        self._dirty_widgets.append(widget)

    async def handle_layout(self, message: messages.Layout) -> None:
        message.stop()
        await self.refresh_layout()

    async def on_resize(self, event: events.Resize) -> None:
        self.size_updated(event.size, event.virtual_size, event.container_size)
        await self.refresh_layout()
        event.stop()

    async def _on_mouse_move(self, event: events.MouseMove) -> None:

        try:
            if self.app.mouse_captured:
                widget = self.app.mouse_captured
                region = self.get_widget_region(widget)
            else:
                widget, region = self.get_widget_at(event.x, event.y)
        except errors.NoWidget:
            await self.app.set_mouse_over(None)
        else:
            await self.app.set_mouse_over(widget)
            mouse_event = events.MouseMove(
                self,
                event.x - region.x,
                event.y - region.y,
                event.delta_x,
                event.delta_y,
                event.button,
                event.shift,
                event.meta,
                event.ctrl,
                screen_x=event.screen_x,
                screen_y=event.screen_y,
                style=event.style,
            )
            mouse_event.set_forwarded()
            await widget.forward_event(mouse_event)

    async def forward_event(self, event: events.Event) -> None:
        if event.is_forwarded:
            return
        event.set_forwarded()
        if isinstance(event, (events.Enter, events.Leave)):
            await self.post_message(event)

        elif isinstance(event, events.MouseMove):
            event.style = self.get_style_at(event.screen_x, event.screen_y)
            await self._on_mouse_move(event)

        elif isinstance(event, events.MouseEvent):
            try:
                if self.app.mouse_captured:
                    widget = self.app.mouse_captured
                    region = self.get_widget_region(widget)
                else:
                    widget, region = self.get_widget_at(event.x, event.y)
            except errors.NoWidget:
                await self.app.set_focus(None)
            else:
                if isinstance(event, events.MouseDown) and widget.can_focus:
                    await self.app.set_focus(widget)
                event.style = self.get_style_at(event.screen_x, event.screen_y)
                await widget.forward_event(event.offset(-region.x, -region.y))

        elif isinstance(event, (events.MouseScrollDown, events.MouseScrollUp)):
            try:
                widget, _region = self.get_widget_at(event.x, event.y)
            except errors.NoWidget:
                return
            self.log("forward", widget, event)
            scroll_widget = widget
            if scroll_widget is not None:
                await scroll_widget.forward_event(event)
        else:
            self.log("view.forwarded", event)
            await self.post_message(event)
