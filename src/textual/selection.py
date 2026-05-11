from __future__ import annotations

from operator import attrgetter
from typing import TYPE_CHECKING, Iterable, Iterator, NamedTuple

from textual.geometry import Offset, Shape

if TYPE_CHECKING:
    from textual.widget import Widget


class Selection(NamedTuple):
    """A selected range of lines."""

    start: Offset | None
    """Offset or None for `start`."""
    end: Offset | None
    """Offset or None for `end`."""

    @classmethod
    def from_offsets(cls, offset1: Offset, offset2: Offset) -> Selection:
        """Create selection from 2 offsets.

        Args:
            offset1: First offset.
            offset2: Second offset.

        Returns:
            New Selection.
        """
        offsets = sorted([offset1, offset2], key=(lambda offset: (offset.y, offset.x)))
        return cls(*offsets)

    def extract(self, text: str) -> str:
        """Extract selection from text.

        Args:
            text: Raw text pulled from widget.

        Returns:
            Extracted text.
        """
        lines = text.splitlines()
        if not lines:
            return ""
        if self.start is None:
            start_line_index = 0
            start_offset = 0
        else:
            start_line_index, start_offset = self.start.transpose

        if self.end is None:
            end_line = len(lines)
            end_offset = len(lines[-1])
        else:
            end_line, end_offset = self.end.transpose
        end_line = min(len(lines), end_line)

        if start_line_index == end_line:
            return lines[start_line_index][start_offset:end_offset]

        selection: list[str] = []
        selected_lines = lines[start_line_index : end_line + 1]
        if len(selected_lines) >= 2:
            first_line, *mid_lines, last_line = selected_lines
            selection.append(first_line[start_offset:])
            selection.extend(mid_lines)
            selection.append(last_line[:end_offset])
        else:
            try:
                selection.append(lines[start_line_index][start_offset:end_offset])
            except IndexError:
                pass
        return "\n".join(selection)

    def get_span(self, y: int) -> tuple[int, int] | None:
        """Get the selected span in a given line.

        Args:
            y: Offset of the line.

        Returns:
            A tuple of x start and end offset, or None for no selection.
        """
        start, end = self
        if start is None and end is None:
            # Selection covers everything
            return 0, -1

        if start is not None and end is not None:
            if y < start.y or y > end.y:
                # Outside
                return None
            if y == start.y and start.y == end.y:
                # Same line
                return start.x, end.x
            if y == end.y:
                # Last line
                return 0, end.x
            if y == start.y:
                return start.x, -1
            # Remaining lines
            return 0, -1

        if start is None and end is not None:
            if y == end.y:
                return 0, end.x
            if y > end.y:
                return None
            return 0, -1

        if end is None and start is not None:
            if y == start.y:
                return start.x, -1
            if y > start.y:
                return 0, -1
            return None
        return 0, -1


SELECT_ALL = Selection(None, None)


class SelectStart(NamedTuple):
    """Describes the start of a select."""

    container: Widget
    """The container under the cursor."""
    container_pointer_delta: Offset
    """The delta between the initial container offset and pointer."""
    container_initial_offset: Offset
    """The initial offset of the container."""
    container_initial_scroll_offset: Offset
    """The initial scroll offset of the container."""
    content_widget: Widget | None
    """The content widget under the pointer (if any)."""
    content_offset: Offset | None
    """The content offset of the widget under the pointer (if appropriate)."""

    @property
    def pointer_start_offset(self) -> Offset:
        """The pointer start offset adjusted for scroll."""
        return (
            self.container.region.offset
            + self.container_pointer_delta
            + (self.container.scroll_offset - self.container_initial_scroll_offset)
        )


class SelectEnd(NamedTuple):
    """The end of a select."""

    container: Widget
    """The container widget under the pointer."""
    content_widget: Widget | None
    """The content widget under the pointer (if any)."""
    content_offset: Offset | None
    """The content offset of the widget under the pointer."""


class SelectState(NamedTuple):
    """An object which describes the current select state."""

    screen_offset: Offset
    """The current mouse position, in screen space."""
    start: SelectStart
    """Describes the select start."""
    end: SelectEnd | None = None
    """Describes the select end."""

    def is_attached_to_dom(self) -> bool:
        """Are the widgets involved attached to the DOM?"""
        # This may return False if the widgets have been removed since selection started
        if not self.start.container.is_attached:
            return False
        if self.end is not None and not self.end.container.is_attached:
            return False
        return True

    @property
    def is_single_content_widget(self) -> bool:
        """Does the start and end fall on the same widget?"""
        assert self.end is not None
        return (
            self.start.content_widget is not None
            and self.start.content_widget is self.end.content_widget
            and self.start.content_offset is not None
            and self.end.content_offset is not None
        )

    @property
    def content_offsets(self) -> tuple[Offset, Offset]:
        """Get the content offset in select order."""
        assert (
            self.end is not None
        ), "Unavailable until there is an end point to the selection"
        start_offset = self.start.content_offset
        end_offset = self.end.content_offset
        assert start_offset is not None
        assert end_offset is not None
        if end_offset.transpose < start_offset.transpose:
            start_offset, end_offset = end_offset, start_offset
        return start_offset, end_offset

    @property
    def select_container(self) -> Widget:
        """A widget that contains both ends of the select."""
        from textual.screen import Screen
        from textual.widget import Widget

        widgets = [
            (
                self.start.content_widget
                if self.start.content_widget is not None
                else self.start.container
            )
        ]
        if self.end is not None:
            widgets.append(
                self.end.content_widget
                if self.end.content_widget is not None
                else self.end.container
            )

        if len(widgets) == 2:
            widget1, widget2 = widgets
            if isinstance(widget1, Screen):
                return widget1
            if isinstance(widget2, Screen):
                return widget2
            try:
                return Widget.get_common_ancestor(widget1, widget2)
            except ValueError:
                return widget1
        else:
            return widgets[0]

    @property
    def selection_bounds(self) -> Shape:
        """A shape which overlays the area of selected text."""

        selection_bounds = Shape.selection_bounds(
            self.select_container.region,
            self.start.pointer_start_offset,
            self.screen_offset,
        )
        return selection_bounds

    @property
    def ordered_offsets(self) -> tuple[Offset, Offset]:
        """Offsets used in selection bounds, in selection order."""
        start_offset = self.start.pointer_start_offset
        end_offset = self.screen_offset

        if start_offset.transpose > end_offset.transpose:
            start_offset, end_offset = end_offset, start_offset

        return start_offset, end_offset

    def update_end(self, pointer_offset: Offset, select_end: SelectEnd) -> SelectState:
        """Update the state with the selction end.

        Args:
            pointer_offset: Current mosue position.
            select_end: Selection end.
        """
        return SelectState(pointer_offset, self.start, select_end)

    def _apply_content_selections(self, selections: dict[Widget, Selection]):
        assert (
            self.end is not None
        ), "Unavailable until there is an end point to the selection"
        start_widget = self.start.content_widget
        start_content_offset = self.start.content_offset
        start_offset = self.start.pointer_start_offset

        end_widget = self.end.content_widget
        end_content_offset = self.end.content_offset
        end_offset = self.screen_offset

        if end_offset.transpose < start_offset.transpose:
            start_widget, end_widget = end_widget, start_widget
            start_content_offset, end_content_offset = (
                end_content_offset,
                start_content_offset,
            )

        if start_widget is not None and start_content_offset is not None:
            selections[start_widget] = Selection(start_content_offset, None)
        if end_widget is not None and end_content_offset is not None:
            selections[end_widget] = Selection(None, end_content_offset)

    def _walk_selected_widgets(self) -> list[Widget]:
        assert (
            self.end is not None
        ), "Unavailable until there is an end point to the selection"

        selection_bounds = self.selection_bounds
        select_container = self.select_container

        # Endpoints sorted by screen position.
        ordered_start, ordered_end = self.ordered_offsets
        start_y = ordered_start.y
        end_y = ordered_end.y

        # Identify the content widgets at each end of the selection, in
        # selection order. Either may be `None` if the pointer was not over a
        # content widget at that end.
        if self.start.pointer_start_offset.transpose <= self.screen_offset.transpose:
            first_content_widget = self.start.content_widget
            last_content_widget = self.end.content_widget
        else:
            first_content_widget = self.end.content_widget
            last_content_widget = self.start.content_widget

        get_selection_order = attrgetter("_selection_order")
        selected: list[Widget] = []

        def walk_in_select_order(root: Widget) -> Iterable[Widget]:
            """Walk descendants of `root` depth-first in selection order."""
            stack: list[Iterator[Widget]] = [
                iter(
                    sorted(
                        root.displayed_and_visible_children,
                        key=get_selection_order,
                    )
                )
            ]
            while stack:
                widget = next(stack[-1], None)
                if widget is None:
                    stack.pop()
                    continue
                yield widget
                children = widget.displayed_and_visible_children
                if children:
                    stack.append(iter(sorted(children, key=get_selection_order)))

        def collect_range(
            container: Widget,
            from_widget: Widget | None,
            to_widget: Widget | None,
            *,
            from_y: int | None = None,
            to_y: int | None = None,
        ) -> None:
            """Collect selectable descendants between two content widgets.

            Walks `container` in selection order, including selectable
            non-container descendants. `from_widget=None` means start at the
            first descendant; `to_widget=None` means continue to the last.

            When the start or end pointer lands on a gap (no content widget),
            `from_y` / `to_y` fall back to a vertical bound on the widget's
            `content_region.y` so the selection grows continuously as the
            pointer moves, rather than snapping to the whole container.
            """
            started = from_widget is None and from_y is None
            for descendant in walk_in_select_order(container):
                if descendant.is_container or not descendant.allow_select:
                    continue
                widget_y = descendant.content_region.y
                if not started:
                    if from_widget is not None:
                        if descendant is from_widget:
                            started = True
                        else:
                            continue
                    else:
                        # from_y bound is active.
                        assert from_y is not None
                        if widget_y >= from_y:
                            started = True
                        else:
                            continue
                if to_widget is None and to_y is not None and widget_y > to_y:
                    return
                selected.append(descendant)
                if to_widget is not None and descendant is to_widget:
                    return

        def visit(parent: Widget) -> None:
            """Walk children of `parent`, deciding inclusion per child."""
            for child in sorted(
                parent.displayed_and_visible_children,
                key=get_selection_order,
            ):
                if child.is_container:
                    child_region = child.region
                    if not child_region:
                        continue
                    if not selection_bounds.overlaps(child_region):
                        continue

                    has_hidden_content = child.is_scrollable and (
                        child.max_scroll_y > 0 or child.max_scroll_x > 0
                    )

                    if has_hidden_content:
                        child_top = child_region.y
                        child_bottom = child_region.bottom
                        extends_above = start_y < child_top
                        extends_below = end_y >= child_bottom

                        if extends_above and extends_below:
                            # Selection passes through this container; select
                            # everything inside it.
                            collect_range(child, None, None)
                            continue
                        if extends_above:
                            # Selection enters this container from above;
                            # select from top down to the end content widget,
                            # or to the pointer y if the pointer is on a gap.
                            if last_content_widget is not None:
                                collect_range(child, None, last_content_widget)
                            else:
                                collect_range(child, None, None, to_y=end_y)
                            continue
                        if extends_below:
                            # Selection exits this container below; select
                            # from the start content widget (or the pointer y
                            # if on a gap) down to the end.
                            if first_content_widget is not None:
                                collect_range(child, first_content_widget, None)
                            else:
                                collect_range(child, None, None, from_y=start_y)
                            continue

                    # Both endpoints inside this child, or nothing scrolled
                    # out; fall back to the standard visual walk.
                    visit(child)
                else:
                    if child.allow_select and selection_bounds.overlaps(
                        child.content_region
                    ):
                        selected.append(child)

        visit(select_container)
        return selected
