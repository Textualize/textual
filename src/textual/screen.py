from __future__ import annotations

import sys

from rich.console import RenderableType
import rich.repr
from rich.style import Style


from . import events, messages, errors

from .geometry import Offset, Region, Size
from ._compositor import Compositor, MapGeometry
from .reactive import Reactive
from .renderables.blank import Blank
from ._timer import Timer
from .widget import Widget

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

# Screen updates will be batched so that they don't happen more often than 60 times per second:
UPDATE_PERIOD: Final = 1 / 60


@rich.repr.auto
class Screen(Widget):
    """A widget for the root of the app."""

    CSS = """
    Screen {
            
        layout: vertical;
        overflow-y: auto;
    }
    """

    dark = Reactive(False)

    def __init__(self, name: str | None = None, id: str | None = None) -> None:
        super().__init__(name=name, id=id)
        self._compositor = Compositor()
        self._dirty_widgets: set[Widget] = set()
        self._update_timer: Timer | None = None

    @property
    def is_transparent(self) -> bool:
        return False

    @property
    def update_timer(self) -> Timer:
        """Timer used to perform updates."""
        if self._update_timer is None:
            self._update_timer = self.set_interval(
                UPDATE_PERIOD, self._on_update, name="screen_update", pause=True
            )
        return self._update_timer

    def watch_dark(self, dark: bool) -> None:
        pass

    def render(self) -> RenderableType:
        return Blank()

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

    def find_widget(self, widget: Widget) -> MapGeometry:
        """Get the screen region of a Widget.

        Args:
            widget (Widget): A Widget within the composition.

        Returns:
            Region: Region relative to screen.
        """
        return self._compositor.find_widget(widget)

    def on_idle(self, event: events.Idle) -> None:
        # Check for any widgets marked as 'dirty' (needs a repaint)
        event.prevent_default()
        if self._layout_required:
            self._refresh_layout()
            self._layout_required = False
            self._dirty_widgets.clear()
        elif self._dirty_widgets or self._dirty_regions:
            self.update_timer.resume()

    def _on_update(self) -> None:
        """Called by the _update_timer."""
        # Render widgets together
        if self._dirty_widgets or self._dirty_regions:
            self._compositor.update_widgets(self._dirty_widgets)
            self._compositor.add_dirty_regions(self._dirty_regions)
            self.app._display(self._compositor.render())
            self._dirty_widgets.clear()
        self.update_timer.pause()

    def _refresh_layout(self, size: Size | None = None, full: bool = False) -> None:
        """Refresh the layout (can change size and positions of widgets)."""
        size = self.size if size is None else size
        if not size:
            return

        self._compositor.update_widgets(self._dirty_widgets)
        self.update_timer.pause()
        try:
            hidden, shown, resized = self._compositor.reflow(self, size)

            Hide = events.Hide
            Show = events.Show
            for widget in hidden:
                widget.post_message_no_wait(Hide(self))
            for widget in shown:
                widget.post_message_no_wait(Show(self))

            # We want to send a resize event to widgets that were just added or change since last layout
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
        except Exception as error:
            self.app.on_exception(error)
            return
        display_update = self._compositor.render(full=full)
        if display_update is not None:
            self.app._display(display_update)

    async def handle_update(self, message: messages.Update) -> None:
        message.stop()
        message.prevent_default()
        widget = message.widget
        assert isinstance(widget, Widget)
        self._dirty_widgets.add(widget)
        self.check_idle()

    async def handle_layout(self, message: messages.Layout) -> None:
        message.stop()
        message.prevent_default()
        self._layout_required = True
        self.check_idle()

    def _screen_resized(self, size: Size):
        """Called by App when the screen is resized."""
        self._refresh_layout(size, full=True)

    async def on_resize(self, event: events.Resize) -> None:
        event.stop()

    async def _on_mouse_move(self, event: events.MouseMove) -> None:
        try:
            if self.app.mouse_captured:
                widget = self.app.mouse_captured
                region = self.find_widget(widget).region
            else:
                widget, region = self.get_widget_at(event.x, event.y)
        except errors.NoWidget:
            await self.app._set_mouse_over(None)
        else:
            await self.app._set_mouse_over(widget)
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
                    region = self.find_widget(widget).region
                else:
                    widget, region = self.get_widget_at(event.x, event.y)
            except errors.NoWidget:
                self.app.set_focus(None)
            else:
                if isinstance(event, events.MouseDown) and widget.can_focus:
                    self.app.set_focus(widget)
                event.style = self.get_style_at(event.screen_x, event.screen_y)
                if widget is self:
                    event.set_forwarded()
                    await self.post_message(event)
                else:
                    await widget.forward_event(event.offset(-region.x, -region.y))

        elif isinstance(event, (events.MouseScrollDown, events.MouseScrollUp)):
            try:
                widget, _region = self.get_widget_at(event.x, event.y)
            except errors.NoWidget:
                return
            scroll_widget = widget
            if scroll_widget is not None:
                if scroll_widget is self:
                    await self.post_message(event)
                else:
                    await scroll_widget.forward_event(event)
        else:
            await self.post_message(event)
