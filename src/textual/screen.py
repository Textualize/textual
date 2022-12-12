from __future__ import annotations

from typing import Iterable, Iterator

import rich.repr
from rich.console import RenderableType
from rich.style import Style

from . import errors, events, messages
from ._callback import invoke
from ._compositor import Compositor, MapGeometry
from .timer import Timer
from ._types import CallbackType
from .geometry import Offset, Region, Size
from ._typing import Final
from .reactive import Reactive
from .renderables.blank import Blank
from .widget import Widget


# Screen updates will be batched so that they don't happen more often than 120 times per second:
UPDATE_PERIOD: Final[float] = 1 / 120


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

    focused: Reactive[Widget | None] = Reactive(None)

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
        self._max_idle = UPDATE_PERIOD

    @property
    def is_transparent(self) -> bool:
        return False

    @property
    def is_current(self) -> bool:
        """Check if this screen is current (i.e. visible to user)."""
        from .app import ScreenStackError

        try:
            return self.app.screen is self
        except ScreenStackError:
            return False

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

        Raises:
            NoWidget: If the widget could not be found in this screen.
        """
        return self._compositor.find_widget(widget)

    @property
    def focus_chain(self) -> list[Widget]:
        """Get widgets that may receive focus, in focus order.

        Returns:
            list[Widget]: List of Widgets in focus order.
        """
        widgets: list[Widget] = []
        add_widget = widgets.append
        stack: list[Iterator[Widget]] = [iter(self.focusable_children)]
        pop = stack.pop
        push = stack.append

        while stack:
            node = next(stack[-1], None)
            if node is None:
                pop()
            else:
                if node.is_container and node.can_focus_children:
                    push(iter(node.focusable_children))
                if node.can_focus:
                    add_widget(node)

        return widgets

    def _move_focus(self, direction: int = 0) -> Widget | None:
        """Move the focus in the given direction.

        Args:
            direction (int, optional): 1 to move forward, -1 to move backward, or
                0 to keep the current focus.

        Returns:
            Widget | None: Newly focused widget, or None for no focus.
        """
        focusable_widgets = self.focus_chain

        if not focusable_widgets:
            # Nothing focusable, so nothing to do
            return self.focused
        if self.focused is None:
            # Nothing currently focused, so focus the first one
            self.set_focus(focusable_widgets[0])
        else:
            try:
                # Find the index of the currently focused widget
                current_index = focusable_widgets.index(self.focused)
            except ValueError:
                # Focused widget was removed in the interim, start again
                self.set_focus(focusable_widgets[0])
            else:
                # Only move the focus if we are currently showing the focus
                if direction:
                    current_index = (current_index + direction) % len(focusable_widgets)
                    self.set_focus(focusable_widgets[current_index])

        return self.focused

    def focus_next(self) -> Widget | None:
        """Focus the next widget.

        Returns:
            Widget | None: Newly focused widget, or None for no focus.
        """
        return self._move_focus(1)

    def focus_previous(self) -> Widget | None:
        """Focus the previous widget.

        Returns:
            Widget | None: Newly focused widget, or None for no focus.
        """
        return self._move_focus(-1)

    def _reset_focus(
        self, widget: Widget, avoiding: list[Widget] | None = None
    ) -> None:
        """Reset the focus when a widget is removed

        Args:
            widget (Widget): A widget that is removed.
            avoiding (list[DOMNode] | None, optional): Optional list of nodes to avoid.
        """

        avoiding = avoiding or []

        # Make this a NOP if we're being asked to deal with a widget that
        # isn't actually the currently-focused widget.
        if self.focused is not widget:
            return

        # Grab the list of widgets that we can set focus to.
        focusable_widgets = self.focus_chain
        if not focusable_widgets:
            # If there's nothing to focus... give up now.
            return

        try:
            # Find the location of the widget we're taking focus from, in
            # the focus chain.
            widget_index = focusable_widgets.index(widget)
        except ValueError:
            # widget is not in focusable widgets
            # It may have been made invisible
            # Move to a sibling if possible
            for sibling in widget.visible_siblings:
                if sibling not in avoiding and sibling.can_focus:
                    self.set_focus(sibling)
                    break
            else:
                self.set_focus(None)
            return

        # Now go looking for something before it, that isn't about to be
        # removed, and which can receive focus, and go focus that.
        chosen: Widget | None = None
        for candidate in reversed(
            focusable_widgets[widget_index + 1 :] + focusable_widgets[:widget_index]
        ):
            if candidate not in avoiding:
                chosen = candidate
                break

        # Go with the what was found.
        self.set_focus(chosen)

    def set_focus(self, widget: Widget | None, scroll_visible: bool = True) -> None:
        """Focus (or un-focus) a widget. A focused widget will receive key events first.

        Args:
            widget (Widget | None): Widget to focus, or None to un-focus.
            scroll_visible (bool, optional): Scroll widget in to view.
        """
        if widget is self.focused:
            # Widget is already focused
            return

        if widget is None:
            # No focus, so blur currently focused widget if it exists
            if self.focused is not None:
                self.focused.post_message_no_wait(events.Blur(self))
                self.focused.emit_no_wait(events.DescendantBlur(self))
                self.focused = None
        elif widget.can_focus:
            if self.focused != widget:
                if self.focused is not None:
                    # Blur currently focused widget
                    self.focused.post_message_no_wait(events.Blur(self))
                    self.focused.emit_no_wait(events.DescendantBlur(self))
                # Change focus
                self.focused = widget
                # Send focus event
                if scroll_visible:
                    self.screen.scroll_to_widget(widget)
                widget.post_message_no_wait(events.Focus(self))
                widget.emit_no_wait(events.DescendantFocus(self))

    async def _on_idle(self, event: events.Idle) -> None:
        # Check for any widgets marked as 'dirty' (needs a repaint)
        event.prevent_default()

        async with self.app._dom_lock:
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
        if self._callbacks:
            self.post_message_no_wait(events.InvokeCallbacks(self))

        self.update_timer.pause()

    async def _on_invoke_callbacks(self, event: events.InvokeCallbacks) -> None:
        """Handle PostScreenUpdate events, which are sent after the screen is updated"""
        await self._invoke_and_clear_callbacks()

    async def _invoke_and_clear_callbacks(self) -> None:
        """If there are scheduled callbacks to run, call them and clear
        the callback queue."""
        if self._callbacks:
            display_update = self._compositor.render()
            self.app._display(self, display_update)
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

            for widget in shown:
                widget.post_message_no_wait(Show(self))

        except Exception as error:
            self.app._handle_exception(error)
            return
        display_update = self._compositor.render(full=full)
        self.app._display(self, display_update)
        if not self.app._dom_ready:
            self.app.post_message_no_wait(events.Ready(self))
            self.app._dom_ready = True

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
        self._screen_resized(event.size)

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
                self.set_focus(None)
            else:
                if isinstance(event, events.MouseUp) and widget.can_focus:
                    if self.focused is not widget:
                        self.set_focus(widget)
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
