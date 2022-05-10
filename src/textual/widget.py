from __future__ import annotations

from typing import (
    Any,
    Awaitable,
    TYPE_CHECKING,
    Callable,
    Iterable,
    NamedTuple,
)

import rich.repr
from rich.align import Align
from rich.console import Console, RenderableType
from rich.measure import Measurement
from rich.padding import Padding
from rich.style import Style
from rich.styled import Styled


from . import errors
from . import events
from ._animator import BoundAnimator
from ._border import Border
from .box_model import BoxModel, get_box_model
from .color import Color
from ._context import active_app
from ._types import Lines
from .dom import DOMNode
from .geometry import clamp, Offset, Region, Size
from .layouts.vertical import VerticalLayout
from .message import Message
from . import messages
from ._layout import Layout
from .reactive import Reactive, watch
from .renderables.opacity import Opacity
from .renderables.tint import Tint


if TYPE_CHECKING:
    from .app import App, ComposeResult
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
    can_focus_children: bool = True

    CSS = """
    """

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:

        self._size = Size(0, 0)
        self._virtual_size = Size(0, 0)
        self._container_size = Size(0, 0)
        self._layout_required = False
        self._default_layout = VerticalLayout()
        self._animate: BoundAnimator | None = None
        self._reactive_watches: dict[str, Callable] = {}
        self.highlight_style: Style | None = None

        self._vertical_scrollbar: ScrollBar | None = None
        self._horizontal_scrollbar: ScrollBar | None = None

        self._render_cache = RenderCache(Size(0, 0), [])
        self._dirty_regions: list[Region] = []

        super().__init__(name=name, id=id, classes=classes)
        self.add_children(*children)

    auto_width = Reactive(True)
    auto_height = Reactive(True)
    has_focus = Reactive(False)
    descendant_has_focus = Reactive(False)
    mouse_over = Reactive(False)
    scroll_x = Reactive(0.0, repaint=False)
    scroll_y = Reactive(0.0, repaint=False)
    scroll_target_x = Reactive(0.0, repaint=False)
    scroll_target_y = Reactive(0.0, repaint=False)
    show_vertical_scrollbar = Reactive(False, layout=True)
    show_horizontal_scrollbar = Reactive(False, layout=True)

    def mount(self, *anon_widgets: Widget, **widgets: Widget) -> None:
        self.app.register(self, *anon_widgets, **widgets)
        self.screen.refresh()

    def compose(self) -> ComposeResult:
        """Yield child widgets for a container."""
        return
        yield

    def on_register(self, app: App) -> None:
        """Called when the instance is registered.

        Args:
            app (App): App instance.
        """
        # Parser the Widget's CSS
        self.app.stylesheet.add_source(
            self.CSS, f"{__file__}:<{self.__class__.__name__}>"
        )

    def get_box_model(self, container: Size, viewport: Size) -> BoxModel:
        """Process the box model for this widget.

        Args:
            container (Size): The size of the container widget (with a layout)
            viewport (Size): The viewport size.

        Returns:
            BoxModel: The size and margin for this widget.
        """
        box_model = get_box_model(
            self.styles,
            container,
            viewport,
            self.get_content_width,
            self.get_content_height,
        )
        return box_model

    def get_content_width(self, container_size: Size, viewport_size: Size) -> int:
        """Gets the width of the content area.

        Args:
            container_size (Size): Size of the container (immediate parent) widget.
            viewport_size (Size): Size of the viewport.

        Returns:
            int: The optimal width of the content.
        """
        console = self.app.console
        renderable = self.render()
        measurement = Measurement.get(console, console.options, renderable)
        return measurement.maximum

    def get_content_height(
        self, container_size: Size, viewport_size: Size, width: int
    ) -> int:
        """Gets the height (number of lines) in the content area.

        Args:
            container_size (Size): Size of the container (immediate parent) widget.
            viewport_size (Size): Size of the viewport.
            width (int): Width of renderable.

        Returns:
            int: The height of the content.
        """
        renderable = self.render()
        options = self.console.options.update_width(width)
        segments = self.console.render(renderable, options)
        # Cheaper than counting the lines returned from render_lines!
        height = sum(text.count("\n") for text, _, _ in segments)
        return height

    async def watch_scroll_x(self, new_value: float) -> None:
        self.horizontal_scrollbar.position = int(new_value)

    async def watch_scroll_y(self, new_value: float) -> None:
        self.vertical_scrollbar.position = int(new_value)

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
        return max(0, self.virtual_size.width - self.container_size.width)

    @property
    def max_scroll_y(self) -> float:
        return max(0, self.virtual_size.height - self.container_size.height)

    @property
    def vertical_scrollbar(self) -> ScrollBar:
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
    def horizontal_scrollbar(self) -> ScrollBar:
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
        width, height = self.container_size

        show_horizontal = self.show_horizontal_scrollbar
        if overflow_x == "hidden":
            show_horizontal = False
        if overflow_x == "scroll":
            show_horizontal = True
        elif overflow_x == "auto":
            show_horizontal = self.virtual_size.width > width

        show_vertical = self.show_vertical_scrollbar
        if overflow_y == "hidden":
            show_vertical = False
        elif overflow_y == "scroll":
            show_vertical = True
        elif overflow_y == "auto":
            show_vertical = self.virtual_size.height > height

        self.show_horizontal_scrollbar = show_horizontal
        self.show_vertical_scrollbar = show_vertical

    @property
    def scrollbars_enabled(self) -> tuple[bool, bool]:
        """A tuple of booleans that indicate if scrollbars are enabled.

        Returns:
            tuple[bool, bool]: A tuple of (<vertical scrollbar enabled>, <horizontal scrollbar enabled>)

        """
        if self.layout is None:
            return False, False

        enabled = self.show_vertical_scrollbar, self.show_horizontal_scrollbar
        return enabled

    def set_dirty(self) -> None:
        """Set the Widget as 'dirty' (requiring re-render)."""
        self._dirty_regions.clear()
        self._dirty_regions.append(self.size.region)

    def scroll_to(
        self,
        x: float | None = None,
        y: float | None = None,
        *,
        animate: bool = True,
    ) -> bool:
        """Scroll to a given (absolute) coordinate, optionally animating.

        Args:
            scroll_x (int | None, optional): X coordinate (column) to scroll to, or ``None`` for no change. Defaults to None.
            scroll_y (int | None, optional): Y coordinate (row) to scroll to, or ``None`` for no change. Defaults to None.
            animate (bool, optional): Animate to new scroll position. Defaults to False.
        """

        scrolled_x = False
        scrolled_y = False

        if animate:
            # TODO: configure animation speed
            if x is not None:
                self.scroll_target_x = x
                if x != self.scroll_x:
                    self.animate(
                        "scroll_x", self.scroll_target_x, speed=80, easing="out_cubic"
                    )
                    scrolled_x = True
            if y is not None:
                self.scroll_target_y = y
                if y != self.scroll_y:
                    self.animate(
                        "scroll_y", self.scroll_target_y, speed=80, easing="out_cubic"
                    )
                    scrolled_y = True

        else:
            if x is not None:
                self.scroll_target_x = self.scroll_x = x
                if x != self.scroll_x:
                    scrolled_x = True
            if y is not None:
                self.scroll_target_y = self.scroll_y = y
                if y != self.scroll_y:
                    scrolled_y = True
            self.refresh(repaint=False, layout=True)
        return scrolled_x or scrolled_y

    def scroll_home(self, animate: bool = True) -> bool:
        return self.scroll_to(0, 0, animate=animate)

    def scroll_end(self, animate: bool = True) -> bool:
        return self.scroll_to(0, self.max_scroll_y, animate=animate)

    def scroll_left(self, animate: bool = True) -> bool:
        return self.scroll_to(x=self.scroll_target_x - 1, animate=animate)

    def scroll_right(self, animate: bool = True) -> bool:
        return self.scroll_to(x=self.scroll_target_x + 1, animate=animate)

    def scroll_up(self, animate: bool = True) -> bool:
        return self.scroll_to(y=self.scroll_target_y + 1, animate=animate)

    def scroll_down(self, animate: bool = True) -> bool:
        return self.scroll_to(y=self.scroll_target_y - 1, animate=animate)

    def scroll_page_up(self, animate: bool = True) -> bool:
        return self.scroll_to(
            y=self.scroll_target_y - self.container_size.height, animate=animate
        )

    def scroll_page_down(self, animate: bool = True) -> bool:
        return self.scroll_to(
            y=self.scroll_target_y + self.container_size.height, animate=animate
        )

    def scroll_page_left(self, animate: bool = True) -> bool:
        return self.scroll_to(
            x=self.scroll_target_x - self.container_size.width, animate=animate
        )

    def scroll_page_right(self, animate: bool = True) -> bool:
        return self.scroll_to(
            x=self.scroll_target_x + self.container_size.width, animate=animate
        )

    def __init_subclass__(
        cls, can_focus: bool = True, can_focus_children: bool = True
    ) -> None:
        super().__init_subclass__()
        cls.can_focus = can_focus
        cls.can_focus_children = can_focus_children

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
        """Adjusts the Widget region to accommodate scrollbars.

        Args:
            region (Region): A region for the widget.

        Returns:
            Region: The widget region minus scrollbars.
        """
        show_vertical_scrollbar, show_horizontal_scrollbar = self.scrollbars_enabled
        if show_horizontal_scrollbar and show_vertical_scrollbar:
            (region, _, _, _) = region.split(-1, -1)
        elif show_vertical_scrollbar:
            region, _ = region.split_vertical(-1)
        elif show_horizontal_scrollbar:
            region, _ = region.split_horizontal(-1)
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
                yield self.vertical_scrollbar, vertical_scrollbar_region
            if horizontal_scrollbar_region:
                yield self.horizontal_scrollbar, horizontal_scrollbar_region
        elif show_vertical_scrollbar:
            region, scrollbar_region = region.split_vertical(-1)
            if scrollbar_region:
                yield self.vertical_scrollbar, scrollbar_region
        elif show_horizontal_scrollbar:
            region, scrollbar_region = region.split_horizontal(-1)
            if scrollbar_region:
                yield self.horizontal_scrollbar, scrollbar_region

    def get_pseudo_classes(self) -> Iterable[str]:
        """Pseudo classes for a widget"""
        if self.mouse_over:
            yield "hover"
        if self.has_focus:
            yield "focus"
        if self.descendant_has_focus:
            yield "focus-within"

    def watch(self, attribute_name, callback: Callable[[Any], Awaitable[None]]) -> None:
        watch(self, attribute_name, callback)

    def render_styled(self) -> RenderableType:
        """Applies style attributes to the default renderable.

        Returns:
            RenderableType: A new renderable.
        """

        renderable = self.render()

        styles = self.styles
        parent_styles = self.parent.styles

        parent_text_style = self.parent.rich_text_style
        text_style = styles.rich_style

        content_align = (styles.content_align_horizontal, styles.content_align_vertical)
        if content_align != ("left", "top"):
            horizontal, vertical = content_align
            renderable = Align(renderable, horizontal, vertical=vertical)

        renderable_text_style = parent_text_style + text_style
        if renderable_text_style:
            renderable = Styled(renderable, renderable_text_style)

        renderable = Padding(renderable, styles.padding, style=renderable_text_style)

        if styles.border:
            renderable = Border(
                renderable,
                styles.border,
                inner_color=styles.background,
                outer_color=Color.from_rich_color(parent_text_style.bgcolor),
            )

        if styles.outline:
            renderable = Border(
                renderable,
                styles.outline,
                inner_color=styles.background,
                outer_color=parent_styles.background,
                outline=True,
            )

        if styles.tint.a != 0:
            renderable = Tint(renderable, styles.tint)
        if styles.opacity != 1.0:
            renderable = Opacity(renderable, opacity=styles.opacity)

        return renderable

    @property
    def size(self) -> Size:
        return self._size

    @property
    def container_size(self) -> Size:
        return self._container_size

    @property
    def virtual_size(self) -> Size:
        return self._virtual_size

    @property
    def region(self) -> Region:
        try:
            return self.screen._compositor.get_widget_region(self)
        except errors.NoWidget:
            return Region()

    @property
    def scroll_offset(self) -> Offset:
        return Offset(int(self.scroll_x), int(self.scroll_y))

    @property
    def is_transparent(self) -> bool:
        """Check if the background styles is not set.

        Returns:
            bool: ``True`` if there is background color, otherwise ``False``.
        """
        return self.is_container and self.styles.background.is_transparent

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
        return self.styles.layout or (
            # If we have children we _should_ return a layout, otherwise they won't be displayed:
            self._default_layout
            if self.children
            else None
        )

    @property
    def is_container(self) -> bool:
        """Check if this widget is a container (contains other widgets)

        Returns:
            bool: True if this widget is a container.
        """
        return self.styles.layout is not None or bool(self.children)

    def watch_mouse_over(self, value: bool) -> None:
        """Update from CSS if mouse over state changes."""
        self.app.update_styles()

    def watch_has_focus(self, value: bool) -> None:
        """Update from CSS if has focus state changes."""
        self.app.update_styles()

    def on_style_change(self) -> None:
        self.set_dirty()
        self.check_idle()

    def size_updated(
        self, size: Size, virtual_size: Size, container_size: Size
    ) -> None:
        if self._size != size or self._virtual_size != virtual_size:
            self._size = size
            self._virtual_size = virtual_size
            self._container_size = container_size

            if self.is_container:
                self._refresh_scrollbars()
                width, height = self.container_size
                if self.show_vertical_scrollbar:
                    self.vertical_scrollbar.window_virtual_size = virtual_size.height
                    self.vertical_scrollbar.window_size = height
                if self.show_horizontal_scrollbar:
                    self.horizontal_scrollbar.window_virtual_size = virtual_size.width
                    self.horizontal_scrollbar.window_size = width

                self.refresh(layout=True)
                self.call_later(self.scroll_to, self.scroll_x, self.scroll_y)
            else:
                self.refresh()

    def _render_lines(self) -> None:
        """Render all lines."""
        width, height = self.size
        renderable = self.render_styled()
        options = self.console.options.update_dimensions(width, height).update(
            highlight=False
        )
        lines = self.console.render_lines(renderable, options)
        self._render_cache = RenderCache(self.size, lines)
        self._dirty_regions.clear()

    def get_render_lines(
        self, start: int | None = None, end: int | None = None
    ) -> Lines:
        """Get segment lines to render the widget.

        Args:
            start (int | None, optional): line start index, or None for first line. Defaults to None.
            end (int | None, optional): line end index, or None for last line. Defaults to None.

        Returns:
            Lines: A list of lists of segments.
        """
        if self._dirty_regions:
            self._render_lines()
            if self.is_container:
                self.horizontal_scrollbar.refresh()
                self.vertical_scrollbar.refresh()
        lines = self._render_cache.lines[start:end]
        return lines

    def check_layout(self) -> bool:
        """Check if a layout has been requested."""
        return self._layout_required

    def _reset_check_layout(self) -> None:
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
            self._layout_required = True
        if repaint:
            self.set_dirty()
        self.check_idle()

    def render(self) -> RenderableType:
        """Get renderable for widget.

        Returns:
            RenderableType: Any renderable
        """

        # Default displays a pretty repr in the center of the screen

        if self.is_container:
            return ""

        return self.css_identifier_styled

    async def action(self, action: str, *params) -> None:
        await self.app.action(action, self)

    async def post_message(self, message: Message) -> bool:
        if not self.check_message_enabled(message):
            return True
        if not self.is_running:
            self.log(self, f"IS NOT RUNNING, {message!r} not sent")
        return await super().post_message(message)

    def on_idle(self, event: events.Idle) -> None:
        """Called when there are no more events on the queue.

        Args:
            event (events.Idle): Idle event.
        """

        if self.check_layout():
            self._reset_check_layout()
            self.screen.post_message_no_wait(messages.Layout(self))
        elif self._dirty_regions:
            self.emit_no_wait(messages.Update(self, self))

    def focus(self) -> None:
        """Give input focus to this widget."""
        self.app.set_focus(self)

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

    def on_mount(self, event: events.Mount) -> None:
        widgets = list(self.compose())
        if widgets:
            self.mount(*widgets)
            self.screen.refresh()

    def on_leave(self) -> None:
        self.mouse_over = False

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_focus(self, event: events.Focus) -> None:
        self.emit_no_wait(events.DescendantFocus(self))
        self.has_focus = True

    def on_blur(self, event: events.Blur) -> None:
        self.emit_no_wait(events.DescendantBlur(self))
        self.has_focus = False

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        self.descendant_has_focus = True

    def on_descendant_blur(self, event: events.DescendantBlur) -> None:
        self.descendant_has_focus = False

    def on_mouse_scroll_down(self, event) -> None:
        if self.is_container:
            self.scroll_down(animate=False)
            event.stop()

    def on_mouse_scroll_up(self, event) -> None:
        if self.is_container:
            self.scroll_up(animate=False)
            event.stop()

    def handle_scroll_to(self, message: ScrollTo) -> None:
        if self.is_container:
            self.scroll_to(message.x, message.y, animate=message.animate)
            message.stop()

    def handle_scroll_up(self, event: ScrollUp) -> None:
        if self.is_container:
            self.scroll_page_up()
            event.stop()

    def handle_scroll_down(self, event: ScrollDown) -> None:
        if self.is_container:
            self.scroll_page_down()
            event.stop()

    def handle_scroll_left(self, event: ScrollLeft) -> None:
        if self.is_container:
            self.scroll_page_left()
            event.stop()

    def handle_scroll_right(self, event: ScrollRight) -> None:
        if self.is_container:
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
