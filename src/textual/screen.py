"""

The `Screen` class is a special widget which represents the content in the terminal. See [Screens](/guide/screens/) for details.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterable,
    Iterator,
    Type,
    TypeVar,
    Union,
    cast,
)

import rich.repr
from rich.console import RenderableType
from rich.style import Style

from . import errors, events, messages
from ._callback import invoke
from ._compositor import Compositor, MapGeometry
from ._context import visible_screen_stack
from ._types import CallbackType
from .binding import Binding
from .css.match import match
from .css.parse import parse_selectors
from .css.query import NoMatches, QueryType
from .dom import DOMNode
from .geometry import Offset, Region, Size
from .reactive import Reactive
from .renderables.background_screen import BackgroundScreen
from .renderables.blank import Blank
from .timer import Timer
from .widget import Widget

if TYPE_CHECKING:
    from typing_extensions import Final

    # Unused & ignored imports are needed for the docs to link to these objects:
    from .errors import NoWidget  # type: ignore  # noqa: F401

# Screen updates will be batched so that they don't happen more often than 60 times per second:
UPDATE_PERIOD: Final[float] = 1 / 60

ScreenResultType = TypeVar("ScreenResultType")
"""The result type of a screen."""

ScreenResultCallbackType = Union[
    Callable[[ScreenResultType], None], Callable[[ScreenResultType], Awaitable[None]]
]
"""Type of a screen result callback function."""


class ResultCallback(Generic[ScreenResultType]):
    """Holds the details of a callback."""

    def __init__(
        self,
        requester: Widget | None,
        callback: ScreenResultCallbackType[ScreenResultType] | None,
    ) -> None:
        """Initialise the result callback object.

        Args:
            requester: The object making a request for the callback.
            callback: The callback function.
        """
        self.requester: Widget | None = requester
        """The object in the DOM that requested the callback."""
        self.callback: ScreenResultCallbackType | None = callback
        """The callback function."""

    def __call__(self, result: ScreenResultType) -> None:
        """Call the callback, passing the given result.

        Args:
            result: The result to pass to the callback.

        Note:
            If the requested or the callback are `None` this will be a no-op.
        """
        if self.requester is not None and self.callback is not None:
            self.requester.call_next(self.callback, result)


@rich.repr.auto
class Screen(Generic[ScreenResultType], Widget):
    """The base class for screens."""

    AUTO_FOCUS: ClassVar[str | None] = "*"
    """A selector to determine what to focus automatically when the screen is activated.

    The widget focused is the first that matches the given [CSS selector](/guide/queries/#query-selectors).
    Set to `None` to disable auto focus.
    """

    DEFAULT_CSS = """
    Screen {
        layout: vertical;
        overflow-y: auto;
        background: $surface;
    }
    """
    focused: Reactive[Widget | None] = Reactive(None)
    """The focused [widget][textual.widget.Widget] or `None` for no focus."""
    stack_updates: Reactive[int] = Reactive(0, repaint=False)
    """An integer that updates when the screen is resumed."""

    BINDINGS = [
        Binding("tab", "focus_next", "Focus Next", show=False),
        Binding("shift+tab", "focus_previous", "Focus Previous", show=False),
    ]

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Initialize the screen.

        Args:
            name: The name of the screen.
            id: The ID of the screen in the DOM.
            classes: The CSS classes for the screen.
        """
        self._modal = False
        super().__init__(name=name, id=id, classes=classes)
        self._compositor = Compositor()
        self._dirty_widgets: set[Widget] = set()
        self.__update_timer: Timer | None = None
        self._callbacks: list[CallbackType] = []
        self._result_callbacks: list[ResultCallback[ScreenResultType]] = []

    @property
    def is_modal(self) -> bool:
        """Is the screen modal?"""
        return self._modal

    @property
    def is_transparent(self) -> bool:
        return False

    @property
    def is_current(self) -> bool:
        """Is the screen current (i.e. visible to user)?"""
        from .app import ScreenStackError

        try:
            return self.app.screen is self
        except ScreenStackError:
            return False

    @property
    def _update_timer(self) -> Timer:
        """Timer used to perform updates."""
        if self.__update_timer is None:
            self.__update_timer = self.set_interval(
                UPDATE_PERIOD, self._on_timer_update, name="screen_update", pause=True
            )
        return self.__update_timer

    def render(self) -> RenderableType:
        background = self.styles.background
        try:
            base_screen = visible_screen_stack.get().pop()
        except IndexError:
            base_screen = None

        if base_screen is not None and 1 > background.a > 0:
            return BackgroundScreen(base_screen, background)

        if background.is_transparent:
            return self.app.render()
        return Blank(background)

    def get_offset(self, widget: Widget) -> Offset:
        """Get the absolute offset of a given Widget.

        Args:
            widget: A widget

        Returns:
            The widget's offset relative to the top left of the terminal.
        """
        return self._compositor.get_offset(widget)

    def get_widget_at(self, x: int, y: int) -> tuple[Widget, Region]:
        """Get the widget at a given coordinate.

        Args:
            x: X Coordinate.
            y: Y Coordinate.

        Returns:
            Widget and screen region.
        """
        return self._compositor.get_widget_at(x, y)

    def get_widgets_at(self, x: int, y: int) -> Iterable[tuple[Widget, Region]]:
        """Get all widgets under a given coordinate.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            Sequence of (WIDGET, REGION) tuples.
        """
        return self._compositor.get_widgets_at(x, y)

    def get_style_at(self, x: int, y: int) -> Style:
        """Get the style under a given coordinate.

        Args:
            x: X Coordinate.
            y: Y Coordinate.

        Returns:
            Rich Style object
        """
        return self._compositor.get_style_at(x, y)

    def find_widget(self, widget: Widget) -> MapGeometry:
        """Get the screen region of a Widget.

        Args:
            widget: A Widget within the composition.

        Returns:
            Region relative to screen.

        Raises:
            NoWidget: If the widget could not be found in this screen.
        """
        return self._compositor.find_widget(widget)

    @property
    def focus_chain(self) -> list[Widget]:
        """A list of widgets that may receive focus, in focus order."""
        # TODO: Calculating a focus chain is moderately expensive.
        # Suspect we can move focus without calculating the entire thing again.

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
                if node.focusable:
                    add_widget(node)

        return widgets

    def _move_focus(
        self, direction: int = 0, selector: str | type[QueryType] = "*"
    ) -> Widget | None:
        """Move the focus in the given direction.

        If no widget is currently focused, this will focus the first focusable widget.
        If no focusable widget matches the given CSS selector, focus is set to `None`.

        Args:
            direction: 1 to move forward, -1 to move backward, or
                0 to keep the current focus.
            selector: CSS selector to filter
                what nodes can be focused.

        Returns:
            Newly focused widget, or None for no focus. If the return
                is not `None`, then it is guaranteed that the widget returned matches
                the CSS selectors given in the argument.
        """
        # TODO: This shouldn't be required
        self._compositor._full_map_invalidated = True
        if not isinstance(selector, str):
            selector = selector.__name__
        selector_set = parse_selectors(selector)
        focus_chain = self.focus_chain
        filtered_focus_chain = (
            node for node in focus_chain if match(selector_set, node)
        )

        if not focus_chain:
            # Nothing focusable, so nothing to do
            return self.focused
        if self.focused is None:
            # Nothing currently focused, so focus the first one.
            to_focus = next(filtered_focus_chain, None)
            self.set_focus(to_focus)
            return self.focused

        # Ensure focus will be in a node that matches the selectors.
        if not direction and not match(selector_set, self.focused):
            direction = 1

        try:
            # Find the index of the currently focused widget
            current_index = focus_chain.index(self.focused)
        except ValueError:
            # Focused widget was removed in the interim, start again
            self.set_focus(next(filtered_focus_chain, None))
        else:
            # Only move the focus if we are currently showing the focus
            if direction:
                to_focus = None
                chain_length = len(focus_chain)
                for step in range(1, len(focus_chain) + 1):
                    node = focus_chain[
                        (current_index + direction * step) % chain_length
                    ]
                    if match(selector_set, node):
                        to_focus = node
                        break
                self.set_focus(to_focus)

        return self.focused

    def focus_next(self, selector: str | type[QueryType] = "*") -> Widget | None:
        """Focus the next widget, optionally filtered by a CSS selector.

        If no widget is currently focused, this will focus the first focusable widget.
        If no focusable widget matches the given CSS selector, focus is set to `None`.

        Args:
            selector: CSS selector to filter
                what nodes can be focused.

        Returns:
            Newly focused widget, or None for no focus. If the return
                is not `None`, then it is guaranteed that the widget returned matches
                the CSS selectors given in the argument.
        """
        return self._move_focus(1, selector)

    def focus_previous(self, selector: str | type[QueryType] = "*") -> Widget | None:
        """Focus the previous widget, optionally filtered by a CSS selector.

        If no widget is currently focused, this will focus the first focusable widget.
        If no focusable widget matches the given CSS selector, focus is set to `None`.

        Args:
            selector: CSS selector to filter
                what nodes can be focused.

        Returns:
            Newly focused widget, or None for no focus. If the return
                is not `None`, then it is guaranteed that the widget returned matches
                the CSS selectors given in the argument.
        """
        return self._move_focus(-1, selector)

    def _reset_focus(
        self, widget: Widget, avoiding: list[Widget] | None = None
    ) -> None:
        """Reset the focus when a widget is removed

        Args:
            widget: A widget that is removed.
            avoiding: Optional list of nodes to avoid.
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
                if sibling not in avoiding and sibling.focusable:
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

    def _update_focus_styles(
        self, focused: Widget | None = None, blurred: Widget | None = None
    ) -> None:
        """Update CSS for focus changes.

        Args:
            focused: The widget that was focused.
            blurred: The widget that was blurred.
        """
        widgets: set[DOMNode] = set()

        if focused is not None:
            for widget in reversed(focused.ancestors_with_self):
                if widget._has_focus_within:
                    widgets.update(widget.walk_children(with_self=True))
                    break
        if blurred is not None:
            for widget in reversed(blurred.ancestors_with_self):
                if widget._has_focus_within:
                    widgets.update(widget.walk_children(with_self=True))
                    break
        if widgets:
            self.app.stylesheet.update_nodes(
                [widget for widget in widgets if widget._has_focus_within], animate=True
            )

    def set_focus(self, widget: Widget | None, scroll_visible: bool = True) -> None:
        """Focus (or un-focus) a widget. A focused widget will receive key events first.

        Args:
            widget: Widget to focus, or None to un-focus.
            scroll_visible: Scroll widget in to view.
        """
        if widget is self.focused:
            # Widget is already focused
            return

        focused: Widget | None = None
        blurred: Widget | None = None

        if widget is None:
            # No focus, so blur currently focused widget if it exists
            if self.focused is not None:
                self.focused.post_message(events.Blur())
                self.focused = None
                blurred = self.focused
            self.log.debug("focus was removed")
        elif widget.focusable:
            if self.focused != widget:
                if self.focused is not None:
                    # Blur currently focused widget
                    self.focused.post_message(events.Blur())
                    blurred = self.focused
                # Change focus
                self.focused = widget
                # Send focus event
                if scroll_visible:

                    def scroll_to_center(widget: Widget) -> None:
                        """Scroll to center (after a refresh)."""
                        if widget.has_focus and not self.screen.can_view(widget):
                            self.screen.scroll_to_center(widget)

                    self.call_after_refresh(scroll_to_center, widget)
                widget.post_message(events.Focus())
                focused = widget

                self.log.debug(widget, "was focused")

        self._update_focus_styles(focused, blurred)

    async def _on_idle(self, event: events.Idle) -> None:
        # Check for any widgets marked as 'dirty' (needs a repaint)
        event.prevent_default()

        if not self.app._batch_count and self.is_current:
            if (
                self._layout_required
                or self._scroll_required
                or self._repaint_required
                or self._dirty_widgets
            ):
                self._update_timer.resume()
                return

        await self._invoke_and_clear_callbacks()

    def _on_timer_update(self) -> None:
        """Called by the _update_timer."""
        self._update_timer.pause()
        if self.is_current:
            if self._layout_required:
                self._refresh_layout()
                self._layout_required = False
                self._scroll_required = False
                self._dirty_widgets.clear()
            elif self._scroll_required:
                self._refresh_layout(scroll=True)
                self._scroll_required = False

            if self._repaint_required:
                self._dirty_widgets.clear()
                self._dirty_widgets.add(self)
                self._repaint_required = False

            if self._dirty_widgets:
                self._compositor.update_widgets(self._dirty_widgets)
                update = self._compositor.render_update(
                    screen_stack=self.app._background_screens
                )
                self.app._display(self, update)
                self._dirty_widgets.clear()

        if self._callbacks:
            self.call_next(self._invoke_and_clear_callbacks)

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
            callback: A callback.
        """

        self._callbacks.append(callback)
        self.check_idle()

    def _push_result_callback(
        self,
        requester: Widget | None,
        callback: ScreenResultCallbackType[ScreenResultType] | None,
    ) -> None:
        """Add a result callback to the screen.

        Args:
            requester: The object requesting the callback.
            callback: The callback.
        """
        self._result_callbacks.append(
            ResultCallback[ScreenResultType](requester, callback)
        )

    def _pop_result_callback(self) -> None:
        """Remove the latest result callback from the stack."""
        self._result_callbacks.pop()

    def _refresh_layout(
        self, size: Size | None = None, full: bool = False, scroll: bool = False
    ) -> None:
        """Refresh the layout (can change size and positions of widgets)."""
        size = self.outer_size if size is None else size
        if not size:
            return
        self._compositor.update_widgets(self._dirty_widgets)
        self._update_timer.pause()
        ResizeEvent = events.Resize

        try:
            if scroll:
                exposed_widgets = self._compositor.reflow_visible(self, size)
                if exposed_widgets:
                    layers = self._compositor.layers
                    for widget, (
                        region,
                        _order,
                        _clip,
                        virtual_size,
                        container_size,
                        _,
                        _,
                    ) in layers:
                        if widget in exposed_widgets:
                            if widget._size_updated(
                                region.size, virtual_size, container_size, layout=False
                            ):
                                widget.post_message(
                                    ResizeEvent(
                                        region.size, virtual_size, container_size
                                    )
                                )

            else:
                hidden, shown, resized = self._compositor.reflow(self, size)
                Hide = events.Hide
                Show = events.Show

                for widget in hidden:
                    widget.post_message(Hide())

                # We want to send a resize event to widgets that were just added or change since last layout
                send_resize = shown | resized

                layers = self._compositor.layers
                for widget, (
                    region,
                    _order,
                    _clip,
                    virtual_size,
                    container_size,
                    _,
                    _,
                ) in layers:
                    widget._size_updated(region.size, virtual_size, container_size)
                    if widget in send_resize:
                        widget.post_message(
                            ResizeEvent(region.size, virtual_size, container_size)
                        )

                for widget in shown:
                    widget.post_message(Show())

        except Exception as error:
            self.app._handle_exception(error)
            return
        if self.is_current:
            display_update = self._compositor.render_update(
                full=full, screen_stack=self.app._background_screens
            )
            self.app._display(self, display_update)

        if not self.app._dom_ready:
            self.app.post_message(events.Ready())
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

    async def _on_update_scroll(self, message: messages.UpdateScroll) -> None:
        message.stop()
        message.prevent_default()
        self._scroll_required = True
        self.check_idle()

    def _screen_resized(self, size: Size):
        """Called by App when the screen is resized."""
        self._refresh_layout(size, full=True)
        self.refresh()

    def _on_screen_resume(self) -> None:
        """Screen has resumed."""
        self.stack_updates += 1
        size = self.app.size
        self._refresh_layout(size, full=True)
        self.refresh()
        if self.AUTO_FOCUS is not None and self.focused is None:
            for widget in self.query(self.AUTO_FOCUS):
                if widget.focusable:
                    self.set_focus(widget)
                    break

    def _on_screen_suspend(self) -> None:
        """Screen has suspended."""
        self.app._set_mouse_over(None)
        self.stack_updates += 1

    async def _on_resize(self, event: events.Resize) -> None:
        event.stop()
        self._screen_resized(event.size)
        for screen in self.app._background_screens:
            screen._screen_resized(event.size)

    def _handle_mouse_move(self, event: events.MouseMove) -> None:
        try:
            if self.app.mouse_captured:
                widget = self.app.mouse_captured
                region = self.find_widget(widget).region
            else:
                widget, region = self.get_widget_at(event.x, event.y)
        except errors.NoWidget:
            self.app._set_mouse_over(None)
        else:
            self.app._set_mouse_over(widget)
            mouse_event = events.MouseMove(
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
            widget._forward_event(mouse_event)

    def _forward_event(self, event: events.Event) -> None:
        if event.is_forwarded:
            return
        event._set_forwarded()
        if isinstance(event, (events.Enter, events.Leave)):
            self.post_message(event)

        elif isinstance(event, events.MouseMove):
            event.style = self.get_style_at(event.screen_x, event.screen_y)
            self._handle_mouse_move(event)

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
                if isinstance(event, events.MouseUp) and widget.focusable:
                    if self.focused is not widget:
                        self.set_focus(widget)
                        event.stop()
                        return
                event.style = self.get_style_at(event.screen_x, event.screen_y)
                if widget is self:
                    event._set_forwarded()
                    self.post_message(event)
                else:
                    widget._forward_event(event._apply_offset(-region.x, -region.y))

        elif isinstance(event, (events.MouseScrollDown, events.MouseScrollUp)):
            try:
                widget, _region = self.get_widget_at(event.x, event.y)
            except errors.NoWidget:
                return
            scroll_widget = widget
            if scroll_widget is not None:
                if scroll_widget is self:
                    self.post_message(event)
                else:
                    scroll_widget._forward_event(event)
        else:
            self.post_message(event)

    class _NoResult:
        """Class used to mark that there is no result."""

    def dismiss(self, result: ScreenResultType | Type[_NoResult] = _NoResult) -> None:
        """Dismiss the screen, optionally with a result.

        If `result` is provided and a callback was set when the screen was [pushed][textual.app.push_screen], then
        the callback will be invoked with `result`.

        Args:
            result: The optional result to be passed to the result callback.

        Raises:
            ScreenStackError: If trying to dismiss a screen that is not at the top of
                the stack.

        """
        if self is not self.app.screen:
            from .app import ScreenStackError

            raise ScreenStackError(
                f"Can't dismiss screen {self} that's not at the top of the stack."
            )
        if result is not self._NoResult and self._result_callbacks:
            self._result_callbacks[-1](cast(ScreenResultType, result))
        self.app.pop_screen()

    def action_dismiss(
        self, result: ScreenResultType | Type[_NoResult] = _NoResult
    ) -> None:
        """A wrapper around [`dismiss`][textual.screen.Screen.dismiss] that can be called as an action.

        Args:
            result: The optional result to be passed to the result callback.
        """
        self.dismiss(result)


@rich.repr.auto
class ModalScreen(Screen[ScreenResultType]):
    """A screen with bindings that take precedence over the App's key bindings.

    The default styling of a modal screen will dim the screen underneath.
    """

    DEFAULT_CSS = """
    ModalScreen {
        layout: vertical;
        overflow-y: auto;
        background: $background 60%;
    }
    """

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._modal = True
