from __future__ import annotations

from fractions import Fraction
from typing import (
    Any,
    Awaitable,
    ClassVar,
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
from ._context import active_app
from ._types import Lines
from .dom import DOMNode
from ._layout import ArrangeResult
from .geometry import clamp, Offset, Region, Size
from .layouts.vertical import VerticalLayout
from .message import Message
from . import messages
from ._layout import Layout
from .reactive import Reactive, watch
from .renderables.opacity import Opacity
from .renderables.tint import Tint
from ._segment_tools import line_crop
from .css.styles import Styles


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
    """Stores results of a previous render."""

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

    CSS = """
    Widget{
        scrollbar-background: $panel-darken-2;
        scrollbar-background-hover: $panel-darken-3;        
        scrollbar-color: $system;
        scrollbar-color-active: $secondary-darken-1;                
        scrollbar-size-vertical: 2;
        scrollbar-size-horizontal: 1;
        
    }
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = set()

    can_focus: bool = False
    can_focus_children: bool = True

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:

        self._size = Size(0, 0)
        self._container_size = Size(0, 0)
        self._layout_required = False
        self._repaint_required = False
        self._default_layout = VerticalLayout()
        self._animate: BoundAnimator | None = None
        self._reactive_watches: dict[str, Callable] = {}
        self.highlight_style: Style | None = None

        self._vertical_scrollbar: ScrollBar | None = None
        self._horizontal_scrollbar: ScrollBar | None = None

        self._render_cache = RenderCache(Size(0, 0), [])
        self._dirty_regions: list[Region] = []

        # Cache the auto content dimensions
        # TODO: add mechanism to explicitly clear this
        self._content_width_cache: tuple[object, int] = (None, 0)
        self._content_height_cache: tuple[object, int] = (None, 0)

        self._arrangement: ArrangeResult | None = None
        self._arrangement_cache_key: tuple[int, Size] = (-1, Size())

        super().__init__(name=name, id=id, classes=classes)
        self.add_children(*children)

    virtual_size = Reactive(Size(0, 0), layout=True)
    auto_width = Reactive(True)
    auto_height = Reactive(True)
    has_focus = Reactive(False)
    descendant_has_focus = Reactive(False)
    mouse_over = Reactive(False)
    scroll_x = Reactive(0.0, repaint=False, layout=False)
    scroll_y = Reactive(0.0, repaint=False, layout=False)
    scroll_target_x = Reactive(0.0, repaint=False)
    scroll_target_y = Reactive(0.0, repaint=False)
    show_vertical_scrollbar = Reactive(False, layout=True)
    show_horizontal_scrollbar = Reactive(False, layout=True)

    def _arrange(self, size: Size) -> ArrangeResult:
        """Arrange children.

        Args:
            size (Size): Size of container.

        Returns:
            ArrangeResult: Widget locations.
        """
        arrange_cache_key = (self.children._updates, size)
        if (
            self._arrangement is not None
            and arrange_cache_key == self._arrangement_cache_key
        ):
            return self._arrangement
        self._arrangement = self.layout.arrange(self, size)
        self._arrangement_cache_key = (self.children._updates, size)
        return self._arrangement

    def _clear_arrangement_cache(self) -> None:
        self._arrangement = None

    def watch_show_horizontal_scrollbar(self, value: bool) -> None:
        """Watch function for show_horizontal_scrollbar attribute.

        Args:
            value (bool): Show horizontal scrollbar flag.
        """
        if not value:
            # reset the scroll position if the scrollbar is hidden.
            self.scroll_to(0, 0, animate=False)

    def watch_show_vertical_scrollbar(self, value: bool) -> None:
        """Watch function for show_vertical_scrollbar attribute.

        Args:
            value (bool): Show vertical scrollbar flag.
        """
        if not value:
            # reset the scroll position if the scrollbar is hidden.
            self.scroll_to(0, 0, animate=False)

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
        # Parse the Widget's CSS
        for path, css in self.css:
            self.app.stylesheet.add_source(css, path=path)

    def get_box_model(
        self, container: Size, viewport: Size, fraction_unit: Fraction
    ) -> BoxModel:
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
            fraction_unit,
            self.get_content_width,
            self.get_content_height,
        )
        return box_model

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Gets the width of the content area.

        Args:
            container (Size): Size of the container (immediate parent) widget.
            viewport (Size): Size of the viewport.

        Returns:
            int: The optimal width of the content.
        """
        if self.is_container:
            assert self.layout is not None
            return (
                self.layout.get_content_width(self, container, viewport)
                + self.scrollbar_size_vertical
            )

        cache_key = container.width
        if self._content_width_cache[0] == cache_key:
            return self._content_width_cache[1]

        console = self.app.console
        renderable = self.render()
        measurement = Measurement.get(
            console,
            console.options.update_width(container.width),
            renderable,
        )
        width = measurement.maximum
        self._content_width_cache = (cache_key, width)
        return width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        """Gets the height (number of lines) in the content area.

        Args:
            container (Size): Size of the container (immediate parent) widget.
            viewport (Size): Size of the viewport.
            width (int): Width of renderable.

        Returns:
            int: The height of the content.
        """
        if self.is_container:
            assert self.layout is not None
            height = (
                self.layout.get_content_height(
                    self,
                    container,
                    viewport,
                    width,
                )
                + self.scrollbar_size_horizontal
            )
        else:
            cache_key = width

            if self._content_height_cache[0] == cache_key:
                return self._content_height_cache[1]

            renderable = self.render()
            options = self.console.options.update_width(width).update(highlight=False)
            segments = self.console.render(renderable, options)
            # Cheaper than counting the lines returned from render_lines!
            height = sum(text.count("\n") for text, _, _ in segments)
            self._content_height_cache = (cache_key, height)

        return height

    def watch_scroll_x(self, new_value: float) -> None:
        self.horizontal_scrollbar.position = int(new_value)
        self.refresh(layout=True)

    def watch_scroll_y(self, new_value: float) -> None:
        self.vertical_scrollbar.position = int(new_value)
        self.refresh(layout=True)

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
        """The maximum value of `scroll_x`."""
        return max(
            0,
            self.virtual_size.width
            - self.container_size.width
            + self.scrollbar_size_vertical,
        )

    @property
    def max_scroll_y(self) -> float:
        """The maximum value of `scroll_y`."""
        return max(
            0,
            self.virtual_size.height
            - self.container_size.height
            + self.scrollbar_size_horizontal,
        )

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
            vertical=True, name="vertical", thickness=self.scrollbar_size_vertical
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
            vertical=False, name="horizontal", thickness=self.scrollbar_size_horizontal
        )

        self.app.start_widget(self, scroll_bar)
        return scroll_bar

    def _refresh_scrollbars(self) -> None:
        """Refresh scrollbar visibility."""
        if not self.is_scrollable:
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
        self.horizontal_scrollbar.display = show_horizontal
        self.vertical_scrollbar.display = show_vertical

    @property
    def scrollbars_enabled(self) -> tuple[bool, bool]:
        """A tuple of booleans that indicate if scrollbars are enabled.

        Returns:
            tuple[bool, bool]: A tuple of (<vertical scrollbar enabled>, <horizontal scrollbar enabled>)

        """
        if not self.is_scrollable:
            return False, False

        enabled = self.show_vertical_scrollbar, self.show_horizontal_scrollbar
        return enabled

    @property
    def scrollbar_dimensions(self) -> tuple[int, int]:
        """Get the size of any scrollbars on the widget"""
        return (self.scrollbar_size_horizontal, self.scrollbar_size_vertical)

    @property
    def scrollbar_size_vertical(self) -> int:
        """Get the width used by the *vertical* scrollbar."""
        return (
            self.styles.scrollbar_size_vertical if self.show_vertical_scrollbar else 0
        )

    @property
    def scrollbar_size_horizontal(self) -> int:
        """Get the height used by the *horizontal* scrollbar."""
        return (
            self.styles.scrollbar_size_horizontal
            if self.show_horizontal_scrollbar
            else 0
        )

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
        speed: float | None = None,
        duration: float | None = None,
    ) -> bool:
        """Scroll to a given (absolute) coordinate, optionally animating.

        Args:
            x (int | None, optional): X coordinate (column) to scroll to, or ``None`` for no change. Defaults to None.
            y (int | None, optional): Y coordinate (row) to scroll to, or ``None`` for no change. Defaults to None.
            animate (bool, optional): Animate to new scroll position. Defaults to False.

        Returns:
            bool: True if the scroll position changed, otherwise False.
        """
        scrolled_x = scrolled_y = False
        if animate:
            # TODO: configure animation speed
            if duration is None and speed is None:
                speed = 50
            if x is not None:
                self.scroll_target_x = x
                if x != self.scroll_x:
                    self.animate(
                        "scroll_x",
                        self.scroll_target_x,
                        speed=speed,
                        duration=duration,
                        easing="out_cubic",
                    )
                    scrolled_x = True
            if y is not None:
                self.scroll_target_y = y
                if y != self.scroll_y:
                    self.animate(
                        "scroll_y",
                        self.scroll_target_y,
                        speed=speed,
                        duration=duration,
                        easing="out_cubic",
                    )
                    scrolled_y = True

        else:
            if x is not None:
                scroll_x = self.scroll_x
                self.scroll_target_x = self.scroll_x = x
                scrolled_x = scroll_x != self.scroll_x
            if y is not None:
                scroll_y = self.scroll_y
                self.scroll_target_y = self.scroll_y = y
                scrolled_y = scroll_y != self.scroll_y
            if scrolled_x or scrolled_y:
                self.refresh(repaint=False, layout=True)

        return scrolled_x or scrolled_y

    def scroll_relative(
        self,
        x: float | None = None,
        y: float | None = None,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
    ) -> bool:
        """Scroll relative to current position.

        Args:
            x (int | None, optional): X distance (columns) to scroll, or ``None`` for no change. Defaults to None.
            y (int | None, optional): Y distance (rows) to scroll, or ``None`` for no change. Defaults to None.
            animate (bool, optional): Animate to new scroll position. Defaults to False.

        Returns:
            bool: True if the scroll position changed, otherwise False.
        """
        return self.scroll_to(
            None if x is None else (self.scroll_x + x),
            None if y is None else (self.scroll_y + y),
            animate=animate,
            speed=speed,
            duration=duration,
        )

    def scroll_home(self, *, animate: bool = True) -> bool:
        return self.scroll_to(0, 0, animate=animate, duration=1)

    def scroll_end(self, *, animate: bool = True) -> bool:
        return self.scroll_to(0, self.max_scroll_y, animate=animate, duration=1)

    def scroll_left(self, *, animate: bool = True) -> bool:
        return self.scroll_to(x=self.scroll_target_x - 1, animate=animate)

    def scroll_right(self, *, animate: bool = True) -> bool:
        return self.scroll_to(x=self.scroll_target_x + 1, animate=animate)

    def scroll_up(self, *, animate: bool = True) -> bool:
        return self.scroll_to(y=self.scroll_target_y + 1, animate=animate)

    def scroll_down(self, *, animate: bool = True) -> bool:
        return self.scroll_to(y=self.scroll_target_y - 1, animate=animate)

    def scroll_page_up(self, *, animate: bool = True) -> bool:
        return self.scroll_to(
            y=self.scroll_target_y - self.container_size.height, animate=animate
        )

    def scroll_page_down(self, *, animate: bool = True) -> bool:
        return self.scroll_to(
            y=self.scroll_target_y + self.container_size.height, animate=animate
        )

    def scroll_page_left(self, *, animate: bool = True) -> bool:
        return self.scroll_to(
            x=self.scroll_target_x - self.container_size.width,
            animate=animate,
            duration=0.3,
        )

    def scroll_page_right(self, *, animate: bool = True) -> bool:
        return self.scroll_to(
            x=self.scroll_target_x + self.container_size.width,
            animate=animate,
            duration=0.3,
        )

    def scroll_to_widget(self, widget: Widget, *, animate: bool = True) -> bool:
        """Starting from `widget`, travel up the DOM to this node, scrolling all containers such that
        every widget is visible within its parent container. This will, in the majority of cases,
        bring the target widget into

        Args:
            widget (Widget): A descendant widget.
            animate (bool, optional): True to animate, or False to jump. Defaults to True.

        Returns:
            bool: True if any scrolling has occurred in any descendant, otherwise False.
        """

        scrolls = set()

        node = widget.parent
        child = widget
        while node:
            try:
                widget_region = child.region
                container_region = node.region
            except (errors.NoWidget, AttributeError):
                return False

            if widget_region in container_region:
                # Widget is visible, nothing to do
                child = node
                node = node.parent
                continue

            # We can either scroll so the widget is at the top of the container, or so that
            # it is at the bottom. We want to pick which has the shortest distance
            top_delta = widget_region.origin - container_region.origin

            bottom_delta = widget_region.origin - (
                container_region.origin
                + Offset(0, container_region.height - widget_region.height)
            )

            if widget_region.width > container_region.width:
                delta_x = top_delta.x
            else:
                delta_x = min(top_delta.x, bottom_delta.x, key=abs)

            if widget_region.height > container_region.height:
                delta_y = top_delta.y
            else:
                delta_y = min(top_delta.y, bottom_delta.y, key=abs)

            scrolled = node.scroll_relative(
                delta_x or None, delta_y or None, animate=animate, duration=0.2
            )
            scrolls.add(scrolled)

            if node == self:
                break
            child = node
            node = node.parent

        return any(scrolls)

    def __init_subclass__(
        cls,
        can_focus: bool = True,
        can_focus_children: bool = True,
        inherit_css: bool = True,
    ) -> None:
        super().__init_subclass__(inherit_css=inherit_css)
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

    def _get_scrollable_region(self, region: Region) -> Region:
        """Adjusts the Widget region to accommodate scrollbars.

        Args:
            region (Region): A region for the widget.

        Returns:
            Region: The widget region minus scrollbars.
        """
        show_vertical_scrollbar, show_horizontal_scrollbar = self.scrollbars_enabled

        horizontal_scrollbar_thickness = self.scrollbar_size_horizontal
        vertical_scrollbar_thickness = self.scrollbar_size_vertical

        if self.styles.scrollbar_gutter == "stable":
            # Let's _always_ reserve some space, whether the scrollbar is actually displayed or not:
            show_vertical_scrollbar = True
            vertical_scrollbar_thickness = self.styles.scrollbar_size_vertical

        if show_horizontal_scrollbar and show_vertical_scrollbar:
            (region, _, _, _) = region.split(
                -vertical_scrollbar_thickness,
                -horizontal_scrollbar_thickness,
            )
        elif show_vertical_scrollbar:
            region, _ = region.split_vertical(-vertical_scrollbar_thickness)
        elif show_horizontal_scrollbar:
            region, _ = region.split_horizontal(-horizontal_scrollbar_thickness)
        return region

    def _arrange_scrollbars(self, size: Size) -> Iterable[tuple[Widget, Region]]:
        """Arrange the 'chrome' widgets (typically scrollbars) for a layout element.

        Args:
            size (Size): Size of the containing region.

        Returns:
            Iterable[tuple[Widget, Region]]: Tuples of scrollbar Widget and region.

        """
        region = size.region
        show_vertical_scrollbar, show_horizontal_scrollbar = self.scrollbars_enabled

        scrollbar_size_horizontal = self.scrollbar_size_horizontal
        scrollbar_size_vertical = self.scrollbar_size_vertical
        if show_horizontal_scrollbar and show_vertical_scrollbar:
            (
                _,
                vertical_scrollbar_region,
                horizontal_scrollbar_region,
                _,
            ) = region.split(
                -scrollbar_size_vertical,
                -scrollbar_size_horizontal,
            )
            if vertical_scrollbar_region:
                yield self.vertical_scrollbar, vertical_scrollbar_region
            if horizontal_scrollbar_region:
                yield self.horizontal_scrollbar, horizontal_scrollbar_region
        elif show_vertical_scrollbar:
            _, scrollbar_region = region.split_vertical(-scrollbar_size_vertical)
            if scrollbar_region:
                yield self.vertical_scrollbar, scrollbar_region
        elif show_horizontal_scrollbar:
            _, scrollbar_region = region.split_horizontal(-scrollbar_size_horizontal)
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

        (base_background, base_color), (background, color) = self.colors
        styles = self.styles

        renderable = self.render()

        content_align = (styles.content_align_horizontal, styles.content_align_vertical)
        if content_align != ("left", "top"):
            horizontal, vertical = content_align
            renderable = Align(renderable, horizontal, vertical=vertical)

        renderable = Padding(
            renderable,
            styles.padding,
            style=Style.from_color(color.rich_color, background.rich_color),
        )

        if styles.border:
            renderable = Border(
                renderable,
                styles.border,
                inner_color=background,
                outer_color=base_background,
            )

        if styles.outline:
            renderable = Border(
                renderable,
                styles.outline,
                inner_color=styles.background,
                outer_color=base_background,
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
    def content_region(self) -> Region:
        """Gets an absolute region containing the content (minus padding and border)."""
        return self.region.shrink(self.styles.content_gutter)

    @property
    def content_offset(self) -> Offset:
        """An offset from the Widget origin where the content begins."""
        x, y = self.styles.content_gutter.top_left
        return Offset(x, y)

    @property
    def region(self) -> Region:
        """The region occupied by this widget, relative to the Screen."""
        try:
            return self.screen.find_widget(self).region
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
        return self.is_scrollable and self.styles.background.is_transparent

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
    def layout(self) -> Layout:
        """Get the layout object if set in styles, or a default layout."""
        return self.styles.layout or self._default_layout

    @property
    def is_container(self) -> bool:
        """Check if this widget is a container (contains other widgets).

        Returns:
            bool: True if this widget is a container.
        """
        return self.styles.layout is not None or bool(self.children)

    @property
    def is_scrollable(self) -> bool:
        """Check if this Widget may be scrolled.

        Returns:
            bool: True if this widget may be scrolled.
        """
        return self.is_container

    def watch_mouse_over(self, value: bool) -> None:
        """Update from CSS if mouse over state changes."""
        self.app.update_styles()

    def watch_has_focus(self, value: bool) -> None:
        """Update from CSS if has focus state changes."""
        self.app.update_styles()

    def size_updated(
        self, size: Size, virtual_size: Size, container_size: Size
    ) -> None:
        if self._size != size or self.virtual_size != virtual_size:
            self._size = size
            self.virtual_size = virtual_size
            self._container_size = container_size
            if self.is_scrollable:
                self._refresh_scrollbars()
                width, height = self.container_size
                if self.show_vertical_scrollbar:
                    self.vertical_scrollbar.window_virtual_size = virtual_size.height
                    self.vertical_scrollbar.window_size = height
                if self.show_horizontal_scrollbar:
                    self.horizontal_scrollbar.window_virtual_size = virtual_size.width
                    self.horizontal_scrollbar.window_size = width

                self.scroll_x = self.validate_scroll_x(self.scroll_x)
                self.scroll_y = self.validate_scroll_y(self.scroll_y)
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

    def _crop_lines(self, lines: Lines, x1, x2) -> Lines:
        width = self.size.width
        if (x1, x2) != (0, width):
            lines = [line_crop(line, x1, x2, width) for line in lines]
        return lines

    def render_lines(self, crop: Region) -> Lines:
        """Render the widget in to lines.

        Args:
            crop (Region): Region within visible area to.

        Returns:
            Lines: A list of list of segments
        """
        if self._dirty_regions:
            self._render_lines()

        x1, y1, x2, y2 = crop.corners
        lines = self._render_cache.lines[y1:y2]
        lines = self._crop_lines(lines, x1, x2)
        return lines

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
            self._clear_arrangement_cache()
        if repaint:
            self._content_width_cache = (None, 0)
            self._content_height_cache = (None, 0)
            self.set_dirty()
            self._repaint_required = True
            if isinstance(self.parent, Widget) and self.styles.auto_dimensions:
                self.parent.refresh(layout=True)

        self.check_idle()

    def render(self) -> RenderableType:
        """Get renderable for widget.

        Args:
            style (Styles): The Styles object for this Widget.

        Returns:
            RenderableType: Any renderable
        """
        return "" if self.is_container else self.css_identifier_styled

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

        if self._repaint_required:
            self.screen.post_message_no_wait(messages.Update(self, self))
        if self._layout_required:
            self.screen.post_message_no_wait(messages.Layout(self))
        self._layout_required = False
        self._repaint_required = False

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
            self.screen.refresh(repaint=False, layout=True)

    def on_leave(self) -> None:
        self.mouse_over = False

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_focus(self, event: events.Focus) -> None:
        self.emit_no_wait(events.DescendantFocus(self))
        self.has_focus = True
        self.refresh()

    def on_blur(self, event: events.Blur) -> None:
        self.emit_no_wait(events.DescendantBlur(self))
        self.has_focus = False
        self.refresh()

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        self.descendant_has_focus = True
        if "focus-within" in self.pseudo_classes:
            sender = event.sender
            for child in self.walk_children(False):
                child.refresh()
                if child is sender:
                    break

    def on_descendant_blur(self, event: events.DescendantBlur) -> None:
        self.descendant_has_focus = False
        if "focus-within" in self.pseudo_classes:
            sender = event.sender
            for child in self.walk_children(False):
                child.refresh()
                if child is sender:
                    break

    def on_mouse_scroll_down(self, event) -> None:
        if self.is_scrollable:
            if self.scroll_down(animate=False):
                event.stop()

    def on_mouse_scroll_up(self, event) -> None:
        if self.is_scrollable:
            if self.scroll_up(animate=False):
                event.stop()

    def handle_scroll_to(self, message: ScrollTo) -> None:
        if self.is_scrollable:
            self.scroll_to(message.x, message.y, animate=message.animate, duration=0.1)
            message.stop()

    def handle_scroll_up(self, event: ScrollUp) -> None:
        if self.is_scrollable:
            self.scroll_page_up()
            event.stop()

    def handle_scroll_down(self, event: ScrollDown) -> None:
        if self.is_scrollable:
            self.scroll_page_down()
            event.stop()

    def handle_scroll_left(self, event: ScrollLeft) -> None:
        if self.is_scrollable:
            self.scroll_page_left()
            event.stop()

    def handle_scroll_right(self, event: ScrollRight) -> None:
        if self.is_scrollable:
            self.scroll_page_right()
            event.stop()

    def key_home(self) -> bool:
        if self.is_scrollable:
            self.scroll_home()
            return True
        return False

    def key_end(self) -> bool:
        if self.is_scrollable:
            self.scroll_end()
            return True
        return False

    def key_left(self) -> bool:
        if self.is_scrollable:
            self.scroll_left()
            return True
        return False

    def key_right(self) -> bool:
        if self.is_scrollable:
            self.scroll_right()
            return True
        return False

    def key_down(self) -> bool:
        if self.is_scrollable:
            self.scroll_up()
            return True
        return False

    def key_up(self) -> bool:
        if self.is_scrollable:
            self.scroll_down()
            return True
        return False

    def key_pagedown(self) -> bool:
        if self.is_scrollable:
            self.scroll_page_down()
            return True
        return False

    def key_pageup(self) -> bool:
        if self.is_scrollable:
            self.scroll_page_up()
            return True
        return False
