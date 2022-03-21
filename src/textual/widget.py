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
from .geometry import clamp, Offset, Region, Size
from .message import Message
from . import messages
from .layout import Layout
from .reactive import Reactive, watch
from .renderables.opacity import Opacity


if TYPE_CHECKING:
    from .scrollbar import (
        ScrollBar,
        ScrollTo,
        ScrollUp,
        ScrollDown,
        ScrollLeft,
        ScrollRight,
    )


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
        self._virtual_size = Size(0, 0)
        self._repaint_required = False
        self._layout_required = False
        self._animate: BoundAnimator | None = None
        self._reactive_watches: dict[str, Callable] = {}
        self._mouse_over: bool = False
        self.render_cache: RenderCache | None = None
        self.highlight_style: Style | None = None

        self._vertical_scrollbar: ScrollBar | None = None
        self._horizontal_scrollbar: ScrollBar | None = None

        super().__init__(name=name, id=id, classes=classes)
        self.add_children(*children)

    has_focus = Reactive(False)
    mouse_over = Reactive(False)
    scroll_x = Reactive(0.0)
    scroll_y = Reactive(0.0)
    scroll_target_x = Reactive(0.0)
    scroll_target_y = Reactive(0.0)
    show_vertical_scrollbar = Reactive(False, layout=True)
    show_horizontal_scrollbar = Reactive(False, layout=True)

    async def watch_scroll_x(self, new_value: float) -> None:
        self.hscroll.position = int(new_value)

    async def watch_scroll_y(self, new_value: float) -> None:
        self.vscroll.position = int(new_value)

    def validate_scroll_x(self, value: float) -> float:
        return clamp(value, 0, self.max_scroll_x)

    def validate_scroll_target_x(self, value: float) -> float:
        return clamp(value, 0, self.max_scroll_x)

    def validate_scroll_y(self, value: float) -> float:
        return clamp(value, 0, self.max_scroll_y)

    def validate_scroll_target_y(self, value: float) -> float:
        return clamp(value, 0, self.max_scroll_y)

    @property
    def max_scroll_x(self) -> float:
        return max(0, self.virtual_size.width - self.scroll_size.width)

    @property
    def max_scroll_y(self) -> float:
        return max(0, self.virtual_size.height - self.scroll_size.height)

    @property
    def vscroll(self) -> ScrollBar:
        """Get a vertical scrollbar (create if necessary)

        Returns:
            ScrollBar: ScrollBar Widget.
        """
        from .scrollbar import ScrollBar

        if self._vertical_scrollbar is not None:
            return self._vertical_scrollbar
        self._vertical_scrollbar = scroll_bar = ScrollBar(
            vertical=True, name="vertical"
        )
        self.app.start_widget(self, scroll_bar)
        return scroll_bar

    @property
    def hscroll(self) -> ScrollBar:
        """Get a vertical scrollbar (create if necessary)

        Returns:
            ScrollBar: ScrollBar Widget.
        """
        from .scrollbar import ScrollBar

        if self._horizontal_scrollbar is not None:
            return self._horizontal_scrollbar
        self._horizontal_scrollbar = scroll_bar = ScrollBar(
            vertical=False, name="horizontal"
        )

        self.app.start_widget(self, scroll_bar)
        return scroll_bar

    def _refresh_scrollbars(self) -> None:
        """Refresh scrollbar visibility."""
        if not self.is_container:
            return
        styles = self.styles
        overflow_x = styles.overflow_x
        overflow_y = styles.overflow_y

        if overflow_x == "hidden":
            self.show_horizontal_scrollbar = False
        elif overflow_x == "scroll":
            self.show_horizontal_scrollbar = True
        elif overflow_x == "auto":
            self.show_horizontal_scrollbar = (
                self.virtual_size.width > self.scroll_size.width
            )

        if overflow_y == "hidden":
            self.show_vertical_scrollbar = False
        elif overflow_y == "scroll":
            self.show_vertical_scrollbar = True
        elif overflow_y == "auto":
            self.show_vertical_scrollbar = (
                self.virtual_size.height > self.scroll_size.height
            )
        self.log(
            "REFRESH_SCROLLBARS",
            self,
            self.virtual_size.height,
            self.scroll_size.height,
        )

    @property
    def scrollbars_enabled(self) -> tuple[bool, bool]:
        """A tuple of booleans that indicate if scrollbars are enabled.

        Returns:
            tuple[bool, bool]: A tuple of (<vertical scrollbar enabled>, <horizontal scrollbar enabled>)

        """
        if self.layout is None:
            return False, False
        return self.show_vertical_scrollbar, self.show_horizontal_scrollbar

    def scroll_to(
        self,
        x: float | None = None,
        y: float | None = None,
        *,
        animate: bool = True,
    ):
        """Scroll to a given (absolute) coordinate, optionally animating.

        Args:
            scroll_x (int | None, optional): X coordinate (column) to scroll to, or ``None`` for no change. Defaults to None.
            scroll_y (int | None, optional): Y coordinate (row) to scroll to, or ``None`` for no change. Defaults to None.
            animate (bool, optional): Animate to new scroll position. Defaults to False.
        """

        self.log(
            "scroll_to", x=x, y=y, max_x=self.max_scroll_x, max_y=self.max_scroll_y
        )

        if animate:
            # TODO: configure animation speed
            if x is not None:
                self.scroll_target_x = x
                self.animate(
                    "scroll_x", self.scroll_target_x, speed=80, easing="out_cubic"
                )
            if y is not None:
                self.scroll_target_y = y
                self.animate(
                    "scroll_y", self.scroll_target_y, speed=80, easing="out_cubic"
                )

        else:
            if x is not None:
                self.scroll_target_x = self.scroll_x = x
            if y is not None:
                self.scroll_target_y = self.scroll_y = y
            self.refresh(layout=True)

    def scroll_home(self, animate: bool = True) -> None:
        self.scroll_to(0, 0, animate=animate)

    def scroll_end(self, animate: bool = True) -> None:
        self.scroll_to(0, self.max_scroll_y, animate=animate)

    def scroll_left(self, animate: bool = True) -> None:
        self.scroll_to(x=self.scroll_target_x - 1.5, animate=animate)

    def scroll_right(self, animate: bool = True) -> None:
        self.scroll_to(x=self.scroll_target_x + 1.5, animate=animate)

    def scroll_up(self, animate: bool = True) -> None:
        self.scroll_to(y=self.scroll_target_y + 1.5, animate=animate)

    def scroll_down(self, animate: bool = True) -> None:
        self.scroll_to(y=self.scroll_target_y - 1.5, animate=animate)

    def scroll_page_up(self, animate: bool = True) -> None:
        self.scroll_to(
            y=self.scroll_target_y - self.scroll_size.height, animate=animate
        )

    def scroll_page_down(self, animate: bool = True) -> None:
        self.scroll_to(
            y=self.scroll_target_y + self.scroll_size.height, animate=animate
        )

    def scroll_page_left(self, animate: bool = True) -> None:
        self.scroll_to(x=self.scroll_target_x - self.scroll_size.width, animate=animate)

    def scroll_page_right(self, animate: bool = True) -> None:
        self.scroll_to(x=self.scroll_target_x + self.scroll_size.width, animate=animate)

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

    def _arrange_container(self, region: Region) -> Region:

        show_vertical_scrollbar, show_horizontal_scrollbar = self.scrollbars_enabled

        # self.log(self.styles.gutter)
        # region = region.shrink(self.styles.gutter)

        if show_horizontal_scrollbar and show_vertical_scrollbar:
            (region, _, _, _) = region.split(-1, -1)
            return region
        elif show_vertical_scrollbar:
            region, _ = region.split_vertical(-1)
            return region
        elif show_horizontal_scrollbar:
            region, _ = region.split_horizontal(-1)
            return region
        return region

    def _arrange_scrollbars(self, size: Size) -> Iterable[tuple[Widget, Region]]:
        """Arrange the 'chrome' widgets (typically scrollbars) for a layout element.

        Args:
            size (Size): _description_

        Returns:
            Iterable[tuple[Widget, Region]]: _description_

        Yields:
            Iterator[Iterable[tuple[Widget, Region]]]: _description_
        """
        region = size.region
        show_vertical_scrollbar, show_horizontal_scrollbar = self.scrollbars_enabled

        if show_horizontal_scrollbar and show_vertical_scrollbar:
            (
                region,
                vertical_scrollbar_region,
                horizontal_scrollbar_region,
                _,
            ) = region.split(-1, -1)

            if vertical_scrollbar_region:
                yield self.vscroll, vertical_scrollbar_region
            if horizontal_scrollbar_region:
                yield self.hscroll, horizontal_scrollbar_region
        elif show_vertical_scrollbar:
            region, scrollbar_region = region.split_vertical(-1)
            if scrollbar_region:
                yield self.vscroll, scrollbar_region
        elif show_horizontal_scrollbar:
            region, scrollbar_region = region.split_horizontal(-1)
            if scrollbar_region:
                yield self.hscroll, scrollbar_region

    def get_pseudo_classes(self) -> Iterable[str]:
        """Pseudo classes for a widget"""
        if self._mouse_over:
            yield "hover"
        if self.has_focus:
            yield "focus"

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
            renderable = Border(
                renderable,
                styles.border,
                inner_color=renderable_text_style.bgcolor,
                outer_color=parent_text_style.bgcolor,
            )

        if styles.outline:
            renderable = Border(
                renderable,
                styles.outline,
                outline=True,
                inner_color=renderable_text_style.bgcolor,
                outer_color=parent_text_style.bgcolor,
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
    def scroll_size(self) -> Size:
        return self._size - self.styles.gutter.totals

    @property
    def virtual_size(self) -> Size:
        return self._virtual_size

    @property
    def region(self) -> Region:
        return self.screen._compositor.get_widget_region(self)

    @property
    def scroll(self) -> Offset:
        return Offset(int(self.scroll_x), int(self.scroll_y))

    @property
    def is_transparent(self) -> bool:
        """Check if the background styles is not set.

        Returns:
            bool: ``True`` if there is background color, otherwise ``False``.
        """
        return self.layout is not None and self.styles.text.bgcolor is None

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

    @property
    def is_container(self) -> bool:
        """Check if this widget is a container (contains other widgets)

        Returns:
            bool: True if this widget is a container.
        """
        return self.styles.layout is not None

    def watch_mouse_over(self, value: bool) -> None:
        """Update from CSS if mouse over state changes."""
        self.app.update_styles()

    def watch_has_focus(self, value: bool) -> None:
        """Update from CSS if has focus state changes."""
        self.app.update_styles()

    def on_style_change(self) -> None:
        self.clear_render_cache()

    def size_updated(self, size: Size, virtual_size: Size) -> None:
        if self._size != size or self._virtual_size != virtual_size:
            self._size = size
            self._virtual_size = virtual_size
            self._refresh_scrollbars()
            width, height = self.scroll_size
            if self.show_vertical_scrollbar:
                self.vscroll.window_virtual_size = virtual_size.height
                self.vscroll.window_size = height
                self.vscroll.refresh()
            if self.show_horizontal_scrollbar:
                self.hscroll.window_virtual_size = virtual_size.width
                self.hscroll.window_size = width
                self.hscroll.refresh()

            self.scroll_to(self.scroll_x, self.scroll_y)
            self.refresh()
        self.call_later(self._refresh_scrollbars)

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

    def call_later(self, callback: Callable, *args, **kwargs) -> None:
        self.app.call_later(callback, *args, **kwargs)

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

    def pre_render(self) -> None:
        self._refresh_scrollbars()

    def render(self) -> RenderableType:
        """Get renderable for widget.

        Returns:
            RenderableType: Any renderable
        """

        # Default displays a pretty repr in the center of the screen

        label = self.css_identifier_styled

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
        self.size_updated(event.size, event.virtual_size)

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
        await self.dispatch_key(event)

    def on_mouse_scroll_down(self) -> None:
        self.scroll_down(animate=True)

    def on_mouse_scroll_up(self) -> None:
        self.scroll_up(animate=True)

    def handle_scroll_to(self, message: ScrollTo) -> None:
        self.scroll_to(message.x, message.y, animate=message.animate)

    def handle_scroll_up(self, event: ScrollUp) -> None:
        self.scroll_page_up()
        event.stop()

    def handle_scroll_down(self, event: ScrollDown) -> None:
        self.scroll_page_down()
        event.stop()

    def handle_scroll_left(self, event: ScrollLeft) -> None:
        self.scroll_page_left()
        event.stop()

    def handle_scroll_right(self, event: ScrollRight) -> None:
        self.scroll_page_right()
        event.stop()

    def key_home(self) -> bool:
        if self.is_container:
            self.scroll_home()
            return True
        return False

    def key_end(self) -> bool:
        if self.is_container:
            self.scroll_end()
            return True
        return False

    def key_left(self) -> bool:
        if self.is_container:
            self.scroll_left()
            return True
        return False

    def key_right(self) -> bool:
        if self.is_container:
            self.scroll_right()
            return True
        return False

    def key_down(self) -> bool:
        if self.is_container:
            self.scroll_up()
            return True
        return False

    def key_up(self) -> bool:
        if self.is_container:
            self.scroll_down()
            return True
        return False

    def key_pagedown(self) -> bool:
        if self.is_container:
            self.scroll_page_down()
            return True
        return False

    def key_pageup(self) -> bool:
        if self.is_container:
            self.scroll_page_up()
            return True
        return False
