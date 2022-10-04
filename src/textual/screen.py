from __future__ import annotations

import sys
from typing import Iterable

import rich.repr
from rich.console import RenderableType
from rich.style import Style

from . import errors, events, messages
from ._callback import invoke
from ._compositor import Compositor, MapGeometry
from .timer import Timer
from ._types import CallbackType
from .geometry import Offset, Region, Size
from .reactive import Reactive
from .renderables.blank import Blank
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

    DEFAULT_CSS = """
    Screen {
        layout: vertical;
        overflow-y: auto;
        background: $surface;
    }
    """

    dark: Reactive[bool] = Reactive(False)

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._compositor = Compositor()
        self._dirty_widgets: set[Widget] = set()
        self._update_timer: Timer | None = None
        self._callbacks: list[CallbackType] = []

    @property
    def is_transparent(self) -> bool:
        return False

    @property
    def is_current(self) -> bool:
        """Check if this screen is current (i.e. visible to user)."""
        return self.app.screen is self

    @property
    def update_timer(self) -> Timer:
        """Timer used to perform updates."""
        if self._update_timer is None:
            self._update_timer = self.set_interval(
                UPDATE_PERIOD, self._on_timer_update, name="screen_update", pause=True
            )
        return self._update_timer

    @property
    def widgets(self) -> list[Widget]:
        """Get all widgets."""
        return list(self._compositor.map.keys())

    @property
    def visible_widgets(self) -> list[Widget]:
        """Get a list of visible widgets."""
        return list(self._compositor.visible_widgets)

    def watch_dark(self, dark: bool) -> None:
        pass

    def render(self) -> RenderableType:
        background = self.styles.background
        if background.is_transparent:
            return self.app.render()
        return Blank(background)

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

    def get_widgets_at(self, x: int, y: int) -> Iterable[tuple[Widget, Region]]:
        """Get all widgets under a given coordinate.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            Iterable[tuple[Widget, Region]]: Sequence of (WIDGET, REGION) tuples.
        """
        return self._compositor.get_widgets_at(x, y)

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

    async def _on_idle(self, event: events.Idle) -> None:
        # Check for any widgets marked as 'dirty' (needs a repaint)
        event.prevent_default()

        if self.is_current:
            if self._layout_required:
                self._refresh_layout()
                self._layout_required = False
                self._dirty_widgets.clear()
            if self._repaint_required:
                self._dirty_widgets.clear()
                self._dirty_widgets.add(self)
                self._repaint_required = False

            if self._dirty_widgets:
                self.update_timer.resume()

        # The Screen is idle - a good opportunity to invoke the scheduled callbacks
        await self._invoke_and_clear_callbacks()

    def _on_timer_update(self) -> None:
        """Called by the _update_timer."""
        # Render widgets together
        if self._dirty_widgets:
            self._compositor.update_widgets(self._dirty_widgets)
            self.app._display(self, self._compositor.render())
            self._dirty_widgets.clear()

        self.update_timer.pause()
        if self._callbacks:
            self.post_message_no_wait(events.InvokeCallbacks(self))

    async def _on_invoke_callbacks(self, event: events.InvokeCallbacks) -> None:
        """Handle PostScreenUpdate events, which are sent after the screen is updated"""
        await self._invoke_and_clear_callbacks()

    async def _invoke_and_clear_callbacks(self) -> None:
        """If there are scheduled callbacks to run, call them and clear
        the callback queue."""
        if self._callbacks:
            callbacks = self._callbacks[:]
            self._callbacks.clear()
            for callback in callbacks:
                await invoke(callback)

    def _invoke_later(self, callback: CallbackType) -> None:
        """Enqueue a callback to be invoked after the screen is repainted.

        Args:
            callback (CallbackType): A callback.
        """

        self._callbacks.append(callback)
        self.check_idle()

    def _refresh_layout(self, size: Size | None = None, full: bool = False) -> None:
        """Refresh the layout (can change size and positions of widgets)."""
        size = self.outer_size if size is None else size
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
            ResizeEvent = events.Resize

            layers = self._compositor.layers
            for widget, (
                region,
                _order,
                _clip,
                virtual_size,
                container_size,
                _,
            ) in layers:
                widget._size_updated(region.size, virtual_size, container_size)
                if widget in send_resize:
                    widget.post_message_no_wait(
                        ResizeEvent(self, region.size, virtual_size, container_size)
                    )

        except Exception as error:
            self.app._handle_exception(error)
            return
        display_update = self._compositor.render(full=full)
        if display_update is not None:
            self.app._display(self, display_update)

    async def _on_update(self, message: messages.Update) -> None:
        message.stop()
        message.prevent_default()
        widget = message.widget
        assert isinstance(widget, Widget)
        self._dirty_widgets.add(widget)
        self.check_idle()

    async def _on_layout(self, message: messages.Layout) -> None:
        message.stop()
        message.prevent_default()
        self._layout_required = True
        self.check_idle()

    def _screen_resized(self, size: Size):
        """Called by App when the screen is resized."""
        self._refresh_layout(size, full=True)

    def _on_screen_resume(self) -> None:
        """Called by the App"""

        size = self.app.size
        self._refresh_layout(size, full=True)

    async def _on_resize(self, event: events.Resize) -> None:
        event.stop()

    async def _handle_mouse_move(self, event: events.MouseMove) -> None:
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
            widget.hover_style = event.style
            mouse_event._set_forwarded()
            await widget._forward_event(mouse_event)

    async def _forward_event(self, event: events.Event) -> None:
        if event.is_forwarded:
            return
        event._set_forwarded()
        if isinstance(event, (events.Enter, events.Leave)):
            await self.post_message(event)

        elif isinstance(event, events.MouseMove):
            event.style = self.get_style_at(event.screen_x, event.screen_y)
            await self._handle_mouse_move(event)

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
                if isinstance(event, events.MouseUp) and widget.can_focus:
                    if self.app.focused is not widget:
                        self.app.set_focus(widget)
                        event.stop()
                        return
                event.style = self.get_style_at(event.screen_x, event.screen_y)
                if widget is self:
                    event._set_forwarded()
                    await self.post_message(event)
                else:
                    await widget._forward_event(
                        event._apply_offset(-region.x, -region.y)
                    )

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
                    await scroll_widget._forward_event(event)
        else:
            await self.post_message(event)
