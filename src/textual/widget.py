from __future__ import annotations

from asyncio import Lock
from fractions import Fraction
from itertools import islice
from operator import attrgetter
from typing import TYPE_CHECKING, ClassVar, Collection, Iterable, NamedTuple, cast

import rich.repr
from rich.console import Console, ConsoleRenderable, JustifyMethod, RenderableType
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style
from rich.styled import Styled
from rich.text import Text

from . import errors, events, messages
from ._animator import BoundAnimator
from ._arrange import DockArrangeResult, arrange
from ._context import active_app
from ._layout import Layout
from ._segment_tools import align_lines
from ._styles_cache import StylesCache
from ._types import Lines
from .binding import NoBinding
from .box_model import BoxModel, get_box_model
from .css.constants import VALID_TEXT_ALIGN
from .dom import DOMNode, NoScreen
from .geometry import Offset, Region, Size, Spacing, clamp
from .layouts.vertical import VerticalLayout
from .message import Message
from .reactive import Reactive

if TYPE_CHECKING:
    from .app import App, ComposeResult
    from .scrollbar import (
        ScrollBar,
        ScrollBarCorner,
        ScrollDown,
        ScrollLeft,
        ScrollRight,
        ScrollTo,
        ScrollUp,
    )


_JUSTIFY_MAP: dict[str, JustifyMethod] = {
    "start": "left",
    "end": "right",
    "justify": "full",
}


class RenderCache(NamedTuple):
    """Stores results of a previous render."""

    size: Size
    lines: Lines


@rich.repr.auto
class Widget(DOMNode):
    """
    A Widget is the base class for Textual widgets. Extent this class (or a sub-class) when defining your own widgets.

    """

    DEFAULT_CSS = """
    Widget{
        scrollbar-background: $panel-darken-1;
        scrollbar-background-hover: $panel-darken-2;
        scrollbar-color: $primary-lighten-1;
        scrollbar-color-active: $warning-darken-1;
        scrollbar-corner-color: $panel-darken-3;
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
        self.highlight_style: Style | None = None

        self._vertical_scrollbar: ScrollBar | None = None
        self._horizontal_scrollbar: ScrollBar | None = None
        self._scrollbar_corner: ScrollBarCorner | None = None

        self._render_cache = RenderCache(Size(0, 0), [])
        # Regions which need to be updated (in Widget)
        self._dirty_regions: set[Region] = set()
        # Regions which need to be transferred from cache to screen
        self._repaint_regions: set[Region] = set()

        # Cache the auto content dimensions
        # TODO: add mechanism to explicitly clear this
        self._content_width_cache: tuple[object, int] = (None, 0)
        self._content_height_cache: tuple[object, int] = (None, 0)

        self._arrangement: DockArrangeResult | None = None
        self._arrangement_cache_key: tuple[int, Size] = (-1, Size())

        self._styles_cache = StylesCache()
        self._rich_style_cache: dict[str, Style] = {}

        self._lock = Lock()

        super().__init__(
            name=name,
            id=id,
            classes=self.DEFAULT_CLASSES if classes is None else classes,
        )
        self._add_children(*children)

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

    @property
    def siblings(self) -> list[Widget]:
        """Get the widget's siblings (self is removed from the return list).

        Returns:
            list[Widget]: A list of siblings.
        """
        parent = self.parent
        if parent is not None:
            siblings = list(parent.children)
            siblings.remove(self)
            return siblings
        else:
            return []

    @property
    def allow_vertical_scroll(self) -> bool:
        """Check if vertical scroll is permitted.

        May be overridden if you want different logic regarding allowing scrolling.

        Returns:
            bool: True if the widget may scroll _vertically_.
        """
        return self.is_scrollable and self.show_vertical_scrollbar

    @property
    def allow_horizontal_scroll(self) -> bool:
        """Check if horizontal scroll is permitted.

        May be overridden if you want different logic regarding allowing scrolling.

        Returns:
            bool: True if the widget may scroll _horizontally_.
        """
        return self.is_scrollable and self.show_horizontal_scrollbar

    @property
    def _allow_scroll(self) -> bool:
        """Check if both axis may be scrolled.

        Returns:
            bool: True if horizontal and vertical scrolling is enabled.
        """
        return self.is_scrollable and (
            self.allow_horizontal_scroll or self.allow_vertical_scroll
        )

    def get_component_rich_style(self, name: str) -> Style:
        """Get a *Rich* style for a component.

        Args:
            name (str): Name of component.

        Returns:
            Style: A Rich style object.
        """
        style = self._rich_style_cache.get(name)
        if style is None:
            style = self.get_component_styles(name).rich_style
            self._rich_style_cache[name] = style
        return style

    def _arrange(self, size: Size) -> DockArrangeResult:
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

        self._arrangement_cache_key = arrange_cache_key
        self._arrangement = arrange(self, self.children, size, self.screen.size)
        return self._arrangement

    def _clear_arrangement_cache(self) -> None:
        """Clear arrangement cache, forcing a new arrange operation."""
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
        """Mount child widgets (making this widget a container).

        Widgets may be passed as positional arguments or keyword arguments. If keyword arguments,
        the keys will be set as the Widget's id.

        Example:
            ```python
            self.mount(Static("hello"), header=Header())
            ```

        """
        self.app._register(self, *anon_widgets, **widgets)
        self.screen.refresh(layout=True)

    def compose(self) -> ComposeResult:
        """Called by Textual to create child widgets.

        Extend this to build a UI.

        Example:
            ```python
            def compose(self) -> ComposeResult:
                yield Header()
                yield Container(
                    TreeControl(), Viewer()
                )
                yield Footer()
            ```

        """
        return
        yield

    def _post_register(self, app: App) -> None:
        """Called when the instance is registered.

        Args:
            app (App): App instance.
        """
        # Parse the Widget's CSS
        for path, css, tie_breaker in self.get_default_css():
            self.app.stylesheet.add_source(
                css, path=path, is_default_css=True, tie_breaker=tie_breaker
            )

    def _get_box_model(
        self, container: Size, viewport: Size, fraction_unit: Fraction
    ) -> BoxModel:
        """Process the box model for this widget.

        Args:
            container (Size): The size of the container widget (with a layout)
            viewport (Size): The viewport size.
            fraction_unit (Fraction): The unit used for `fr` units.

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

        May be overridden in a subclass.

        Args:
            container (Size): Size of the container (immediate parent) widget.
            viewport (Size): Size of the viewport.

        Returns:
            int: The optimal width of the content.
        """
        if self.is_container:
            assert self._layout is not None
            return self._layout.get_content_width(self, container, viewport)

        cache_key = container.width
        if self._content_width_cache[0] == cache_key:
            return self._content_width_cache[1]

        console = self.app.console
        renderable = self.post_render(self.render())

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

        May be overridden in a subclass.

        Args:
            container (Size): Size of the container (immediate parent) widget.
            viewport (Size): Size of the viewport.
            width (int): Width of renderable.

        Returns:
            int: The height of the content.
        """

        if self.is_container:
            assert self._layout is not None
            height = (
                self._layout.get_content_height(
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
            options = self._console.options.update_width(width).update(highlight=False)
            segments = self._console.render(renderable, options)
            # Cheaper than counting the lines returned from render_lines!
            height = sum(text.count("\n") for text, _, _ in segments)
            self._content_height_cache = (cache_key, height)

        return height

    def watch_scroll_x(self, new_value: float) -> None:
        self.horizontal_scrollbar.position = int(new_value)
        self.refresh(layout=True)
        self.horizontal_scrollbar.refresh()

    def watch_scroll_y(self, new_value: float) -> None:
        self.vertical_scrollbar.position = int(new_value)
        self.refresh(layout=True)
        self.vertical_scrollbar.refresh()

    def validate_scroll_x(self, value: float) -> float:
        return clamp(value, 0, self.max_scroll_x)

    def validate_scroll_target_x(self, value: float) -> float:
        return clamp(value, 0, self.max_scroll_x)

    def validate_scroll_y(self, value: float) -> float:
        return clamp(value, 0, self.max_scroll_y)

    def validate_scroll_target_y(self, value: float) -> float:
        return clamp(value, 0, self.max_scroll_y)

    @property
    def max_scroll_x(self) -> int:
        """The maximum value of `scroll_x`."""
        return max(
            0,
            self.virtual_size.width
            - self.container_size.width
            + self.scrollbar_size_vertical,
        )

    @property
    def max_scroll_y(self) -> int:
        """The maximum value of `scroll_y`."""
        return max(
            0,
            self.virtual_size.height
            - self.container_size.height
            + self.scrollbar_size_horizontal,
        )

    @property
    def scrollbar_corner(self) -> ScrollBarCorner:
        """Return the ScrollBarCorner - the cells that appear between the
        horizontal and vertical scrollbars (only when both are visible).
        """
        from .scrollbar import ScrollBarCorner

        if self._scrollbar_corner is not None:
            return self._scrollbar_corner
        self._scrollbar_corner = ScrollBarCorner()
        self.app._start_widget(self, self._scrollbar_corner)
        return self._scrollbar_corner

    @property
    def vertical_scrollbar(self) -> ScrollBar:
        """Get a vertical scrollbar (create if necessary).

        Returns:
            ScrollBar: ScrollBar Widget.
        """
        from .scrollbar import ScrollBar

        if self._vertical_scrollbar is not None:
            return self._vertical_scrollbar
        self._vertical_scrollbar = scroll_bar = ScrollBar(
            vertical=True, name="vertical", thickness=self.scrollbar_size_vertical
        )
        self.app._start_widget(self, scroll_bar)
        return scroll_bar

    @property
    def horizontal_scrollbar(self) -> ScrollBar:
        """Get a vertical scrollbar (create if necessary).

        Returns:
            ScrollBar: ScrollBar Widget.
        """
        from .scrollbar import ScrollBar

        if self._horizontal_scrollbar is not None:
            return self._horizontal_scrollbar
        self._horizontal_scrollbar = scroll_bar = ScrollBar(
            vertical=False, name="horizontal", thickness=self.scrollbar_size_horizontal
        )

        self.app._start_widget(self, scroll_bar)
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
    def scrollbar_size_vertical(self) -> int:
        """Get the width used by the *vertical* scrollbar.

        Returns:
            int: Number of columns in the vertical scrollbar.
        """
        styles = self.styles
        if styles.scrollbar_gutter == "stable" and styles.overflow_y == "auto":
            return styles.scrollbar_size_vertical
        return styles.scrollbar_size_vertical if self.show_vertical_scrollbar else 0

    @property
    def scrollbar_size_horizontal(self) -> int:
        """Get the height used by the *horizontal* scrollbar.

        Returns:
            int: Number of rows in the horizontal scrollbar.
        """
        styles = self.styles
        if styles.scrollbar_gutter == "stable" and styles.overflow_x == "auto":
            return styles.scrollbar_size_horizontal
        return styles.scrollbar_size_horizontal if self.show_horizontal_scrollbar else 0

    @property
    def scrollbar_gutter(self) -> Spacing:
        """Spacing required to fit scrollbar(s).

        Returns:
            Spacing: Scrollbar gutter spacing.
        """
        gutter = Spacing(
            0, self.scrollbar_size_vertical, self.scrollbar_size_horizontal, 0
        )
        return gutter

    @property
    def gutter(self) -> Spacing:
        """Spacing for padding / border / scrollbars.

        Returns:
            Spacing: Additional spacing around content area.

        """
        return self.styles.gutter + self.scrollbar_gutter

    @property
    def size(self) -> Size:
        """The size of the content area.

        Returns:
            Size: Content area size.
        """
        return self.content_region.size

    @property
    def outer_size(self) -> Size:
        """The size of the widget (including padding and border).

        Returns:
            Size: Outer size.
        """
        return self._size

    @property
    def container_size(self) -> Size:
        """The size of the container (parent widget).

        Returns:
            Size: Container size.
        """
        return self._container_size

    @property
    def content_region(self) -> Region:
        """Gets an absolute region containing the content (minus padding and border).

        Returns:
            Region: Screen region that contains a widget's content.
        """
        content_region = self.region.shrink(self.styles.gutter)
        return content_region

    @property
    def content_offset(self) -> Offset:
        """An offset from the Widget origin where the content begins.

        Returns:
            Offset: Offset from widget's origin.

        """
        x, y = self.gutter.top_left
        return Offset(x, y)

    @property
    def region(self) -> Region:
        """The region occupied by this widget, relative to the Screen.

        Raises:
            NoScreen: If there is no screen.
            errors.NoWidget: If the widget is not on the screen.

        Returns:
            Region: Region within screen occupied by widget.
        """
        try:
            return self.screen.find_widget(self).region
        except NoScreen:
            return Region()
        except errors.NoWidget:
            return Region()

    @property
    def container_viewport(self) -> Region:
        """The viewport region (parent window).

        Returns:
            Region: The region that contains this widget.
        """
        if self.parent is None:
            return self.size.region
        assert isinstance(self.parent, Widget)
        return self.parent.region

    @property
    def virtual_region(self) -> Region:
        """The widget region relative to it's container. Which may not be visible,
        depending on scroll offset.
        """
        try:
            return self.screen.find_widget(self).virtual_region
        except NoScreen:
            return Region()
        except errors.NoWidget:
            return Region()

    @property
    def window_region(self) -> Region:
        """The region within the scrollable area that is currently visible.

        Returns:
            Region: New region.
        """
        window_region = self.region.at_offset(self.scroll_offset)
        return window_region

    @property
    def virtual_region_with_margin(self) -> Region:
        """The widget region relative to its container (*including margin*), which may not be visible,
        depending on the scroll offset.

        Returns:
            Region: The virtual region of the Widget, inclusive of its margin.
        """
        return self.virtual_region.grow(self.styles.margin)

    @property
    def focusable_children(self) -> list[Widget]:
        """Get the children which may be focused.

        Returns:
            list[Widget]: List of widgets that can receive focus.

        """
        focusable = [
            child for child in self.children if child.display and child.visible
        ]
        return sorted(focusable, key=attrgetter("_focus_sort_key"))

    @property
    def _focus_sort_key(self) -> tuple[int, int]:
        """Key function to sort widgets in to focus order."""
        x, y, _, _ = self.virtual_region
        top, _, _, left = self.styles.margin
        return y - top, x - left

    @property
    def scroll_offset(self) -> Offset:
        """Get the current scroll offset.

        Returns:
            Offset: Offset a container has been scrolled by.
        """
        return Offset(int(self.scroll_x), int(self.scroll_y))

    @property
    def is_transparent(self) -> bool:
        """Check if the background styles is not set.

        Returns:
            bool: ``True`` if there is background color, otherwise ``False``.
        """
        return self.is_scrollable and self.styles.background.is_transparent

    @property
    def _console(self) -> Console:
        """Get the current console.

        Returns:
            Console: A Rich console object.

        """
        return active_app.get().console

    @property
    def animate(self) -> BoundAnimator:
        """Get an animator to animate attributes on this widget.

        Example:
            ```python
            self.animate("brightness", 0.5)
            ```

        Returns:
            BoundAnimator: An animator bound to this widget.
        """
        if self._animate is None:
            self._animate = self.app.animator.bind(self)
        assert self._animate is not None
        return self._animate

    @property
    def _layout(self) -> Layout:
        """Get the layout object if set in styles, or a default layout.

        Returns:
            Layout: A layout object.

        """
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
        return self.styles.layout is not None or bool(self.children)

    @property
    def layer(self) -> str:
        """Get the name of this widgets layer.

        Returns:
            str: Name of layer.

        """
        return self.styles.layer or "default"

    @property
    def layers(self) -> tuple[str, ...]:
        """Layers of from parent.

        Returns:
            tuple[str, ...]: Tuple of layer names.
        """
        for node in self.ancestors:
            if not isinstance(node, Widget):
                break
            if node.styles.has_rule("layers"):
                return node.styles.layers
        return ("default",)

    def _set_dirty(self, *regions: Region) -> None:
        """Set the Widget as 'dirty' (requiring re-paint).

        Regions should be specified as positional args. If no regions are added, then
        the entire widget will be considered dirty.

        Args:
            *regions (Region): Regions which require a repaint.

        """
        if regions:
            content_offset = self.content_offset
            widget_regions = [region.translate(content_offset) for region in regions]
            self._dirty_regions.update(widget_regions)
            self._repaint_regions.update(widget_regions)
            self._styles_cache.set_dirty(*widget_regions)
        else:
            self._dirty_regions.clear()
            self._repaint_regions.clear()
            self._styles_cache.clear()
            self._dirty_regions.add(self.outer_size.region)
            self._repaint_regions.add(self.outer_size.region)

    def _exchange_repaint_regions(self) -> Collection[Region]:
        """Get a copy of the regions which need a repaint, and clear internal cache.

        Returns:
            Collection[Region]: Regions to repaint.
        """
        regions = self._repaint_regions.copy()
        self._repaint_regions.clear()
        return regions

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
            x (int | None, optional): X coordinate (column) to scroll to, or None for no change. Defaults to None.
            y (int | None, optional): Y coordinate (row) to scroll to, or None for no change. Defaults to None.
            animate (bool, optional): Animate to new scroll position. Defaults to True.
            speed (float | None, optional): Speed of scroll if animate is True. Or None to use duration.
            duration (float | None, optional): Duration of animation, if animate is True and speed is False.

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
            speed (float | None, optional): Speed of scroll if animate is True. Or None to use duration.
            duration (float | None, optional): Duration of animation, if animate is True and speed is False.

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
        """Scroll to home position.

        Args:
            animate (bool, optional): Animate scroll. Defaults to True.

        Returns:
            bool: True if any scrolling was done.
        """
        return self.scroll_to(0, 0, animate=animate, duration=1)

    def scroll_end(self, *, animate: bool = True) -> bool:
        """Scroll to the end of the container.

        Args:
            animate (bool, optional): Animate scroll. Defaults to True.

        Returns:
            bool: True if any scrolling was done.

        """
        return self.scroll_to(0, self.max_scroll_y, animate=animate, duration=1)

    def scroll_left(self, *, animate: bool = True) -> bool:
        """Scroll one cell left.

        Args:
            animate (bool, optional): Animate scroll. Defaults to True.

        Returns:
            bool: True if any scrolling was done.

        """
        return self.scroll_to(x=self.scroll_target_x - 1, animate=animate)

    def scroll_right(self, *, animate: bool = True) -> bool:
        """Scroll on cell right.

        Args:
            animate (bool, optional): Animate scroll. Defaults to True.

        Returns:
            bool: True if any scrolling was done.

        """
        return self.scroll_to(x=self.scroll_target_x + 1, animate=animate)

    def scroll_down(self, *, animate: bool = True) -> bool:
        """Scroll one line down.

        Args:
            animate (bool, optional): Animate scroll. Defaults to True.

        Returns:
            bool: True if any scrolling was done.

        """
        return self.scroll_to(y=self.scroll_target_y + 1, animate=animate)

    def scroll_up(self, *, animate: bool = True) -> bool:
        """Scroll one line up.

        Args:
            animate (bool, optional): Animate scroll. Defaults to True.

        Returns:
            bool: True if any scrolling was done.

        """
        return self.scroll_to(y=self.scroll_target_y - 1, animate=animate)

    def scroll_page_up(self, *, animate: bool = True) -> bool:
        """Scroll one page up.

        Args:
            animate (bool, optional): Animate scroll. Defaults to True.

        Returns:
            bool: True if any scrolling was done.

        """
        return self.scroll_to(
            y=self.scroll_target_y - self.container_size.height, animate=animate
        )

    def scroll_page_down(self, *, animate: bool = True) -> bool:
        """Scroll one page down.

        Args:
            animate (bool, optional): Animate scroll. Defaults to True.

        Returns:
            bool: True if any scrolling was done.

        """
        return self.scroll_to(
            y=self.scroll_target_y + self.container_size.height, animate=animate
        )

    def scroll_page_left(self, *, animate: bool = True) -> bool:
        """Scroll one page left.

        Args:
            animate (bool, optional): Animate scroll. Defaults to True.

        Returns:
            bool: True if any scrolling was done.

        """
        return self.scroll_to(
            x=self.scroll_target_x - self.container_size.width,
            animate=animate,
            duration=0.3,
        )

    def scroll_page_right(self, *, animate: bool = True) -> bool:
        """Scroll one page right.

        Args:
            animate (bool, optional): Animate scroll. Defaults to True.

        Returns:
            bool: True if any scrolling was done.

        """
        return self.scroll_to(
            x=self.scroll_target_x + self.container_size.width,
            animate=animate,
            duration=0.3,
        )

    def scroll_to_widget(self, widget: Widget, *, animate: bool = True) -> bool:
        """Scroll scrolling to bring a widget in to view.

        Args:
            widget (Widget): A descendant widget.
            animate (bool, optional): True to animate, or False to jump. Defaults to True.

        Returns:
            bool: True if any scrolling has occurred in any descendant, otherwise False.
        """

        # Grow the region by the margin so to keep the margin in view.
        region = widget.virtual_region_with_margin
        scrolled = False

        while isinstance(widget.parent, Widget) and widget is not self:
            container = widget.parent
            scroll_offset = container.scroll_to_region(
                region, spacing=widget.parent.gutter, animate=animate
            )
            if scroll_offset:
                scrolled = True

            # Adjust the region by the amount we just scrolled it, and convert to
            # it's parent's virtual coordinate system.
            region = (
                (
                    region.translate(-scroll_offset)
                    .translate(-widget.scroll_offset)
                    .translate(container.virtual_region.offset)
                )
                .grow(container.styles.margin)
                .intersection(container.virtual_region)
            )
            widget = container
        return scrolled

    def scroll_to_region(
        self, region: Region, *, spacing: Spacing | None = None, animate: bool = True
    ) -> Offset:
        """Scrolls a given region in to view, if required.

        This method will scroll the least distance required to move `region` fully within
        the scrollable area.

        Args:
            region (Region): A region that should be visible.
            spacing (Spacing | None, optional): Optional spacing around the region. Defaults to None.
            animate (bool, optional): Enable animation. Defaults to True.
            spacing (Spacing): Space to subtract from the window region.

        Returns:
            Offset: The distance that was scrolled.
        """
        window = self.content_region.at_offset(self.scroll_offset)
        if spacing is not None:
            window = window.shrink(spacing)

        if window in region:
            return Offset()

        delta_x, delta_y = Region.get_scroll_to_visible(window, region)
        scroll_x, scroll_y = self.scroll_offset
        delta = Offset(
            clamp(scroll_x + delta_x, 0, self.max_scroll_x) - scroll_x,
            clamp(scroll_y + delta_y, 0, self.max_scroll_y) - scroll_y,
        )
        if delta:
            self.scroll_relative(
                delta.x or None,
                delta.y or None,
                animate=animate if (abs(delta_y) > 1 or delta_x) else False,
                duration=0.2,
            )
        return delta

    def scroll_visible(self) -> None:
        """Scroll the container to make this widget visible."""
        parent = self.parent
        if isinstance(parent, Widget):
            self.call_later(parent.scroll_to_widget, self)

    def __init_subclass__(
        cls,
        can_focus: bool | None = None,
        can_focus_children: bool | None = None,
        inherit_css: bool = True,
    ) -> None:
        base = cls.__mro__[0]
        super().__init_subclass__(inherit_css=inherit_css)
        if issubclass(base, Widget):
            cls.can_focus = base.can_focus if can_focus is None else can_focus
            cls.can_focus_children = (
                base.can_focus_children
                if can_focus_children is None
                else can_focus_children
            )

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

        scrollbar_size_horizontal = self.styles.scrollbar_size_horizontal
        scrollbar_size_vertical = self.styles.scrollbar_size_vertical

        if self.styles.scrollbar_gutter == "stable":
            # Let's _always_ reserve some space, whether the scrollbar is actually displayed or not:
            show_vertical_scrollbar = True
            scrollbar_size_vertical = self.styles.scrollbar_size_vertical

        if show_horizontal_scrollbar and show_vertical_scrollbar:
            (region, _, _, _) = region.split(
                -scrollbar_size_vertical,
                -scrollbar_size_horizontal,
            )
        elif show_vertical_scrollbar:
            region, _ = region.split_vertical(-scrollbar_size_vertical)
        elif show_horizontal_scrollbar:
            region, _ = region.split_horizontal(-scrollbar_size_horizontal)
        return region

    def _arrange_scrollbars(self, region: Region) -> Iterable[tuple[Widget, Region]]:
        """Arrange the 'chrome' widgets (typically scrollbars) for a layout element.

        Args:
            region (Region): The containing region.

        Returns:
            Iterable[tuple[Widget, Region]]: Tuples of scrollbar Widget and region.

        """

        show_vertical_scrollbar, show_horizontal_scrollbar = self.scrollbars_enabled

        scrollbar_size_horizontal = self.scrollbar_size_horizontal
        scrollbar_size_vertical = self.scrollbar_size_vertical

        if show_horizontal_scrollbar and show_vertical_scrollbar:
            (
                _,
                vertical_scrollbar_region,
                horizontal_scrollbar_region,
                scrollbar_corner_gap,
            ) = region.split(
                -scrollbar_size_vertical,
                -scrollbar_size_horizontal,
            )
            if scrollbar_corner_gap:
                yield self.scrollbar_corner, scrollbar_corner_gap
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
        """Pseudo classes for a widget.

        Returns:
            Iterable[str]: Names of the pseudo classes.

        """
        if self.mouse_over:
            yield "hover"
        if self.has_focus:
            yield "focus"
        if self.descendant_has_focus:
            yield "focus-within"

    def post_render(self, renderable: RenderableType) -> ConsoleRenderable:
        """Applies style attributes to the default renderable.

        Returns:
            RenderableType: A new renderable.
        """
        text_justify: JustifyMethod | None = None
        if self.styles.has_rule("text_align"):
            text_align: JustifyMethod = cast(JustifyMethod, self.styles.text_align)
            text_justify = _JUSTIFY_MAP.get(text_align, text_align)

        if isinstance(renderable, str):
            renderable = Text.from_markup(renderable, justify=text_justify)

        rich_style = self.rich_style
        if isinstance(renderable, Text):
            renderable.stylize(rich_style)
            if text_justify is not None and renderable.justify is None:
                renderable.justify = text_justify
        else:
            renderable = Styled(renderable, rich_style)

        return renderable

    def watch_mouse_over(self, value: bool) -> None:
        """Update from CSS if mouse over state changes."""
        self.app.update_styles(self)

    def watch_has_focus(self, value: bool) -> None:
        """Update from CSS if has focus state changes."""
        self.app.update_styles(self)

    def _size_updated(
        self, size: Size, virtual_size: Size, container_size: Size
    ) -> None:
        """Called when the widget's size is updated.

        Args:
            size (Size): Screen size.
            virtual_size (Size): Virtual (scrollable) size.
            container_size (Size): Container size (size of parent).
        """
        if self._size != size or self.virtual_size != virtual_size:
            self._size = size
            self.virtual_size = virtual_size
            self._container_size = container_size
            if self.is_scrollable:
                self._refresh_scrollbars()
                width, height = self.container_size
                if self.show_vertical_scrollbar:
                    self.vertical_scrollbar.window_virtual_size = virtual_size.height
                    self.vertical_scrollbar.window_size = (
                        height - self.scrollbar_size_horizontal
                    )
                if self.show_horizontal_scrollbar:
                    self.horizontal_scrollbar.window_virtual_size = virtual_size.width
                    self.horizontal_scrollbar.window_size = (
                        width - self.scrollbar_size_vertical
                    )

                self.scroll_x = self.validate_scroll_x(self.scroll_x)
                self.scroll_y = self.validate_scroll_y(self.scroll_y)
                self.refresh(layout=True)
                self.scroll_to(self.scroll_x, self.scroll_y)
            else:
                self.refresh()

    def _render_content(self) -> None:
        """Render all lines."""
        width, height = self.size
        renderable = self.render()
        renderable = self.post_render(renderable)
        options = self._console.options.update_dimensions(width, height).update(
            highlight=False
        )

        segments = self._console.render(renderable, options)
        lines = list(
            islice(
                Segment.split_and_crop_lines(
                    segments, width, include_new_lines=False, pad=False
                ),
                None,
                height,
            )
        )

        styles = self.styles
        align_horizontal, align_vertical = styles.content_align
        lines = list(
            align_lines(
                lines,
                Style(),
                self.size,
                align_horizontal,
                align_vertical,
            )
        )

        self._render_cache = RenderCache(self.size, lines)
        self._dirty_regions.clear()

    def render_line(self, y: int) -> list[Segment]:
        """Render a line of content.

        Args:
            y (int): Y Coordinate of line.

        Returns:
            list[Segment]: A rendered line.
        """
        if self._dirty_regions:
            self._render_content()
        line = self._render_cache.lines[y]
        return line

    def render_lines(self, crop: Region) -> Lines:
        """Render the widget in to lines.

        Args:
            crop (Region): Region within visible area to render.

        Returns:
            Lines: A list of list of segments.
        """
        lines = self._styles_cache.render_widget(self, crop)
        return lines

    def get_style_at(self, x: int, y: int) -> Style:
        """Get the Rich style at a given screen offset.

        Args:
            x (int): X coordinate relative to the screen.
            y (int): Y coordinate relative to the screen.

        Returns:
            Style: A rich Style object.
        """
        offset_x, offset_y = self.screen.get_offset(self)
        return self.screen.get_style_at(x + offset_x, y + offset_y)

    async def _forward_event(self, event: events.Event) -> None:
        event.set_forwarded()
        await self.post_message(event)

    def refresh(
        self, *regions: Region, repaint: bool = True, layout: bool = False
    ) -> None:
        """Initiate a refresh of the widget.

        This method sets an internal flag to perform a refresh, which will be done on the
        next idle event. Only one refresh will be done even if this method is called multiple times.

        By default this method will cause the content of the widget to refresh, but not change its size. You can also
        set `layout=True` to perform a layout.

        !!! warning

            It is rarely necessary to call this method explicitly. Updating styles or reactive attributes will
            do this automatically.

        Args:
            *regions (Region, optional): Additional screen regions to mark as dirty.
            repaint (bool, optional): Repaint the widget (will call render() again). Defaults to True.
            layout (bool, optional): Also layout widgets in the view. Defaults to False.
        """

        if layout:
            self._layout_required = True
            if isinstance(self._parent, Widget):
                self._parent._clear_arrangement_cache()

        if repaint:
            self._set_dirty(*regions)
            self._content_width_cache = (None, 0)
            self._content_height_cache = (None, 0)
            self._rich_style_cache.clear()
            self._repaint_required = True
            if isinstance(self.parent, Widget) and self.styles.auto_dimensions:
                self.parent.refresh(layout=True)

        self.check_idle()

    def remove(self) -> None:
        """Remove the Widget from the DOM (effectively deleting it)"""
        self.app.post_message_no_wait(events.Remove(self, widget=self))

    def render(self) -> RenderableType:
        """Get renderable for widget.

        Returns:
            RenderableType: Any renderable
        """
        render = "" if self.is_container else self.css_identifier_styled
        return render

    async def action(self, action: str) -> None:
        """Perform a given action, with this widget as the default namespace.

        Args:
            action (str): Action encoded as a string.
        """
        await self.app.action(action, self)

    async def post_message(self, message: Message) -> bool:
        """Post a message to this widget.

        Args:
            message (Message): Message to post.

        Returns:
            bool: True if the message was posted, False if this widget was closed / closing.
        """
        if not self.check_message_enabled(message):
            return True
        if not self.is_running:
            self.log.warning(self, f"IS NOT RUNNING, {message!r} not sent")
        return await super().post_message(message)

    async def _on_idle(self, event: events.Idle) -> None:
        """Called when there are no more events on the queue.

        Args:
            event (events.Idle): Idle event.
        """
        if self._parent is not None and not self._closing:
            try:
                screen = self.screen
            except NoScreen:
                pass
            else:
                if self._repaint_required:
                    self._repaint_required = False
                    screen.post_message_no_wait(messages.Update(self, self))
                if self._layout_required:
                    self._layout_required = False
                    screen.post_message_no_wait(messages.Layout(self))

    def focus(self, scroll_visible: bool = True) -> None:
        """Give focus to this widget.

        Args:
            scroll_visible (bool, optional): Scroll parent to make this widget
                visible. Defaults to True.
        """
        self.app.set_focus(self, scroll_visible=scroll_visible)

    def capture_mouse(self, capture: bool = True) -> None:
        """Capture (or release) the mouse.

        When captured, mouse events will go to this widget even when the pointer is not directly over the widget.

        Args:
            capture (bool, optional): True to capture or False to release. Defaults to True.
        """
        self.app.capture_mouse(self if capture else None)

    def release_mouse(self) -> None:
        """Release the mouse.

        Mouse events will only be sent when the mouse is over the widget.
        """
        self.app.capture_mouse(None)

    async def broker_event(self, event_name: str, event: events.Event) -> bool:
        return await self.app._broker_event(event_name, event, default_namespace=self)

    def _on_styles_updated(self) -> None:
        self._rich_style_cache.clear()

    async def _on_mouse_down(self, event: events.MouseUp) -> None:
        await self.broker_event("mouse.down", event)

    async def _on_mouse_up(self, event: events.MouseUp) -> None:
        await self.broker_event("mouse.up", event)

    async def _on_click(self, event: events.Click) -> None:
        await self.broker_event("click", event)

    async def _on_key(self, event: events.Key) -> None:
        try:
            binding = self._bindings.get_key(event.key)
        except NoBinding:
            await self.dispatch_key(event)
        else:
            await self.action(binding.action)

    def _on_compose(self, event: events.Compose) -> None:
        widgets = self.compose()
        self.app.mount_all(widgets)

    def _on_mount(self, event: events.Mount) -> None:
        widgets = self.compose()
        self.mount(*widgets)
        self.screen.refresh(repaint=False, layout=True)

    def _on_leave(self, event: events.Leave) -> None:
        self.mouse_over = False

    def _on_enter(self, event: events.Enter) -> None:
        self.mouse_over = True

    def _on_focus(self, event: events.Focus) -> None:
        self.emit_no_wait(events.DescendantFocus(self))
        self.has_focus = True
        self.refresh()

    def _on_blur(self, event: events.Blur) -> None:
        self.emit_no_wait(events.DescendantBlur(self))
        self.has_focus = False
        self.refresh()

    def _on_descendant_focus(self, event: events.DescendantFocus) -> None:
        self.descendant_has_focus = True
        if "focus-within" in self.pseudo_classes:
            sender = event.sender
            for child in self.walk_children(False):
                child.refresh()
                if child is sender:
                    break

    def _on_descendant_blur(self, event: events.DescendantBlur) -> None:
        self.descendant_has_focus = False
        if "focus-within" in self.pseudo_classes:
            sender = event.sender
            for child in self.walk_children(False):
                child.refresh()
                if child is sender:
                    break

    def _on_mouse_scroll_down(self, event) -> None:
        if self.allow_vertical_scroll:
            if self.scroll_down(animate=False):
                event.stop()

    def _on_mouse_scroll_up(self, event) -> None:
        if self.allow_vertical_scroll:
            if self.scroll_up(animate=False):
                event.stop()

    def _on_scroll_to(self, message: ScrollTo) -> None:
        if self._allow_scroll:
            self.scroll_to(message.x, message.y, animate=message.animate, duration=0.1)
            message.stop()

    def _on_scroll_up(self, event: ScrollUp) -> None:
        if self.allow_vertical_scroll:
            self.scroll_page_up()
            event.stop()

    def _on_scroll_down(self, event: ScrollDown) -> None:
        if self.allow_vertical_scroll:
            self.scroll_page_down()
            event.stop()

    def _on_scroll_left(self, event: ScrollLeft) -> None:
        if self.allow_horizontal_scroll:
            self.scroll_page_left()
            event.stop()

    def _on_scroll_right(self, event: ScrollRight) -> None:
        if self.allow_horizontal_scroll:
            self.scroll_page_right()
            event.stop()

    def _on_hide(self, event: events.Hide) -> None:
        if self.has_focus:
            self.app._reset_focus(self)

    def _on_scroll_to_region(self, message: messages.ScrollToRegion) -> None:
        self.scroll_to_region(message.region, animate=True)

    def _key_home(self) -> bool:
        if self._allow_scroll:
            self.scroll_home()
            return True
        return False

    def _key_end(self) -> bool:
        if self._allow_scroll:
            self.scroll_end()
            return True
        return False

    def _key_left(self) -> bool:
        if self.allow_horizontal_scroll:
            self.scroll_left()
            return True
        return False

    def _key_right(self) -> bool:
        if self.allow_horizontal_scroll:
            self.scroll_right()
            return True
        return False

    def _key_down(self) -> bool:
        if self.allow_vertical_scroll:
            self.scroll_down()
            return True
        return False

    def _key_up(self) -> bool:
        if self.allow_vertical_scroll:
            self.scroll_up()
            return True
        return False

    def _key_pagedown(self) -> bool:
        if self.allow_vertical_scroll:
            self.scroll_page_down()
            return True
        return False

    def _key_pageup(self) -> bool:
        if self.allow_vertical_scroll:
            self.scroll_page_up()
            return True
        return False
