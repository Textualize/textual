from __future__ import annotations

from asyncio import Lock, wait
from collections import Counter
from fractions import Fraction
from itertools import islice
from operator import attrgetter
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Collection,
    Generator,
    Iterable,
    NamedTuple,
    Sequence,
    TypeVar,
    cast,
    overload,
)

import rich.repr
from rich.console import (
    Console,
    ConsoleOptions,
    ConsoleRenderable,
    JustifyMethod,
    RenderableType,
    RenderResult,
    RichCast,
)
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style
from rich.text import Text
from rich.traceback import Traceback
from typing_extensions import Self

from . import constants, errors, events, messages
from ._animator import DEFAULT_EASING, Animatable, BoundAnimator, EasingFunction
from ._arrange import DockArrangeResult, arrange
from ._asyncio import create_task
from ._cache import FIFOCache
from ._compose import compose
from ._context import NoActiveAppError, active_app
from ._easing import DEFAULT_SCROLL_EASING
from ._layout import Layout
from ._segment_tools import align_lines
from ._styles_cache import StylesCache
from .actions import SkipAction
from .await_remove import AwaitRemove
from .binding import Binding
from .box_model import BoxModel
from .css.query import NoMatches, WrongType
from .css.scalar import ScalarOffset
from .dom import DOMNode, NoScreen
from .geometry import Offset, Region, Size, Spacing, clamp
from .layouts.vertical import VerticalLayout
from .message import Message
from .messages import CallbackType
from .reactive import Reactive
from .render import measure
from .strip import Strip
from .walk import walk_depth_first

if TYPE_CHECKING:
    from .app import App, ComposeResult
    from .message_pump import MessagePump
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


class AwaitMount:
    """An awaitable returned by mount() and mount_all().

    Example:
        await self.mount(Static("foo"))

    """

    def __init__(self, parent: Widget, widgets: Sequence[Widget]) -> None:
        self._parent = parent
        self._widgets = widgets

    async def __call__(self) -> None:
        """Allows awaiting via a call operation."""
        await self

    def __await__(self) -> Generator[None, None, None]:
        async def await_mount() -> None:
            if self._widgets:
                aws = [
                    create_task(widget._mounted_event.wait(), name="await mount")
                    for widget in self._widgets
                ]
                if aws:
                    await wait(aws)
                    self._parent.refresh(layout=True)

        return await_mount().__await__()


class _Styled:
    """Apply a style to a renderable.

    Args:
        renderable: Any renderable.
        style: A style to apply across the entire renderable.
    """

    def __init__(
        self, renderable: "ConsoleRenderable", style: Style, link_style: Style | None
    ) -> None:
        self.renderable = renderable
        self.style = style
        self.link_style = link_style

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        style = console.get_style(self.style)
        result_segments = console.render(self.renderable, options)

        _Segment = Segment
        if style:
            apply = style.__add__
            result_segments = (
                _Segment(text, apply(_style), None)
                for text, _style, control in result_segments
            )
        link_style = self.link_style
        if link_style:
            result_segments = (
                _Segment(
                    text,
                    (
                        style
                        if style._meta is None
                        else (style + link_style if "@click" in style.meta else style)
                    ),
                    control,
                )
                for text, style, control in result_segments
                if style is not None
            )
        return result_segments

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return Measurement.get(console, options, self.renderable)


class RenderCache(NamedTuple):
    """Stores results of a previous render."""

    size: Size
    lines: list[Strip]


class WidgetError(Exception):
    """Base widget error."""


class MountError(WidgetError):
    """Error raised when there was a problem with the mount request."""


class PseudoClasses(NamedTuple):
    """Used for render/render_line based widgets that use caching. This structure can be used as a
    cache-key."""

    enabled: bool
    focus: bool
    hover: bool


class _BorderTitle:
    """Descriptor to set border titles."""

    def __set_name__(self, owner: Widget, name: str) -> None:
        # The private name where we store the real data.
        self._internal_name = f"_{name}"

    def __set__(self, obj: Widget, title: str | Text | None) -> None:
        """Setting a title accepts a str, Text, or None."""
        if title is None:
            setattr(obj, self._internal_name, None)
        else:
            # We store the title as Text
            new_title = obj.render_str(title)
            new_title.expand_tabs(4)
            new_title = new_title.split()[0]
            setattr(obj, self._internal_name, new_title)
        obj.refresh()

    def __get__(self, obj: Widget, objtype: type[Widget] | None = None) -> str | None:
        """Getting a title will return None or a str as console markup."""
        title: Text | None = getattr(obj, self._internal_name, None)
        if title is None:
            return None
        # If we have a title, convert from Text to console markup
        return title.markup


@rich.repr.auto
class Widget(DOMNode):
    """
    A Widget is the base class for Textual widgets.

    See also [static][textual.widgets._static.Static] for starting point for your own widgets.

    """

    BINDINGS = [
        Binding("up", "scroll_up", "Scroll Up", show=False),
        Binding("down", "scroll_down", "Scroll Down", show=False),
        Binding("left", "scroll_left", "Scroll Up", show=False),
        Binding("right", "scroll_right", "Scroll Right", show=False),
        Binding("home", "scroll_home", "Scroll Home", show=False),
        Binding("end", "scroll_end", "Scroll End", show=False),
        Binding("pageup", "page_up", "Page Up", show=False),
        Binding("pagedown", "page_down", "Page Down", show=False),
    ]

    DEFAULT_CSS = """
    Widget{
        scrollbar-background: $panel-darken-1;
        scrollbar-background-hover: $panel-darken-2;
        scrollbar-background-active: $panel-darken-3;
        scrollbar-color: $primary-lighten-1;
        scrollbar-color-active: $warning-darken-1;
        scrollbar-color-hover: $primary-lighten-1;
        scrollbar-corner-color: $panel-darken-1;
        scrollbar-size-vertical: 2;
        scrollbar-size-horizontal: 1;
        link-background:;
        link-color: $text;
        link-style: underline;
        link-hover-background: $accent;
        link-hover-color: $text;
        link-hover-style: bold not underline;
    }
    """
    COMPONENT_CLASSES: ClassVar[set[str]] = set()

    can_focus: bool = False
    """Widget may receive focus."""
    can_focus_children: bool = True
    """Widget's children may receive focus."""
    expand = Reactive(False)
    """Rich renderable may expand."""
    shrink = Reactive(True)
    """Rich renderable may shrink."""
    auto_links = Reactive(True)
    """Widget will highlight links automatically."""
    disabled = Reactive(False)
    """The disabled state of the widget. `True` if disabled, `False` if not."""

    hover_style: Reactive[Style] = Reactive(Style, repaint=False)
    highlight_link_id: Reactive[str] = Reactive("")

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        self._size = Size(0, 0)
        self._container_size = Size(0, 0)
        self._layout_required = False
        self._repaint_required = False
        self._scroll_required = False
        self._default_layout = VerticalLayout()
        self._animate: BoundAnimator | None = None
        self.highlight_style: Style | None = None

        self._vertical_scrollbar: ScrollBar | None = None
        self._horizontal_scrollbar: ScrollBar | None = None
        self._scrollbar_corner: ScrollBarCorner | None = None

        self._border_title: Text | None = None
        self._border_subtitle: Text | None = None

        self._render_cache = RenderCache(Size(0, 0), [])
        # Regions which need to be updated (in Widget)
        self._dirty_regions: set[Region] = set()
        # Regions which need to be transferred from cache to screen
        self._repaint_regions: set[Region] = set()

        # Cache the auto content dimensions
        # TODO: add mechanism to explicitly clear this
        self._content_width_cache: tuple[object, int] = (None, 0)
        self._content_height_cache: tuple[object, int] = (None, 0)

        self._arrangement_cache: FIFOCache[
            tuple[Size, int], DockArrangeResult
        ] = FIFOCache(4)

        self._styles_cache = StylesCache()
        self._rich_style_cache: dict[str, tuple[Style, Style]] = {}
        self._stabilize_scrollbar: tuple[Size, str, str] | None = None
        """Used to prevent scrollbar logic getting stuck in an infinite loop."""

        self._lock = Lock()

        super().__init__(
            name=name,
            id=id,
            classes=self.DEFAULT_CLASSES if classes is None else classes,
        )

        if self in children:
            raise WidgetError("A widget can't be its own parent")

        for child in children:
            if not isinstance(child, Widget):
                raise TypeError(
                    f"Widget positional arguments must be Widget subclasses; not {child!r}"
                )

        self._add_children(*children)
        self.disabled = disabled

    virtual_size = Reactive(Size(0, 0), layout=True)
    auto_width = Reactive(True)
    auto_height = Reactive(True)
    has_focus = Reactive(False, repaint=False)
    mouse_over = Reactive(False, repaint=False)
    scroll_x = Reactive(0.0, repaint=False, layout=False)
    scroll_y = Reactive(0.0, repaint=False, layout=False)
    scroll_target_x = Reactive(0.0, repaint=False)
    scroll_target_y = Reactive(0.0, repaint=False)
    show_vertical_scrollbar = Reactive(False, layout=True)
    show_horizontal_scrollbar = Reactive(False, layout=True)

    border_title = _BorderTitle()
    """A title to show in the top border (if there is one)."""
    border_subtitle = _BorderTitle()
    """A title to show in the bottom border (if there is one)."""

    @property
    def siblings(self) -> list[Widget]:
        """Get the widget's siblings (self is removed from the return list).

        Returns:
            A list of siblings.
        """
        parent = self.parent
        if parent is not None:
            siblings = list(parent._nodes)
            siblings.remove(self)
            return siblings
        else:
            return []

    @property
    def visible_siblings(self) -> list[Widget]:
        """A list of siblings which will be shown.

        Returns:
            List of siblings.
        """
        siblings = [
            widget for widget in self.siblings if widget.visible and widget.display
        ]
        return siblings

    @property
    def allow_vertical_scroll(self) -> bool:
        """Check if vertical scroll is permitted.

        May be overridden if you want different logic regarding allowing scrolling.

        Returns:
            True if the widget may scroll _vertically_.
        """
        return self.is_scrollable and self.show_vertical_scrollbar

    @property
    def allow_horizontal_scroll(self) -> bool:
        """Check if horizontal scroll is permitted.

        May be overridden if you want different logic regarding allowing scrolling.

        Returns:
            True if the widget may scroll _horizontally_.
        """
        return self.is_scrollable and self.show_horizontal_scrollbar

    @property
    def _allow_scroll(self) -> bool:
        """Check if both axis may be scrolled.

        Returns:
            True if horizontal and vertical scrolling is enabled.
        """
        return self.is_scrollable and (
            self.allow_horizontal_scroll or self.allow_vertical_scroll
        )

    @property
    def offset(self) -> Offset:
        """Widget offset from origin.

        Returns:
            Relative offset.
        """
        return self.styles.offset.resolve(self.size, self.app.size)

    @offset.setter
    def offset(self, offset: tuple[int, int]) -> None:
        self.styles.offset = ScalarOffset.from_offset(offset)

    def __enter__(self) -> Self:
        """Use as context manager when composing."""
        self.app._compose_stacks[-1].append(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit compose context manager."""
        compose_stack = self.app._compose_stacks[-1]
        composed = compose_stack.pop()
        if compose_stack:
            compose_stack[-1].compose_add_child(composed)
        else:
            self.app._composed[-1].append(composed)

    ExpectType = TypeVar("ExpectType", bound="Widget")

    @overload
    def get_child_by_id(self, id: str) -> Widget:
        ...

    @overload
    def get_child_by_id(self, id: str, expect_type: type[ExpectType]) -> ExpectType:
        ...

    def get_child_by_id(
        self, id: str, expect_type: type[ExpectType] | None = None
    ) -> ExpectType | Widget:
        """Return the first child (immediate descendent) of this node with the given ID.

        Args:
            id: The ID of the child.
            expect_type: Require the object be of the supplied type, or None for any type.
                Defaults to None.

        Returns:
            The first child of this node with the ID.

        Raises:
            NoMatches: if no children could be found for this ID
            WrongType: if the wrong type was found.
        """
        child = self._nodes._get_by_id(id)
        if child is None:
            raise NoMatches(f"No child found with id={id!r}")
        if expect_type is None:
            return child
        if not isinstance(child, expect_type):
            raise WrongType(
                f"Child with id={id!r} is wrong type; expected {expect_type}, got"
                f" {type(child)}"
            )
        return child

    @overload
    def get_widget_by_id(self, id: str) -> Widget:
        ...

    @overload
    def get_widget_by_id(self, id: str, expect_type: type[ExpectType]) -> ExpectType:
        ...

    def get_widget_by_id(
        self, id: str, expect_type: type[ExpectType] | None = None
    ) -> ExpectType | Widget:
        """Return the first descendant widget with the given ID.

        Performs a depth-first search rooted at this widget.

        Args:
            id: The ID to search for in the subtree.
            expect_type: Require the object be of the supplied type, or None for any type.

        Returns:
            The first descendant encountered with this ID.

        Raises:
            NoMatches: if no children could be found for this ID.
            WrongType: if the wrong type was found.
        """
        # We use Widget as a filter_type so that the inferred type of child is Widget.
        for child in walk_depth_first(self, filter_type=Widget):
            try:
                if expect_type is None:
                    return child.get_child_by_id(id)
                else:
                    return child.get_child_by_id(id, expect_type=expect_type)
            except NoMatches:
                pass
            except WrongType as exc:
                raise WrongType(
                    f"Descendant with id={id!r} is wrong type; expected {expect_type},"
                    f" got {type(child)}"
                ) from exc
        raise NoMatches(f"No descendant found with id={id!r}")

    def get_child_by_type(self, expect_type: type[ExpectType]) -> ExpectType:
        """Get a child of a give type.

        Args:
            expect_type: The type of the expected child.

        Raises:
            NoMatches: If no valid child is found.

        Returns:
            A widget.
        """
        for child in self._nodes:
            # We want the child with the exact type (not subclasses)
            if type(child) is expect_type:
                assert isinstance(child, expect_type)
                return child
        raise NoMatches(f"No immediate child of type {expect_type}; {self._nodes}")

    def get_component_rich_style(self, name: str, *, partial: bool = False) -> Style:
        """Get a *Rich* style for a component.

        Args:
            name: Name of component.
            partial: Return a partial style (not combined with parent).

        Returns:
            A Rich style object.
        """

        if name not in self._rich_style_cache:
            component_styles = self.get_component_styles(name)
            style = component_styles.rich_style
            partial_style = component_styles.partial_rich_style
            self._rich_style_cache[name] = (style, partial_style)

        style, partial_style = self._rich_style_cache[name]

        return partial_style if partial else style

    def render_str(self, text_content: str | Text) -> Text:
        """Convert str in to a Text object.

        If you pass in an existing Text object it will be returned unaltered.

        Args:
            text_content: Text or str.

        Returns:
            A text object.
        """
        text = (
            Text.from_markup(text_content)
            if isinstance(text_content, str)
            else text_content
        )
        return text

    def _arrange(self, size: Size) -> DockArrangeResult:
        """Arrange children.

        Args:
            size: Size of container.

        Returns:
            Widget locations.
        """
        assert self.is_container

        cache_key = (size, self._nodes._updates)
        cached_result = self._arrangement_cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        arrangement = self._arrangement_cache[cache_key] = arrange(
            self, self._nodes, size, self.screen.size
        )

        return arrangement

    def _clear_arrangement_cache(self) -> None:
        """Clear arrangement cache, forcing a new arrange operation."""
        self._arrangement_cache.clear()
        self._stabilize_scrollbar = None

    def _get_virtual_dom(self) -> Iterable[Widget]:
        """Get widgets not part of the DOM.

        Returns:
            An iterable of Widgets.

        """
        if self._horizontal_scrollbar is not None:
            yield self._horizontal_scrollbar
        if self._vertical_scrollbar is not None:
            yield self._vertical_scrollbar
        if self._scrollbar_corner is not None:
            yield self._scrollbar_corner

    def _find_mount_point(self, spot: int | str | "Widget") -> tuple["Widget", int]:
        """Attempt to locate the point where the caller wants to mount something.

        Args:
            spot: The spot to find.

        Returns:
            The parent and the location in its child list.

        Raises:
            MountError: If there was an error finding where to mount a widget.

        The rules of this method are:

        - Given an ``int``, parent is ``self`` and location is the integer value.
        - Given a ``Widget``, parent is the widget's parent and location is
          where the widget is found in the parent's ``children``. If it
          can't be found a ``MountError`` will be raised.
        - Given a string, it is used to perform a ``query_one`` and then the
          result is used as if a ``Widget`` had been given.
        """

        # A numeric location means at that point in our child list.
        if isinstance(spot, int):
            return self, spot

        # If we've got a string, that should be treated like a query that
        # can be passed to query_one. So let's use that to get a widget to
        # work on.
        if isinstance(spot, str):
            spot = self.query_one(spot, Widget)

        # At this point we should have a widget, either because we got given
        # one, or because we pulled one out of the query. First off, does it
        # have a parent? There's no way we can use it as a sibling to make
        # mounting decisions if it doesn't have a parent.
        if spot.parent is None:
            raise MountError(
                f"Unable to find relative location of {spot!r} because it has no parent"
            )

        # We've got a widget. It has a parent. It has (zero or more)
        # children. We should be able to go looking for the widget's
        # location amongst its parent's children.
        try:
            return cast("Widget", spot.parent), spot.parent._nodes.index(spot)
        except ValueError:
            raise MountError(f"{spot!r} is not a child of {self!r}") from None

    def mount(
        self,
        *widgets: Widget,
        before: int | str | Widget | None = None,
        after: int | str | Widget | None = None,
    ) -> AwaitMount:
        """Mount widgets below this widget (making this widget a container).

        Args:
            *widgets: The widget(s) to mount.
            before: Optional location to mount before. An `int` is the index
                of the child to mount before, a `str` is a `query_one` query to
                find the widget to mount before.
            after: Optional location to mount after. An `int` is the index
                of the child to mount after, a `str` is a `query_one` query to
                find the widget to mount after.

        Returns:
            An awaitable object that waits for widgets to be mounted.

        Raises:
            MountError: If there is a problem with the mount request.

        Note:
            Only one of ``before`` or ``after`` can be provided. If both are
            provided a ``MountError`` will be raised.
        """

        # Check for duplicate IDs in the incoming widgets
        ids_to_mount = [widget.id for widget in widgets if widget.id is not None]
        unique_ids = set(ids_to_mount)
        num_unique_ids = len(unique_ids)
        num_widgets_with_ids = len(ids_to_mount)
        if num_unique_ids != num_widgets_with_ids:
            counter = Counter(widget.id for widget in widgets)
            for widget_id, count in counter.items():
                if count > 1:
                    raise MountError(
                        f"Tried to insert {count!r} widgets with the same ID {widget_id!r}. "
                        "Widget IDs must be unique."
                    )

        # Saying you want to mount before *and* after something is an error.
        if before is not None and after is not None:
            raise MountError(
                "Only one of `before` or `after` can be handled -- not both"
            )

        # Decide the final resting place depending on what we've been asked
        # to do.
        insert_before: int | None = None
        insert_after: int | None = None
        if before is not None:
            parent, insert_before = self._find_mount_point(before)
        elif after is not None:
            parent, insert_after = self._find_mount_point(after)
        else:
            parent = self

        mounted = self.app._register(
            parent, *widgets, before=insert_before, after=insert_after
        )

        await_mount = AwaitMount(self, mounted)
        self.call_next(await_mount)
        return await_mount

    def mount_all(
        self,
        widgets: Iterable[Widget],
        *,
        before: int | str | Widget | None = None,
        after: int | str | Widget | None = None,
    ) -> AwaitMount:
        """Mount widgets from an iterable.

        Args:
            widgets: An iterable of widgets.
            before: Optional location to mount before. An `int` is the index
                of the child to mount before, a `str` is a `query_one` query to
                find the widget to mount before.
            after: Optional location to mount after. An `int` is the index
                of the child to mount after, a `str` is a `query_one` query to
                find the widget to mount after.

        Returns:
            An awaitable object that waits for widgets to be mounted.

        Raises:
            MountError: If there is a problem with the mount request.

        Note:
            Only one of ``before`` or ``after`` can be provided. If both are
            provided a ``MountError`` will be raised.
        """
        await_mount = self.mount(*widgets, before=before, after=after)
        return await_mount

    def move_child(
        self,
        child: int | Widget,
        before: int | Widget | None = None,
        after: int | Widget | None = None,
    ) -> None:
        """Move a child widget within its parent's list of children.

        Args:
            child: The child widget to move.
            before: Optional location to move before. An `int` is the index
                of the child to move before, a `str` is a `query_one` query to
                find the widget to move before.
            after: Optional location to move after. An `int` is the index
                of the child to move after, a `str` is a `query_one` query to
                find the widget to move after.

        Raises:
            WidgetError: If there is a problem with the child or target.

        Note:
            Only one of ``before`` or ``after`` can be provided. If neither
            or both are provided a ``WidgetError`` will be raised.
        """

        # One or the other of before or after are required. Can't do
        # neither, can't do both.
        if before is None and after is None:
            raise WidgetError("One of `before` or `after` is required.")
        elif before is not None and after is not None:
            raise WidgetError("Only one of `before` or `after` can be handled.")

        def _to_widget(child: int | Widget, called: str) -> Widget:
            """Ensure a given child reference is a Widget."""
            if isinstance(child, int):
                try:
                    child = self._nodes[child]
                except IndexError:
                    raise WidgetError(
                        f"An index of {child} for the child to {called} is out of bounds"
                    ) from None
            else:
                # We got an actual widget, so let's be sure it really is one of
                # our children.
                try:
                    _ = self._nodes.index(child)
                except ValueError:
                    raise WidgetError(f"{child!r} is not a child of {self!r}") from None
            return child

        # Ensure the child and target are widgets.
        child = _to_widget(child, "move")
        target = _to_widget(
            cast("int | Widget", before if after is None else after), "move towards"
        )

        # At this point we should know what we're moving, and it should be a
        # child; where we're moving it to, which should be within the child
        # list; and how we're supposed to move it. All that's left is doing
        # the right thing.
        self._nodes._remove(child)
        if before is not None:
            self._nodes._insert(self._nodes.index(target), child)
        else:
            self._nodes._insert(self._nodes.index(target) + 1, child)

        # Request a refresh.
        self.refresh(layout=True)

    def compose(self) -> ComposeResult:
        """Called by Textual to create child widgets.

        Extend this to build a UI.

        Example:
            ```python
            def compose(self) -> ComposeResult:
                yield Header()
                yield Container(
                    Tree(), Viewer()
                )
                yield Footer()
            ```

        """
        yield from ()

    def _post_register(self, app: App) -> None:
        """Called when the instance is registered.

        Args:
            app: App instance.
        """
        # Parse the Widget's CSS
        for path, css, tie_breaker in self._get_default_css():
            self.app.stylesheet.add_source(
                css, path=path, is_default_css=True, tie_breaker=tie_breaker
            )

    def _get_box_model(
        self,
        container: Size,
        viewport: Size,
        width_fraction: Fraction,
        height_fraction: Fraction,
    ) -> BoxModel:
        """Process the box model for this widget.

        Args:
            container: The size of the container widget (with a layout)
            viewport: The viewport size.
            width_fraction: A fraction used for 1 `fr` unit on the width dimension.
            height_fraction: A fraction used for 1 `fr` unit on the height dimension.

        Returns:
            The size and margin for this widget.
        """
        styles = self.styles
        _content_width, _content_height = container
        content_width = Fraction(_content_width)
        content_height = Fraction(_content_height)
        is_border_box = styles.box_sizing == "border-box"
        gutter = styles.gutter
        margin = styles.margin

        is_auto_width = styles.width and styles.width.is_auto
        is_auto_height = styles.height and styles.height.is_auto

        # Container minus padding and border
        content_container = container - gutter.totals
        # The container including the content
        sizing_container = content_container if is_border_box else container

        if styles.width is None:
            # No width specified, fill available space
            content_width = Fraction(content_container.width - margin.width)
        elif is_auto_width:
            # When width is auto, we want enough space to always fit the content
            content_width = Fraction(
                self.get_content_width(
                    content_container - styles.margin.totals, viewport
                )
            )
            if styles.scrollbar_gutter == "stable" and styles.overflow_x == "auto":
                content_width += styles.scrollbar_size_vertical
            if (
                content_width < content_container.width
                and self._has_relative_children_width
            ):
                content_width = Fraction(content_container.width)
        else:
            # An explicit width
            styles_width = styles.width
            content_width = styles_width.resolve(
                sizing_container - styles.margin.totals, viewport, width_fraction
            )
            if is_border_box and styles_width.excludes_border:
                content_width -= gutter.width

        if styles.min_width is not None:
            # Restrict to minimum width, if set
            min_width = styles.min_width.resolve(
                content_container, viewport, width_fraction
            )
            content_width = max(content_width, min_width)

        if styles.max_width is not None:
            # Restrict to maximum width, if set
            max_width = styles.max_width.resolve(
                content_container, viewport, width_fraction
            )
            if is_border_box:
                max_width -= gutter.width
            content_width = min(content_width, max_width)

        content_width = max(Fraction(0), content_width)

        if styles.height is None:
            # No height specified, fill the available space
            content_height = Fraction(content_container.height - margin.height)
        elif is_auto_height:
            # Calculate dimensions based on content
            content_height = Fraction(
                self.get_content_height(content_container, viewport, int(content_width))
            )
            if styles.scrollbar_gutter == "stable" and styles.overflow_y == "auto":
                content_height += styles.scrollbar_size_horizontal
            if (
                content_height < content_container.height
                and self._has_relative_children_height
            ):
                content_height = Fraction(content_container.height)
        else:
            styles_height = styles.height
            # Explicit height set
            content_height = styles_height.resolve(
                sizing_container - styles.margin.totals, viewport, height_fraction
            )
            if is_border_box and styles_height.excludes_border:
                content_height -= gutter.height

        if styles.min_height is not None:
            # Restrict to minimum height, if set
            min_height = styles.min_height.resolve(
                content_container, viewport, height_fraction
            )
            content_height = max(content_height, min_height)

        if styles.max_height is not None:
            # Restrict maximum height, if set
            max_height = styles.max_height.resolve(
                content_container, viewport, height_fraction
            )
            content_height = min(content_height, max_height)

        content_height = max(Fraction(0), content_height)

        model = BoxModel(
            content_width + gutter.width, content_height + gutter.height, margin
        )
        return model

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Called by textual to get the width of the content area. May be overridden in a subclass.

        Args:
            container: Size of the container (immediate parent) widget.
            viewport: Size of the viewport.

        Returns:
            The optimal width of the content.
        """
        if self.is_container:
            assert self._layout is not None
            return self._layout.get_content_width(self, container, viewport)

        cache_key = container.width
        if self._content_width_cache[0] == cache_key:
            return self._content_width_cache[1]

        console = self.app.console
        renderable = self._render()

        width = measure(
            console, renderable, container.width, container_width=container.width
        )
        if self.expand:
            width = max(container.width, width)
        if self.shrink:
            width = min(width, container.width)

        self._content_width_cache = (cache_key, width)
        return width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        """Called by Textual to get the height of the content area. May be overridden in a subclass.

        Args:
            container: Size of the container (immediate parent) widget.
            viewport: Size of the viewport.
            width: Width of renderable.

        Returns:
            The height of the content.
        """
        if self.is_container:
            assert self._layout is not None
            height = self._layout.get_content_height(
                self,
                container,
                viewport,
                width,
            )
        else:
            cache_key = width

            if self._content_height_cache[0] == cache_key:
                return self._content_height_cache[1]

            renderable = self.render()
            options = self._console.options.update_width(width).update(highlight=False)
            segments = self._console.render(renderable, options)
            # Cheaper than counting the lines returned from render_lines!
            height = sum([text.count("\n") for text, _, _ in segments])
            self._content_height_cache = (cache_key, height)

        return height

    def watch_hover_style(
        self, previous_hover_style: Style, hover_style: Style
    ) -> None:
        if self.auto_links:
            self.highlight_link_id = hover_style.link_id

    def watch_scroll_x(self, old_value: float, new_value: float) -> None:
        self.horizontal_scrollbar.position = round(new_value)
        if round(old_value) != round(new_value):
            self._refresh_scroll()

    def watch_scroll_y(self, old_value: float, new_value: float) -> None:
        self.vertical_scrollbar.position = round(new_value)
        if round(old_value) != round(new_value):
            self._refresh_scroll()

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
            - (self.container_size.width - self.scrollbar_size_vertical),
        )

    @property
    def max_scroll_y(self) -> int:
        """The maximum value of `scroll_y`."""
        return max(
            0,
            self.virtual_size.height
            - (self.container_size.height - self.scrollbar_size_horizontal),
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
            ScrollBar Widget.
        """
        from .scrollbar import ScrollBar

        if self._vertical_scrollbar is not None:
            return self._vertical_scrollbar
        self._vertical_scrollbar = scroll_bar = ScrollBar(
            vertical=True, name="vertical", thickness=self.scrollbar_size_vertical
        )
        self._vertical_scrollbar.display = False
        self.app._start_widget(self, scroll_bar)
        return scroll_bar

    @property
    def horizontal_scrollbar(self) -> ScrollBar:
        """Get a vertical scrollbar (create if necessary).

        Returns:
            ScrollBar Widget.
        """

        from .scrollbar import ScrollBar

        if self._horizontal_scrollbar is not None:
            return self._horizontal_scrollbar
        self._horizontal_scrollbar = scroll_bar = ScrollBar(
            vertical=False, name="horizontal", thickness=self.scrollbar_size_horizontal
        )
        self._horizontal_scrollbar.display = False
        self.app._start_widget(self, scroll_bar)
        return scroll_bar

    def _refresh_scrollbars(self) -> None:
        """Refresh scrollbar visibility."""
        if not self.is_scrollable or not self.container_size:
            return

        styles = self.styles
        overflow_x = styles.overflow_x
        overflow_y = styles.overflow_y

        stabilize_scrollbar = (
            self.container_size,
            overflow_x,
            overflow_y,
        )
        if self._stabilize_scrollbar == stabilize_scrollbar:
            return

        width, height = self._container_size

        show_horizontal = False
        if overflow_x == "hidden":
            show_horizontal = False
        elif overflow_x == "scroll":
            show_horizontal = True
        elif overflow_x == "auto":
            show_horizontal = self.virtual_size.width > width

        show_vertical = False
        if overflow_y == "hidden":
            show_vertical = False
        elif overflow_y == "scroll":
            show_vertical = True
        elif overflow_y == "auto":
            show_vertical = self.virtual_size.height > height

        # When a single scrollbar is shown, the other dimension changes, so we need to recalculate.
        if overflow_x == "auto" and show_vertical and not show_horizontal:
            show_horizontal = self.virtual_size.width > (
                width - styles.scrollbar_size_vertical
            )
        if overflow_y == "auto" and show_horizontal and not show_vertical:
            show_vertical = self.virtual_size.height > (
                height - styles.scrollbar_size_horizontal
            )

        self._stabilize_scrollbar = stabilize_scrollbar

        self.show_horizontal_scrollbar = show_horizontal
        self.show_vertical_scrollbar = show_vertical

        if self._horizontal_scrollbar is not None or show_horizontal:
            self.horizontal_scrollbar.display = show_horizontal
        if self._vertical_scrollbar is not None or show_vertical:
            self.vertical_scrollbar.display = show_vertical

    @property
    def scrollbars_enabled(self) -> tuple[bool, bool]:
        """A tuple of booleans that indicate if scrollbars are enabled.

        Returns:
            A tuple of (<vertical scrollbar enabled>, <horizontal scrollbar enabled>)

        """
        if not self.is_scrollable:
            return False, False

        enabled = self.show_vertical_scrollbar, self.show_horizontal_scrollbar
        return enabled

    @property
    def scrollbars_space(self) -> tuple[int, int]:
        """The number of cells occupied by scrollbars for width and height"""
        return (self.scrollbar_size_vertical, self.scrollbar_size_horizontal)

    @property
    def scrollbar_size_vertical(self) -> int:
        """Get the width used by the *vertical* scrollbar.

        Returns:
            Number of columns in the vertical scrollbar.
        """
        styles = self.styles
        if styles.scrollbar_gutter == "stable" and styles.overflow_y == "auto":
            return styles.scrollbar_size_vertical
        return styles.scrollbar_size_vertical if self.show_vertical_scrollbar else 0

    @property
    def scrollbar_size_horizontal(self) -> int:
        """Get the height used by the *horizontal* scrollbar.

        Returns:
            Number of rows in the horizontal scrollbar.
        """
        styles = self.styles
        return styles.scrollbar_size_horizontal if self.show_horizontal_scrollbar else 0

    @property
    def scrollbar_gutter(self) -> Spacing:
        """Spacing required to fit scrollbar(s).

        Returns:
            Scrollbar gutter spacing.
        """
        return Spacing(
            0, self.scrollbar_size_vertical, self.scrollbar_size_horizontal, 0
        )

    @property
    def gutter(self) -> Spacing:
        """Spacing for padding / border / scrollbars.

        Returns:
            Additional spacing around content area.

        """
        return self.styles.gutter + self.scrollbar_gutter

    @property
    def size(self) -> Size:
        """The size of the content area.

        Returns:
            Content area size.
        """
        return self.content_region.size

    @property
    def outer_size(self) -> Size:
        """The size of the widget (including padding and border).

        Returns:
            Outer size.
        """
        return self._size

    @property
    def container_size(self) -> Size:
        """The size of the container (parent widget).

        Returns:
            Container size.
        """
        return self._container_size

    @property
    def content_region(self) -> Region:
        """Gets an absolute region containing the content (minus padding and border).

        Returns:
            Screen region that contains a widget's content.
        """
        content_region = self.region.shrink(self.styles.gutter)
        return content_region

    @property
    def scrollable_content_region(self) -> Region:
        """Gets an absolute region containing the scrollable content (minus padding, border, and scrollbars).

        Returns:
            Screen region that contains a widget's content.
        """
        content_region = self.region.shrink(self.styles.gutter).shrink(
            self.scrollbar_gutter
        )
        return content_region

    @property
    def content_offset(self) -> Offset:
        """An offset from the Widget origin where the content begins.

        Returns:
            Offset from widget's origin.

        """
        x, y = self.gutter.top_left
        return Offset(x, y)

    @property
    def content_size(self) -> Size:
        """Get the size of the content area."""
        return self.region.shrink(self.styles.gutter).size

    @property
    def region(self) -> Region:
        """The region occupied by this widget, relative to the Screen.

        Raises:
            NoScreen: If there is no screen.
            errors.NoWidget: If the widget is not on the screen.

        Returns:
            Region within screen occupied by widget.
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
            The region that contains this widget.
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
            New region.
        """
        window_region = self.region.at_offset(self.scroll_offset)
        return window_region

    @property
    def virtual_region_with_margin(self) -> Region:
        """The widget region relative to its container (*including margin*), which may not be visible,
        depending on the scroll offset.

        Returns:
            The virtual region of the Widget, inclusive of its margin.
        """
        return self.virtual_region.grow(self.styles.margin)

    @property
    def _self_or_ancestors_disabled(self) -> bool:
        """Is this widget or any of its ancestors disabled?"""
        return any(
            node.disabled
            for node in self.ancestors_with_self
            if isinstance(node, Widget)
        )

    @property
    def focusable(self) -> bool:
        """Can this widget currently receive focus?"""
        return self.can_focus and not self._self_or_ancestors_disabled

    @property
    def focusable_children(self) -> list[Widget]:
        """Get the children which may be focused.

        Returns:
            List of widgets that can receive focus.

        """
        focusable = [child for child in self._nodes if child.display and child.visible]
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
            Offset a container has been scrolled by.
        """
        return Offset(round(self.scroll_x), round(self.scroll_y))

    @property
    def is_transparent(self) -> bool:
        """Check if the background styles is not set.

        Returns:
            ``True`` if there is background color, otherwise ``False``.
        """
        return self.is_scrollable and self.styles.background.is_transparent

    @property
    def _console(self) -> Console:
        """Get the current console.

        Returns:
            A Rich console object.

        """
        return active_app.get().console

    @property
    def _has_relative_children_width(self) -> bool:
        """Do any children have a relative width?"""
        if not self.is_container:
            return False
        return any(widget.styles.is_relative_width for widget in self.children)

    @property
    def _has_relative_children_height(self) -> bool:
        """Do any children have a relative height?"""
        if not self.is_container:
            return False
        return any(widget.styles.is_relative_height for widget in self.children)

    def animate(
        self,
        attribute: str,
        value: float | Animatable,
        *,
        final_value: object = ...,
        duration: float | None = None,
        speed: float | None = None,
        delay: float = 0.0,
        easing: EasingFunction | str = DEFAULT_EASING,
        on_complete: CallbackType | None = None,
    ) -> None:
        """Animate an attribute.

        Args:
            attribute: Name of the attribute to animate.
            value: The value to animate to.
            final_value: The final value of the animation. Defaults to `value` if not set.
            duration: The duration of the animate. Defaults to None.
            speed: The speed of the animation. Defaults to None.
            delay: A delay (in seconds) before the animation starts. Defaults to 0.0.
            easing: An easing method. Defaults to "in_out_cubic".
            on_complete: A callable to invoke when the animation is finished. Defaults to None.

        """
        if self._animate is None:
            self._animate = self.app.animator.bind(self)
        assert self._animate is not None
        self._animate(
            attribute,
            value,
            final_value=final_value,
            duration=duration,
            speed=speed,
            delay=delay,
            easing=easing,
            on_complete=on_complete,
        )

    @property
    def _layout(self) -> Layout:
        """Get the layout object if set in styles, or a default layout.

        Returns:
            A layout object.

        """
        return self.styles.layout or self._default_layout

    @property
    def is_container(self) -> bool:
        """Check if this widget is a container (contains other widgets).

        Returns:
            True if this widget is a container.
        """
        return self.styles.layout is not None or bool(self._nodes)

    @property
    def is_scrollable(self) -> bool:
        """Check if this Widget may be scrolled.

        Returns:
            True if this widget may be scrolled.
        """
        return self.styles.layout is not None or bool(self._nodes)

    @property
    def layer(self) -> str:
        """Get the name of this widgets layer.

        Returns:
            Name of layer.

        """
        return self.styles.layer or "default"

    @property
    def layers(self) -> tuple[str, ...]:
        """Layers of from parent.

        Returns:
            Tuple of layer names.
        """
        for node in self.ancestors_with_self:
            if not isinstance(node, Widget):
                break
            if node.styles.has_rule("layers"):
                return node.styles.layers
        return ("default",)

    @property
    def link_style(self) -> Style:
        """Style of links."""
        styles = self.styles
        _, background = self.background_colors
        link_background = background + styles.link_background
        link_color = link_background + (
            link_background.get_contrast_text(styles.link_color.a)
            if styles.auto_link_color
            else styles.link_color
        )
        style = styles.link_style + Style.from_color(
            link_color.rich_color,
            link_background.rich_color,
        )
        return style

    @property
    def link_hover_style(self) -> Style:
        """Style of links with mouse hover."""
        styles = self.styles
        _, background = self.background_colors
        hover_background = background + styles.link_hover_background
        hover_color = hover_background + (
            hover_background.get_contrast_text(styles.link_hover_color.a)
            if styles.auto_link_hover_color
            else styles.link_hover_color
        )
        style = styles.link_hover_style + Style.from_color(
            hover_color.rich_color,
            hover_background.rich_color,
        )
        return style

    def _set_dirty(self, *regions: Region) -> None:
        """Set the Widget as 'dirty' (requiring re-paint).

        Regions should be specified as positional args. If no regions are added, then
        the entire widget will be considered dirty.

        Args:
            *regions: Regions which require a repaint.

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
            Regions to repaint.
        """
        regions = self._repaint_regions.copy()
        self._repaint_regions.clear()
        return regions

    def _scroll_to(
        self,
        x: float | None = None,
        y: float | None = None,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> bool:
        """Scroll to a given (absolute) coordinate, optionally animating.

        Args:
            x: X coordinate (column) to scroll to, or `None` for no change.
            y: Y coordinate (row) to scroll to, or `None` for no change.
            animate: Animate to new scroll position.
            speed: Speed of scroll if `animate` is `True`. Or `None` to use duration.
            duration: Duration of animation, if `animate` is `True` and speed is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.

        Returns:
            `True` if the scroll position changed, otherwise `False`.
        """

        maybe_scroll_x = x is not None and (self.allow_horizontal_scroll or force)
        maybe_scroll_y = y is not None and (self.allow_vertical_scroll or force)
        scrolled_x = scrolled_y = False
        if animate:
            # TODO: configure animation speed
            if duration is None and speed is None:
                speed = 50

            if easing is None:
                easing = DEFAULT_SCROLL_EASING

            if maybe_scroll_x:
                assert x is not None
                self.scroll_target_x = x
                if x != self.scroll_x:
                    self.animate(
                        "scroll_x",
                        self.scroll_target_x,
                        speed=speed,
                        duration=duration,
                        easing=easing,
                    )
                    scrolled_x = True
            if maybe_scroll_y:
                assert y is not None
                self.scroll_target_y = y
                if y != self.scroll_y:
                    self.animate(
                        "scroll_y",
                        self.scroll_target_y,
                        speed=speed,
                        duration=duration,
                        easing=easing,
                    )
                    scrolled_y = True

        else:
            if maybe_scroll_x:
                assert x is not None
                scroll_x = self.scroll_x
                self.scroll_target_x = self.scroll_x = x
                scrolled_x = scroll_x != self.scroll_x
            if maybe_scroll_y:
                assert y is not None
                scroll_y = self.scroll_y
                self.scroll_target_y = self.scroll_y = y
                scrolled_y = scroll_y != self.scroll_y

        return scrolled_x or scrolled_y

    def scroll_to(
        self,
        x: float | None = None,
        y: float | None = None,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> None:
        """Scroll to a given (absolute) coordinate, optionally animating.

        Args:
            x: X coordinate (column) to scroll to, or `None` for no change.
            y: Y coordinate (row) to scroll to, or `None` for no change.
            animate: Animate to new scroll position.
            speed: Speed of scroll if `animate` is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.

        Note:
            The call to scroll is made after the next refresh.
        """
        self.call_after_refresh(
            self._scroll_to,
            x,
            y,
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
        )

    def scroll_relative(
        self,
        x: float | None = None,
        y: float | None = None,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> None:
        """Scroll relative to current position.

        Args:
            x: X distance (columns) to scroll, or ``None`` for no change.
            y: Y distance (rows) to scroll, or ``None`` for no change.
            animate: Animate to new scroll position.
            speed: Speed of scroll if `animate` is `True`. Or `None` to use `duration`.
            duration: Duration of animation, if animate is `True` and speed is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.
        """
        self.scroll_to(
            None if x is None else (self.scroll_x + x),
            None if y is None else (self.scroll_y + y),
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
        )

    def scroll_home(
        self,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> None:
        """Scroll to home position.

        Args:
            animate: Animate scroll.
            speed: Speed of scroll if animate is `True`; or `None` to use duration.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.
        """
        if speed is None and duration is None:
            duration = 1.0
        self.scroll_to(
            0,
            0,
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
        )

    def scroll_end(
        self,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> None:
        """Scroll to the end of the container.

        Args:
            animate: Animate scroll.
            speed: Speed of scroll if `animate` is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.
        """
        if speed is None and duration is None:
            duration = 1.0

        # In most cases we'd call self.scroll_to and let it handle the call
        # to do things after a refresh, but here we need the refresh to
        # happen first so that we can get the new self.max_scroll_y (that
        # is, we need the layout to work out and then figure out how big
        # things are). Because of this we'll create a closure over the call
        # here and make our own call to call_after_refresh.
        def _lazily_scroll_end() -> None:
            """Scroll to the end of the widget."""
            self._scroll_to(
                0,
                self.max_scroll_y,
                animate=animate,
                speed=speed,
                duration=duration,
                easing=easing,
                force=force,
            )

        self.call_after_refresh(_lazily_scroll_end)

    def scroll_left(
        self,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> None:
        """Scroll one cell left.

        Args:
            animate: Animate scroll.
            speed: Speed of scroll if `animate` is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.
        """
        self.scroll_to(
            x=self.scroll_target_x - 1,
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
        )

    def _scroll_left_for_pointer(
        self,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> bool:
        """Scroll left one position, taking scroll sensitivity into account.

        Args:
            animate: Animate scroll.
            speed: Speed of scroll if `animate` is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.

        Returns:
            `True` if any scrolling was done.

        Note:
            How much is scrolled is controlled by
            [App.scroll_sensitivity_x][textual.app.App.scroll_sensitivity_x].
        """
        return self._scroll_to(
            x=self.scroll_target_x - self.app.scroll_sensitivity_x,
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
        )

    def scroll_right(
        self,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> None:
        """Scroll one cell right.

        Args:
            animate: Animate scroll.
            speed: Speed of scroll if animate is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.
        """
        self.scroll_to(
            x=self.scroll_target_x + 1,
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
        )

    def _scroll_right_for_pointer(
        self,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> bool:
        """Scroll right one position, taking scroll sensitivity into account.

        Args:
            animate: Animate scroll.
            speed: Speed of scroll if animate is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.

        Returns:
            `True` if any scrolling was done.

        Note:
            How much is scrolled is controlled by
            [App.scroll_sensitivity_x][textual.app.App.scroll_sensitivity_x].
        """
        return self._scroll_to(
            x=self.scroll_target_x + self.app.scroll_sensitivity_x,
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
        )

    def scroll_down(
        self,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> None:
        """Scroll one line down.

        Args:
            animate: Animate scroll.
            speed: Speed of scroll if `animate` is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.
        """
        self.scroll_to(
            y=self.scroll_target_y + 1,
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
        )

    def _scroll_down_for_pointer(
        self,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> bool:
        """Scroll down one position, taking scroll sensitivity into account.

        Args:
            animate: Animate scroll.
            speed: Speed of scroll if `animate` is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.

        Returns:
            `True` if any scrolling was done.

        Note:
            How much is scrolled is controlled by
            [App.scroll_sensitivity_y][textual.app.App.scroll_sensitivity_y].
        """
        return self._scroll_to(
            y=self.scroll_target_y + self.app.scroll_sensitivity_y,
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
        )

    def scroll_up(
        self,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> None:
        """Scroll one line up.

        Args:
            animate: Animate scroll.
            speed: Speed of scroll if `animate` is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and speed is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.
        """
        self.scroll_to(
            y=self.scroll_target_y - 1,
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
        )

    def _scroll_up_for_pointer(
        self,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> bool:
        """Scroll up one position, taking scroll sensitivity into account.

        Args:
            animate: Animate scroll.
            speed: Speed of scroll if `animate` is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and speed is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.

        Returns:
            `True` if any scrolling was done.

        Note:
            How much is scrolled is controlled by
            [App.scroll_sensitivity_y][textual.app.App.scroll_sensitivity_y].
        """
        return self._scroll_to(
            y=self.scroll_target_y - self.app.scroll_sensitivity_y,
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
        )

    def scroll_page_up(
        self,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> None:
        """Scroll one page up.

        Args:
            animate: Animate scroll.
            speed: Speed of scroll if animate is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.
        """
        self.scroll_to(
            y=self.scroll_y - self.container_size.height,
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
        )

    def scroll_page_down(
        self,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> None:
        """Scroll one page down.

        Args:
            animate: Animate scroll.
            speed: Speed of scroll if animate is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.
        """
        self.scroll_to(
            y=self.scroll_y + self.container_size.height,
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
        )

    def scroll_page_left(
        self,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> None:
        """Scroll one page left.

        Args:
            animate: Animate scroll.
            speed: Speed of scroll if animate is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.
        """
        if speed is None and duration is None:
            duration = 0.3
        self.scroll_to(
            x=self.scroll_x - self.container_size.width,
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
        )

    def scroll_page_right(
        self,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> None:
        """Scroll one page right.

        Args:
            animate: Animate scroll.
            speed: Speed of scroll if animate is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.
        """
        if speed is None and duration is None:
            duration = 0.3
        self.scroll_to(
            x=self.scroll_x + self.container_size.width,
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
        )

    def scroll_to_widget(
        self,
        widget: Widget,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        top: bool = False,
        force: bool = False,
    ) -> bool:
        """Scroll scrolling to bring a widget in to view.

        Args:
            widget: A descendant widget.
            animate: `True` to animate, or `False` to jump.
            speed: Speed of scroll if `animate` is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            top: Scroll widget to top of container.
            force: Force scrolling even when prohibited by overflow styling.

        Returns:
            `True` if any scrolling has occurred in any descendant, otherwise `False`.
        """

        # Grow the region by the margin so to keep the margin in view.
        region = widget.virtual_region_with_margin
        scrolled = False

        while isinstance(widget.parent, Widget) and widget is not self:
            container = widget.parent

            if widget.styles.dock:
                scroll_offset = Offset(0, 0)
            else:
                scroll_offset = container.scroll_to_region(
                    region,
                    spacing=widget.parent.gutter,
                    animate=animate,
                    speed=speed,
                    duration=duration,
                    top=top,
                    easing=easing,
                    force=force,
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
        self,
        region: Region,
        *,
        spacing: Spacing | None = None,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        top: bool = False,
        force: bool = False,
    ) -> Offset:
        """Scrolls a given region in to view, if required.

        This method will scroll the least distance required to move `region` fully within
        the scrollable area.

        Args:
            region: A region that should be visible.
            spacing: Optional spacing around the region.
            animate: `True` to animate, or `False` to jump.
            speed: Speed of scroll if `animate` is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            top: Scroll `region` to top of container.
            force: Force scrolling even when prohibited by overflow styling.

        Returns:
            The distance that was scrolled.
        """
        window = self.scrollable_content_region.at_offset(self.scroll_offset)
        if spacing is not None:
            window = window.shrink(spacing)

        if window in region and not top:
            return Offset()

        delta_x, delta_y = Region.get_scroll_to_visible(window, region, top=top)
        scroll_x, scroll_y = self.scroll_offset
        delta = Offset(
            clamp(scroll_x + delta_x, 0, self.max_scroll_x) - scroll_x,
            clamp(scroll_y + delta_y, 0, self.max_scroll_y) - scroll_y,
        )
        if delta:
            if speed is None and duration is None:
                duration = 0.2
            self.scroll_relative(
                delta.x or None,
                delta.y or None,
                animate=animate if (abs(delta_y) > 1 or delta_x) else False,
                speed=speed,
                duration=duration,
                easing=easing,
                force=force,
            )
        return delta

    def scroll_visible(
        self,
        animate: bool = True,
        *,
        speed: float | None = None,
        duration: float | None = None,
        top: bool = False,
        easing: EasingFunction | str | None = None,
        force: bool = False,
    ) -> None:
        """Scroll the container to make this widget visible.

        Args:
            animate: Animate scroll.
            speed: Speed of scroll if animate is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            top: Scroll to top of container.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.
        """
        parent = self.parent
        if isinstance(parent, Widget):
            self.call_after_refresh(
                self.screen.scroll_to_widget,
                self,
                animate=animate,
                speed=speed,
                duration=duration,
                top=top,
                easing=easing,
                force=force,
            )

    def __init_subclass__(
        cls,
        can_focus: bool | None = None,
        can_focus_children: bool | None = None,
        inherit_css: bool = True,
        inherit_bindings: bool = True,
    ) -> None:
        base = cls.__mro__[0]
        super().__init_subclass__(
            inherit_css=inherit_css,
            inherit_bindings=inherit_bindings,
        )
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
            region: A region for the widget.

        Returns:
            The widget region minus scrollbars.
        """
        show_vertical_scrollbar, show_horizontal_scrollbar = self.scrollbars_enabled

        styles = self.styles
        scrollbar_size_horizontal = styles.scrollbar_size_horizontal
        scrollbar_size_vertical = styles.scrollbar_size_vertical

        if styles.scrollbar_gutter == "stable":
            # Let's _always_ reserve some space, whether the scrollbar is actually displayed or not:
            show_vertical_scrollbar = True
            scrollbar_size_vertical = styles.scrollbar_size_vertical

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
            region: The containing region.

        Returns:
            Tuples of scrollbar Widget and region.

        """
        show_vertical_scrollbar, show_horizontal_scrollbar = self.scrollbars_enabled

        scrollbar_size_horizontal = self.scrollbar_size_horizontal
        scrollbar_size_vertical = self.scrollbar_size_vertical

        if show_horizontal_scrollbar and show_vertical_scrollbar:
            (
                window_region,
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
                scrollbar = self.vertical_scrollbar
                scrollbar.window_virtual_size = self.virtual_size.height
                scrollbar.window_size = window_region.height
                yield scrollbar, vertical_scrollbar_region
            if horizontal_scrollbar_region:
                scrollbar = self.horizontal_scrollbar
                scrollbar.window_virtual_size = self.virtual_size.width
                scrollbar.window_size = window_region.width
                yield scrollbar, horizontal_scrollbar_region

        elif show_vertical_scrollbar:
            window_region, scrollbar_region = region.split_vertical(
                -scrollbar_size_vertical
            )
            if scrollbar_region:
                scrollbar = self.vertical_scrollbar
                scrollbar.window_virtual_size = self.virtual_size.height
                scrollbar.window_size = window_region.height
                yield scrollbar, scrollbar_region
        elif show_horizontal_scrollbar:
            window_region, scrollbar_region = region.split_horizontal(
                -scrollbar_size_horizontal
            )
            if scrollbar_region:
                scrollbar = self.horizontal_scrollbar
                scrollbar.window_virtual_size = self.virtual_size.width
                scrollbar.window_size = window_region.width
                yield scrollbar, scrollbar_region

    def get_pseudo_classes(self) -> Iterable[str]:
        """Pseudo classes for a widget.

        Returns:
            Names of the pseudo classes.

        """
        node: MessagePump | None = self
        while isinstance(node, Widget):
            if node.disabled:
                yield "disabled"
                break
            node = node._parent
        else:
            yield "enabled"
        if self.mouse_over:
            yield "hover"
        if self.has_focus:
            yield "focus"
        try:
            focused = self.screen.focused
        except NoScreen:
            pass
        else:
            if focused:
                node = focused
                while node is not None:
                    if node is self:
                        yield "focus-within"
                        break
                    node = node._parent

    def get_pseudo_class_state(self) -> PseudoClasses:
        """Get an object describing whether each pseudo class is present on this object or not.

        Returns:
            A PseudoClasses object describing the pseudo classes that are present.
        """
        node: MessagePump | None = self
        disabled = False
        while isinstance(node, Widget):
            if node.disabled:
                disabled = True
                break
            node = node._parent

        pseudo_classes = PseudoClasses(
            enabled=not disabled,
            hover=self.mouse_over,
            focus=self.has_focus,
        )
        return pseudo_classes

    def post_render(self, renderable: RenderableType) -> ConsoleRenderable:
        """Applies style attributes to the default renderable.

        Returns:
            A new renderable.
        """
        text_justify: JustifyMethod | None = None
        if self.styles.has_rule("text_align"):
            text_align: JustifyMethod = cast(JustifyMethod, self.styles.text_align)
            text_justify = _JUSTIFY_MAP.get(text_align, text_align)

        if isinstance(renderable, str):
            renderable = Text.from_markup(renderable, justify=text_justify)

        if (
            isinstance(renderable, Text)
            and text_justify is not None
            and renderable.justify is None
        ):
            renderable.justify = text_justify

        renderable = _Styled(
            cast(ConsoleRenderable, renderable),
            self.rich_style,
            self.link_style if self.auto_links else None,
        )

        return renderable

    def watch_mouse_over(self, value: bool) -> None:
        """Update from CSS if mouse over state changes."""
        if self._has_hover_style:
            self._update_styles()

    def watch_has_focus(self, value: bool) -> None:
        """Update from CSS if has focus state changes."""
        self._update_styles()

    def watch_disabled(self) -> None:
        """Update the styles of the widget and its children when disabled is toggled."""
        self._update_styles()

    def _size_updated(
        self, size: Size, virtual_size: Size, container_size: Size, layout: bool = True
    ) -> bool:
        """Called when the widget's size is updated.

        Args:
            size: Screen size.
            virtual_size: Virtual (scrollable) size.
            container_size: Container size (size of parent).
            layout: Perform layout if required.

        Returns:
            True if anything changed, or False if nothing changed.
        """
        if (
            self._size != size
            or self.virtual_size != virtual_size
            or self._container_size != container_size
        ):
            self._size = size
            if layout:
                self.virtual_size = virtual_size
            else:
                self._reactive_virtual_size = virtual_size
            self._container_size = container_size
            if self.is_scrollable:
                self._scroll_update(virtual_size)
            return True
        else:
            return False

    def _scroll_update(self, virtual_size: Size) -> None:
        """Update scrollbars visibility and dimensions.

        Args:
            virtual_size: Virtual size.
        """
        self._refresh_scrollbars()
        width, height = self.container_size

        if self.show_vertical_scrollbar:
            self.vertical_scrollbar.window_virtual_size = virtual_size.height
            self.vertical_scrollbar.window_size = (
                height - self.scrollbar_size_horizontal
            )
            if self.vertical_scrollbar._repaint_required:
                self.call_later(self.vertical_scrollbar.refresh)
        if self.show_horizontal_scrollbar:
            self.horizontal_scrollbar.window_virtual_size = virtual_size.width
            self.horizontal_scrollbar.window_size = width - self.scrollbar_size_vertical
            if self.horizontal_scrollbar._repaint_required:
                self.call_later(self.horizontal_scrollbar.refresh)

        self.scroll_x = self.validate_scroll_x(self.scroll_x)
        self.scroll_y = self.validate_scroll_y(self.scroll_y)

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
        strips = [Strip(line, width) for line in lines]
        self._render_cache = RenderCache(self.size, strips)
        self._dirty_regions.clear()

    def render_line(self, y: int) -> Strip:
        """Render a line of content.

        Args:
            y: Y Coordinate of line.

        Returns:
            A rendered line.
        """
        if self._dirty_regions:
            self._render_content()
        try:
            line = self._render_cache.lines[y]
        except IndexError:
            line = Strip.blank(self.size.width, self.rich_style)
        return line

    def render_lines(self, crop: Region) -> list[Strip]:
        """Render the widget in to lines.

        Args:
            crop: Region within visible area to render.

        Returns:
            A list of list of segments.
        """
        strips = self._styles_cache.render_widget(self, crop)
        return strips

    def get_style_at(self, x: int, y: int) -> Style:
        """Get the Rich style in a widget at a given relative offset.

        Args:
            x: X coordinate relative to the widget.
            y: Y coordinate relative to the widget.

        Returns:
            A rich Style object.
        """
        offset = Offset(x, y)
        screen_offset = offset + self.region.offset

        widget, _ = self.screen.get_widget_at(*screen_offset)
        if widget is not self:
            return Style()
        return self.screen.get_style_at(*screen_offset)

    def _forward_event(self, event: events.Event) -> None:
        event._set_forwarded()
        self.post_message(event)

    def _refresh_scroll(self) -> None:
        """Refreshes the scroll position."""
        self._scroll_required = True
        self.check_idle()

    def refresh(
        self,
        *regions: Region,
        repaint: bool = True,
        layout: bool = False,
    ) -> Self:
        """Initiate a refresh of the widget.

        This method sets an internal flag to perform a refresh, which will be done on the
        next idle event. Only one refresh will be done even if this method is called multiple times.

        By default this method will cause the content of the widget to refresh, but not change its size. You can also
        set `layout=True` to perform a layout.

        !!! warning

            It is rarely necessary to call this method explicitly. Updating styles or reactive attributes will
            do this automatically.

        Args:
            *regions: Additional screen regions to mark as dirty.
            repaint: Repaint the widget (will call render() again).
            layout: Also layout widgets in the view.

        Returns:
            The `Widget` instance.
        """
        if layout and not self._layout_required:
            self._layout_required = True
            self._stabilize_scrollbar = None
            for ancestor in self.ancestors:
                if not isinstance(ancestor, Widget):
                    break
                ancestor._clear_arrangement_cache()

        if repaint:
            self._set_dirty(*regions)
            self._content_width_cache = (None, 0)
            self._content_height_cache = (None, 0)
            self._rich_style_cache.clear()
            self._repaint_required = True

        self.check_idle()
        return self

    def remove(self) -> AwaitRemove:
        """Remove the Widget from the DOM (effectively deleting it).

        Returns:
            An awaitable object that waits for the widget to be removed.
        """

        await_remove = self.app._remove_nodes([self], self.parent)
        return await_remove

    def render(self) -> RenderableType:
        """Get renderable for widget.

        Returns:
            Any renderable.
        """
        render: Text | str = "" if self.is_container else self.css_identifier_styled
        return render

    def _render(self) -> ConsoleRenderable | RichCast:
        """Get renderable, promoting str to text as required.

        Returns:
            A renderable.
        """
        renderable = self.render()
        if isinstance(renderable, str):
            return Text(renderable)
        return renderable

    async def run_action(self, action: str) -> None:
        """Perform a given action, with this widget as the default namespace.

        Args:
            action: Action encoded as a string.
        """
        await self.app.run_action(action, self)

    def post_message(self, message: Message) -> bool:
        """Post a message to this widget.

        Args:
            message: Message to post.

        Returns:
            True if the message was posted, False if this widget was closed / closing.
        """

        if constants.DEBUG and not self.is_running and not message.no_dispatch:
            try:
                self.log.warning(self, f"IS NOT RUNNING, {message!r} not sent")
            except NoActiveAppError:
                pass
        return super().post_message(message)

    async def _on_idle(self, event: events.Idle) -> None:
        """Called when there are no more events on the queue.

        Args:
            event: Idle event.
        """
        self._check_refresh()

    def _check_refresh(self) -> None:
        """Check if a refresh was requested."""
        if self._parent is not None and not self._closing:
            try:
                screen = self.screen
            except NoScreen:
                pass
            else:
                if self._scroll_required:
                    self._scroll_required = False
                    screen.post_message(messages.UpdateScroll())
                if self._repaint_required:
                    self._repaint_required = False
                    screen.post_message(messages.Update(self))
                if self._layout_required:
                    self._layout_required = False
                    screen.post_message(messages.Layout())

    def focus(self, scroll_visible: bool = True) -> Self:
        """Give focus to this widget.

        Args:
            scroll_visible: Scroll parent to make this widget visible.

        Returns:
            The `Widget` instance.
        """

        def set_focus(widget: Widget):
            """Callback to set the focus."""
            try:
                widget.screen.set_focus(self, scroll_visible=scroll_visible)
            except NoScreen:
                pass

        self.app.call_later(set_focus, self)
        return self

    def reset_focus(self) -> Self:
        """Reset the focus (move it to the next available widget).

        Returns:
            The `Widget` instance.
        """
        try:
            self.screen._reset_focus(self)
        except NoScreen:
            pass
        return self

    def capture_mouse(self, capture: bool = True) -> None:
        """Capture (or release) the mouse.

        When captured, mouse events will go to this widget even when the pointer is not directly over the widget.

        Args:
            capture: True to capture or False to release. Defaults to True.
        """
        self.app.capture_mouse(self if capture else None)

    def release_mouse(self) -> None:
        """Release the mouse.

        Mouse events will only be sent when the mouse is over the widget.
        """
        self.app.capture_mouse(None)

    def check_message_enabled(self, message: Message) -> bool:
        """Check if a given message is enabled (allowed to be sent).

        Args:
            message: A message object

        Returns:
            `True` if the message will be sent, or `False` if it is disabled.
        """
        # Do the normal checking and get out if that fails.
        if not super().check_message_enabled(message):
            return False
        message_type = type(message)
        if self._is_prevented(message_type):
            return False
        # Otherwise, if this is a mouse event, the widget receiving the
        # event must not be disabled at this moment.
        return (
            not self._self_or_ancestors_disabled
            if isinstance(message, (events.MouseEvent, events.Enter, events.Leave))
            else True
        )

    async def broker_event(self, event_name: str, event: events.Event) -> bool:
        return await self.app._broker_event(event_name, event, default_namespace=self)

    def notify_style_update(self) -> None:
        self._rich_style_cache.clear()

    async def _on_mouse_down(self, event: events.MouseDown) -> None:
        await self.broker_event("mouse.down", event)

    async def _on_mouse_up(self, event: events.MouseUp) -> None:
        await self.broker_event("mouse.up", event)

    async def _on_click(self, event: events.Click) -> None:
        await self.broker_event("click", event)

    async def _on_key(self, event: events.Key) -> None:
        await self.handle_key(event)

    async def handle_key(self, event: events.Key) -> bool:
        return await self.dispatch_key(event)

    async def _on_compose(self) -> None:
        try:
            widgets = compose(self)
        except TypeError as error:
            raise TypeError(
                f"{self!r} compose() method returned an invalid result; {error}"
            ) from error
        except Exception:
            self.app.panic(Traceback())
        else:
            await self.mount(*widgets)

    def _on_mount(self, event: events.Mount) -> None:
        if self.styles.overflow_y == "scroll":
            self.show_vertical_scrollbar = True
        if self.styles.overflow_x == "scroll":
            self.show_horizontal_scrollbar = True

    def _on_leave(self, event: events.Leave) -> None:
        self.mouse_over = False
        self.hover_style = Style()

    def _on_enter(self, event: events.Enter) -> None:
        self.mouse_over = True

    def _on_focus(self, event: events.Focus) -> None:
        self.has_focus = True
        self.refresh()
        self.post_message(events.DescendantFocus())

    def _on_blur(self, event: events.Blur) -> None:
        self.has_focus = False
        self.refresh()
        self.post_message(events.DescendantBlur())

    def _on_descendant_blur(self, event: events.DescendantBlur) -> None:
        if self._has_focus_within:
            self._update_styles()

    def _on_descendant_focus(self, event: events.DescendantBlur) -> None:
        if self._has_focus_within:
            self._update_styles()

    def _on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        if event.ctrl or event.shift:
            if self.allow_horizontal_scroll:
                if self._scroll_right_for_pointer(animate=False):
                    event.stop()
        else:
            if self.allow_vertical_scroll:
                if self._scroll_down_for_pointer(animate=False):
                    event.stop()

    def _on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        if event.ctrl or event.shift:
            if self.allow_horizontal_scroll:
                if self._scroll_left_for_pointer(animate=False):
                    event.stop()
        else:
            if self.allow_vertical_scroll:
                if self._scroll_up_for_pointer(animate=False):
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
            self.reset_focus()

    def _on_scroll_to_region(self, message: messages.ScrollToRegion) -> None:
        self.scroll_to_region(message.region, animate=True)

    def _on_unmount(self) -> None:
        self.workers.cancel_node(self)

    def action_scroll_home(self) -> None:
        if not self._allow_scroll:
            raise SkipAction()
        self.scroll_home()

    def action_scroll_end(self) -> None:
        if not self._allow_scroll:
            raise SkipAction()
        self.scroll_end()

    def action_scroll_left(self) -> None:
        if not self.allow_horizontal_scroll:
            raise SkipAction()
        self.scroll_left()

    def action_scroll_right(self) -> None:
        if not self.allow_horizontal_scroll:
            raise SkipAction()
        self.scroll_right()

    def action_scroll_up(self) -> None:
        if not self.allow_vertical_scroll:
            raise SkipAction()
        self.scroll_up()

    def action_scroll_down(self) -> None:
        if not self.allow_vertical_scroll:
            raise SkipAction()
        self.scroll_down()

    def action_page_down(self) -> None:
        if not self.allow_vertical_scroll:
            raise SkipAction()
        self.scroll_page_down()

    def action_page_up(self) -> None:
        if not self.allow_vertical_scroll:
            raise SkipAction()
        self.scroll_page_up()
