from __future__ import annotations

from logging import getLogger
from typing import (
    Any,
    Awaitable,
    TYPE_CHECKING,
    Callable,
    ClassVar,
    Iterable,
    NamedTuple,
    cast,
)

import rich.repr
from rich.align import Align
from rich.console import Console, RenderableType
from rich.padding import Padding
from rich.pretty import Pretty
from rich.style import Style
from rich.styled import Styled
from rich.text import Text

from . import errors, log
from . import events
from ._animator import BoundAnimator
from ._border import Border
from ._callback import invoke
from ._context import active_app
from ._types import Lines
from .dom import DOMNode
from .geometry import Offset, Region, Size
from .message import Message
from . import messages
from .layout import Layout
from .reactive import Reactive, watch
from .renderables.opacity import Opacity

if TYPE_CHECKING:
    from .screen import Screen


class RenderCache(NamedTuple):
    size: Size
    lines: Lines

    @property
    def cursor_line(self) -> int | None:
        for index, line in enumerate(self.lines):
            for _text, style, _control in line:
                if style and style._meta and style.meta.get("cursor", False):
                    return index
        return None


@rich.repr.auto
class Widget(DOMNode):

    can_focus: bool = False

    DEFAULT_STYLES = """
        
    """

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: set[str] | None = None,
    ) -> None:

        self._size = Size(0, 0)
        self._repaint_required = False
        self._layout_required = False
        self._animate: BoundAnimator | None = None
        self._reactive_watches: dict[str, Callable] = {}
        self._mouse_over: bool = False
        self.render_cache: RenderCache | None = None
        self.highlight_style: Style | None = None

        super().__init__(name=name, id=id, classes=classes)
        self.add_children(*children)

    has_focus = Reactive(False)
    mouse_over = Reactive(False)
    scroll_x = Reactive(0)
    scroll_y = Reactive(0)
    virtual_size = Reactive(Size(0, 0))

    def __init_subclass__(cls, can_focus: bool = True) -> None:
        super().__init_subclass__()
        cls.can_focus = can_focus

    def __rich_repr__(self) -> rich.repr.Result:
        yield "id", self.id, None
        if self.name:
            yield "name", self.name
        if self.classes:
            yield "classes", set(self.classes)
        pseudo_classes = self.pseudo_classes
        if pseudo_classes:
            yield "pseudo_classes", set(pseudo_classes)

    def get_pseudo_classes(self) -> Iterable[str]:
        """Pseudo classes for a widget"""
        if self._mouse_over:
            yield "hover"
        if self.has_focus:
            yield "focus"
        # TODO: focus

    def watch(self, attribute_name, callback: Callable[[Any], Awaitable[None]]) -> None:
        watch(self, attribute_name, callback)

    def render_styled(self) -> RenderableType:
        """Applies style attributes to the default renderable.

        Returns:
            RenderableType: A new renderable.
        """

        renderable = self.render()
        styles = self.styles

        parent_text_style = self.parent.text_style

        text_style = styles.text
        renderable_text_style = parent_text_style + text_style
        if renderable_text_style:
            renderable = Styled(renderable, renderable_text_style)

        if styles.padding:
            renderable = Padding(
                renderable, styles.padding, style=renderable_text_style
            )

        if styles.border:
            renderable = Border(renderable, styles.border, style=renderable_text_style)

        if styles.outline:
            renderable = Border(
                renderable,
                styles.outline,
                outline=True,
                style=renderable_text_style,
            )

        if styles.opacity:
            renderable = Opacity(renderable, opacity=styles.opacity)

        return renderable

    @property
    def children(self) -> list[Widget]:
        return cast(list[Widget], list(self.node_list))

    @property
    def size(self) -> Size:
        return self._size

    @property
    def virtual_size(self) -> Size:
        return self._virtual_size

    @property
    def region(self) -> Region:
        return self.screen._compositor.get_widget_region(self)

    @property
    def scroll(self) -> Offset:
        return Offset(self.scroll_x, self.scroll_y)

    @property
    def is_transparent(self) -> bool:
        """Check if the background styles is not set.

        Returns:
            bool: ``True`` if there is background color, otherwise ``False``.
        """
        return self.layout is not None or self.styles.text.bgcolor is None

    @property
    def console(self) -> Console:
        """Get the current console."""
        return active_app.get().console

    @property
    def animate(self) -> BoundAnimator:
        if self._animate is None:
            self._animate = self.app.animator.bind(self)
        assert self._animate is not None
        return self._animate

    @property
    def layout(self) -> Layout | None:
        return self.styles.layout

    def watch_mouse_over(self, value: bool) -> None:
        """Update from CSS if mouse over state changes."""
        self.app.update_styles()

    def watch_has_focus(self, value: bool) -> None:
        """Update from CSS if has focus state changes."""
        self.app.update_styles()

    def on_style_change(self) -> None:
        self.clear_render_cache()

    def _update_size(self, size: Size, virtual_size: Size) -> None:
        self._size = size
        self._virtual_size = virtual_size

    def render_lines(self) -> None:
        width, height = self.size
        renderable = self.render_styled()
        options = self.console.options.update_dimensions(width, height)
        lines = self.console.render_lines(renderable, options)
        self.render_cache = RenderCache(self.size, lines)

    def _get_lines(self) -> Lines:
        """Get segment lines to render the widget."""
        if self.render_cache is None:
            self.render_lines()
        assert self.render_cache is not None
        lines = self.render_cache.lines
        return lines

    def clear_render_cache(self) -> None:
        self.render_cache = None

    def check_repaint(self) -> bool:
        return self._repaint_required

    def check_layout(self) -> bool:
        return self._layout_required

    def reset_check_repaint(self) -> None:
        self._repaint_required = False

    def reset_check_layout(self) -> None:
        self._layout_required = False

    def get_style_at(self, x: int, y: int) -> Style:
        offset_x, offset_y = self.screen.get_offset(self)
        return self.screen.get_style_at(x + offset_x, y + offset_y)

    async def call_later(self, callback: Callable, *args, **kwargs) -> None:
        await self.app.call_later(callback, *args, **kwargs)

    async def forward_event(self, event: events.Event) -> None:
        event.set_forwarded()
        await self.post_message(event)

    def refresh(self, *, repaint: bool = True, layout: bool = False) -> None:
        """Initiate a refresh of the widget.

        This method sets an internal flag to perform a refresh, which will be done on the
        next idle event. Only one refresh will be done even if this method is called multiple times.

        Args:
            repaint (bool, optional): Repaint the widget (will call render() again). Defaults to True.
            layout (bool, optional): Also layout widgets in the view. Defaults to False.
        """
        if layout:
            self.clear_render_cache()
            self._layout_required = True
        elif repaint:
            self.clear_render_cache()
            self._repaint_required = True
        self.check_idle()

    def render(self) -> RenderableType:
        """Get renderable for widget.

        Returns:
            RenderableType: Any renderable
        """

        # Default displays a pretty repr in the center of the screen

        label = f"{self.css_identifier_styled} {self.size} {self.virtual_size}"

        return Align.center(label, vertical="middle")

    async def action(self, action: str, *params) -> None:
        await self.app.action(action, self)

    async def post_message(self, message: Message) -> bool:
        if not self.check_message_enabled(message):
            return True
        if not self.is_running:
            self.log(self, f"IS NOT RUNNING, {message!r} not sent")
        return await super().post_message(message)

    async def on_resize(self, event: events.Resize) -> None:
        self._update_size(event.size, event.virtual_size)
        self.refresh()

    async def on_idle(self, event: events.Idle) -> None:
        repaint, layout = self.styles.check_refresh()
        if layout or self.check_layout():
            # self.render_cache = None
            self.reset_check_repaint()
            self.reset_check_layout()
            await self.screen.post_message(messages.Layout(self))
        elif repaint or self.check_repaint():
            # self.render_cache = None
            self.reset_check_repaint()
            await self.emit(messages.Update(self, self))

    async def focus(self) -> None:
        """Give input focus to this widget."""
        await self.app.set_focus(self)

    async def capture_mouse(self, capture: bool = True) -> None:
        """Capture (or release) the mouse.

        When captured, all mouse coordinates will go to this widget even when the pointer is not directly over the widget.

        Args:
            capture (bool, optional): True to capture or False to release. Defaults to True.
        """
        await self.app.capture_mouse(self if capture else None)

    async def release_mouse(self) -> None:
        """Release the mouse.

        Mouse events will only be sent when the mouse is over the widget.
        """
        await self.app.capture_mouse(None)

    async def broker_event(self, event_name: str, event: events.Event) -> bool:
        return await self.app.broker_event(event_name, event, default_namespace=self)

    async def on_mouse_down(self, event: events.MouseUp) -> None:
        await self.broker_event("mouse.down", event)

    async def on_mouse_up(self, event: events.MouseUp) -> None:
        await self.broker_event("mouse.up", event)

    async def on_click(self, event: events.Click) -> None:
        await self.broker_event("click", event)

    async def on_key(self, event: events.Key) -> None:
        if await self.dispatch_key(event):
            event.prevent_default()
