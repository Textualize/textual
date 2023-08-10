from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from rich.segment import Segment
from rich.style import Style
from rich.text import Text

if TYPE_CHECKING:
    from tree_sitter import Language

from textual import events, log
from textual._cells import cell_len
from textual._fix_direction import _fix_direction
from textual._syntax_theme import DEFAULT_SYNTAX_THEME, SyntaxTheme
from textual._types import Literal, Protocol, runtime_checkable
from textual.binding import Binding
from textual.document._document import Document, Location, Selection
from textual.events import MouseEvent
from textual.geometry import Offset, Region, Size, Spacing, clamp
from textual.reactive import Reactive, reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip


@runtime_checkable
class Edit(Protocol):
    """Protocol for actions performed in the text editor which can be done and undone.

    These are typically actions which affect the document (e.g. inserting and deleting
    text), but they can really be anything.

    To perform an edit operation, pass the Edit to `TextArea.edit()`"""

    def do(self, text_area: TextArea) -> object | None:
        """Do the action."""

    def undo(self, text_area: TextArea) -> object | None:
        """Undo the action."""

    def post_edit(self, text_area: TextArea) -> None:
        """Code to execute after content size recalculated and repainted."""


@dataclass
class Insert:
    """Implements the Edit protocol for inserting text at some location."""

    text: str
    """The text to insert."""
    from_location: Location
    """The start location of the insert."""
    to_location: Location
    """The end location of the insert"""
    cursor_destination: Location | None = None
    """The location to move the cursor to after the operation completes."""
    _edit_end: Location | None = field(init=False, default=None)
    """Computed location to move the cursor to if `cursor_destination` is None."""

    def do(self, text_area: TextArea) -> None:
        """Perform the Insert operation.

        Args:
            text_area: The TextArea to perform the insert on.
        """
        self._edit_end = text_area._document.insert_range(
            self.from_location,
            self.to_location,
            self.text,
        )

    def undo(self, text_area: TextArea) -> None:
        """Undo the Insert operation.

        Args:
            text_area: The TextArea to undo the insert operation on.
        """

    def post_edit(self, text_area: TextArea) -> None:
        """Update the cursor location after the widget has been refreshed.

        Args:
            text_area: The TextArea this operation was performed on.
        """
        cursor_destination = self.cursor_destination
        if cursor_destination is not None:
            text_area.selection = cursor_destination
        else:
            text_area.selection = Selection.cursor(self._edit_end)

        text_area.record_cursor_offset()


@dataclass
class Delete:
    """Performs a delete operation."""

    from_location: Location
    """The location to delete from (inclusive)."""

    to_location: Location
    """The location to delete to (exclusive)."""

    cursor_destination: Location | None = None
    """Where to move the cursor to after the deletion."""

    _deleted_text: str | None = field(init=False, default=None)
    """The text that was deleted, or None if the deletion hasn't occurred yet."""

    def do(self, text_area: TextArea) -> str:
        """Do the delete action and record the text that was deleted."""
        self._deleted_text = text_area._document.delete_range(
            self.from_location, self.to_location
        )
        return self._deleted_text

    def undo(self, text_area: TextArea) -> None:
        """Undo the delete action."""

    def post_edit(self, text_area: TextArea) -> None:
        cursor_destination = self.cursor_destination
        if cursor_destination is not None:
            text_area.selection = Selection.cursor(cursor_destination)
        else:
            text_area.selection = Selection.cursor(self.from_location)

        text_area.record_cursor_offset()


class TextArea(ScrollView, can_focus=True):
    DEFAULT_CSS = """\
$text-area-active-line-bg: white 8%;
TextArea {
    background: $panel;
    width: 1fr;
    height: 1fr;
}
TextArea > .text-area--active-line {
    background: $text-area-active-line-bg;
}
TextArea > .text-area--active-line-gutter {
    color: $text;
    background: $text-area-active-line-bg;
}
TextArea > .text-area--gutter {
    color: $text-muted 40%;
}
TextArea > .text-area--cursor {
    color: $text;
    background: white 80%;
}
TextArea > .text-area--selection {
    background: $primary;
}
TextArea > .text-area--width-guide {
    background: white 4%;
}
"""

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "text-area--active-line",
        "text-area--active-line-gutter",
        "text-area--gutter",
        "text-area--cursor",
        "text-area--selection",
        "text-area--width-guide",
    }

    BINDINGS = [
        # Cursor movement
        Binding("up", "cursor_up", "cursor up", show=False),
        Binding("down", "cursor_down", "cursor down", show=False),
        Binding("left", "cursor_left", "cursor left", show=False),
        Binding("ctrl+left", "cursor_left_word", "cursor left word", show=False),
        Binding("right", "cursor_right", "cursor right", show=False),
        Binding("ctrl+right", "cursor_right_word", "cursor right word", show=False),
        Binding("home,ctrl+a", "cursor_line_start", "cursor line start", show=False),
        Binding("end,ctrl+e", "cursor_line_end", "cursor line end", show=False),
        Binding("pageup", "cursor_page_up", "cursor page up", show=False),
        Binding("pagedown", "cursor_page_down", "cursor page down", show=False),
        # Selection with the cursor
        Binding("shift+up", "cursor_up_select", "cursor up select", show=False),
        Binding("shift+down", "cursor_down_select", "cursor down select", show=False),
        Binding("shift+left", "cursor_left_select", "cursor left select", show=False),
        Binding(
            "shift+right", "cursor_right_select", "cursor right select", show=False
        ),
        # Deletion
        Binding("backspace", "delete_left", "delete left", show=False),
        Binding(
            "ctrl+w", "delete_word_left", "delete left to start of word", show=False
        ),
        Binding("delete,ctrl+d", "delete_right", "delete right", show=False),
        Binding(
            "ctrl+f", "delete_word_right", "delete right to start of word", show=False
        ),
        Binding("ctrl+x", "delete_line", "delete line", show=False),
        Binding(
            "ctrl+u", "delete_to_start_of_line", "delete to line start", show=False
        ),
        Binding("ctrl+k", "delete_to_end_of_line", "delete to line end", show=False),
    ]

    language: Reactive[str | "Language" | None] = reactive(None, always_update=True)
    """The language to use.

    This must be set to a valid, non-None value for syntax highlighting to work.

    If the value is a string, a built-in parser will be used.

    If a tree-sitter `Language` object is used,
    """

    theme: Reactive[str | SyntaxTheme] = reactive(DEFAULT_SYNTAX_THEME)
    """The theme to syntax highlight with.

    Supply a `SyntaxTheme` object to customise highlighting, or supply a builtin
    theme name as a string.

    Syntax highlighting is only possible when the `language` attribute is set.
    """

    selection: Reactive[Selection] = reactive(Selection(), always_update=True)
    """The selection start and end locations (zero-based line_index, offset)."""

    show_line_numbers: Reactive[bool] = reactive(True)
    """True to show the line number column, otherwise False."""

    indent_width: Reactive[int] = reactive(4)
    """The width of tabs or the number of spaces to insert on pressing the `tab` key."""

    show_width_guide: Reactive[bool] = reactive(False)
    """If True, a vertical line will indicate the width of the document."""

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        self._document = Document("")
        """The document this widget is currently editing."""

        self.indent_type: Literal["tabs", "spaces"] = "spaces"
        """Whether to indent using tabs or spaces."""

        self.word_pattern = re.compile(r"(?<=\W)(?=\w)|(?<=\w)(?=\W)")
        """Compiled regular expression for what we consider to be a 'word'."""

        self._last_intentional_cell_width: int = 0
        """Tracks the last column (measured in terms of cell length, since we care here about where the cursor
        visually moves rather than logical characters) the user explicitly navigated to so that we can reset to it
        whenever possible."""

        self._undo_stack: list[Edit] = []
        """A stack (the end of the list is the top of the stack) for tracking edits."""

        self._selecting = False
        """True if we're currently selecting text using the mouse, otherwise False."""

    def _watch_selection(self) -> None:
        self.scroll_cursor_visible()

    def _validate_selection(self, selection: Selection) -> Selection:
        start, end = selection
        clamp_visitable = self.clamp_visitable
        return Selection(clamp_visitable(start), clamp_visitable(end))

    def _watch_language(self) -> None:
        """When the language is updated, update the type of document."""
        self._reload_document()

    def _watch_theme(self) -> None:
        """When the theme is updated, update the document."""
        self._reload_document()

    def _watch_show_line_numbers(self) -> None:
        """The line number gutter contributes to virtual size, so recalculate."""
        self._refresh_size()

    def _watch_indent_width(self) -> None:
        """Changing width of tabs will change document display width."""
        self._refresh_size()

    def _reload_document(self) -> None:
        """Recreate the document based on the language and theme currently set."""
        language = self.language
        text = self._document.text
        if not language:
            # If there's no language set, we don't need to use a SyntaxAwareDocument.
            self._document = Document(text)
        else:
            try:
                from textual.document._syntax_aware_document import SyntaxAwareDocument

                self._document = SyntaxAwareDocument(text, language, self.theme)
            except ImportError:
                # SyntaxAwareDocument isn't available on Python 3.7.
                # Fall back to the standard document.
                log.warning("Syntax highlighting isn't available on Python 3.7.")
                self._document = Document(text)

    def load_text(self, text: str) -> None:
        """Load text from a string into the editor.

        Args:
            text: The text to load into the editor.
        """
        self._document = Document(text)
        self._reload_document()
        self._refresh_size()

    def _refresh_size(self) -> None:
        """Calculate the size of the document."""
        width, height = self._document.get_size(self.indent_width)
        # TODO - this is a prime candidate for optimisation.
        # +1 width to make space for the cursor resting at the end of the line
        self.virtual_size = Size(width + self.gutter_width + 1, height)

    def render_line(self, widget_y: int) -> Strip:
        document = self._document

        scroll_x, scroll_y = self.scroll_offset

        line_index = widget_y + scroll_y
        out_of_bounds = line_index >= document.line_count
        if out_of_bounds:
            return Strip.blank(self.size.width)

        line = document.get_line_text(line_index)
        line_character_count = len(line)
        line.tab_size = self.indent_width
        line.set_length(self.virtual_size.width)

        selection = self.selection
        start, end = selection
        selection_top, selection_bottom = selection.range
        selection_top_row, selection_top_column = selection_top
        selection_bottom_row, selection_bottom_column = selection_bottom

        # Selection styling
        if start != end and selection_top_row <= line_index <= selection_bottom_row:
            # If this row intersects with the selection range
            selection_style = self.get_component_rich_style("text-area--selection")
            if line_character_count == 0 and line_index != end:
                # A simple highlight to show empty lines are included in the selection
                line = Text("▌", end="", style=Style(color=selection_style.bgcolor))
            else:
                if line_index == selection_top_row == selection_bottom_row:
                    # Selection within a single line
                    line.stylize_before(
                        selection_style,
                        start=selection_top_column,
                        end=selection_bottom_column,
                    )
                else:
                    # Selection spanning multiple lines
                    if line_index == selection_top_row:
                        line.stylize_before(
                            selection_style,
                            start=selection_top_column,
                            end=line_character_count,
                        )
                    elif line_index == selection_bottom_row:
                        line.stylize_before(
                            selection_style, end=selection_bottom_column
                        )
                    else:
                        line.stylize_before(selection_style, end=line_character_count)

        virtual_width, virtual_height = self.virtual_size

        # Highlight the cursor
        cursor_row, cursor_column = end
        active_line_style = self.get_component_rich_style("text-area--active-line")
        if cursor_row == line_index:
            cursor_style = self.get_component_rich_style("text-area--cursor")
            line.stylize(cursor_style, cursor_column, cursor_column + 1)
            line.stylize_before(active_line_style)

        if self.show_width_guide:
            width_guide_style = self.get_component_rich_style("text-area--width-guide")
            width_column = virtual_width - self.gutter_width
            line.stylize_before(width_guide_style, width_column - 1, width_column)

        # Build the gutter text for this line
        if self.show_line_numbers:
            if cursor_row == line_index:
                gutter_style = self.get_component_rich_style(
                    "text-area--active-line-gutter"
                )
            else:
                gutter_style = self.get_component_rich_style("text-area--gutter")

            gutter_width_no_margin = self.gutter_width - 2
            gutter = Text(
                f"{line_index + 1:>{gutter_width_no_margin}}  ",
                style=gutter_style,
                end="",
            )
        else:
            gutter = Text("", end="")

        # Render the gutter and the text of this line
        gutter_segments = self.app.console.render(gutter)
        text_segments = self.app.console.render(
            line,
            self.app.console.options.update_width(virtual_width),
        )

        # Crop the line to show only the visible part (some may be scrolled out of view)
        gutter_strip = Strip(gutter_segments)
        text_strip = Strip(text_segments).crop(
            scroll_x, scroll_x + virtual_width - self.gutter_width
        )

        # Stylize the line the cursor is currently on.
        if cursor_row == line_index:
            expanded_length = max(virtual_width, self.size.width)
            text_strip = text_strip.extend_cell_length(
                expanded_length, active_line_style
            )

        # Join and return the gutter and the visible portion of this line
        strip = Strip.join([gutter_strip, text_strip]).simplify()
        return strip.apply_style(self.rich_style)

    @property
    def text(self) -> str:
        """The entire text content of the document."""
        return self._document.text

    @property
    def selected_text(self) -> str:
        """The text between the start and end points of the current selection."""
        start, end = self.selection
        return self.get_text_range(start, end)

    def get_text_range(self, start: Location, end: Location) -> str:
        """Get the text between a start and end location.

        Args:
            start: The start location.
            end: The end location.

        Returns:
            The text between start and end.
        """
        start, end = _fix_direction(start, end)
        return self._document.get_text_range(start, end)

    @property
    def gutter_width(self) -> int:
        """The width of the gutter (the left column containing line numbers).

        Returns:
            The cell-width of the line number column. If `show_line_numbers` is `False` returns 0.
        """
        # The longest number in the gutter plus two extra characters: `│ `.
        gutter_margin = 2
        gutter_width = (
            len(str(self._document.line_count + 1)) + gutter_margin
            if self.show_line_numbers
            else 0
        )
        return gutter_width

    def edit(self, edit: Edit) -> Any:
        """Perform an Edit.

        Args:
            edit: The Edit to perform.

        Returns:
            Data relating to the edit that may be useful. The data returned
            may be different depending on the edit performed.
        """
        result = edit.do(self)

        # TODO: Think about this...
        # self._undo_stack.append(edit)
        # self._undo_stack = self._undo_stack[-20:]

        self._refresh_size()
        edit.post_edit(self)

        return result

    # def undo(self) -> None:
    #     if self._undo_stack:
    #         action = self._undo_stack.pop()
    #         action.undo(self)

    # --- Lower level event/key handling
    async def _on_key(self, event: events.Key) -> None:
        """Handle key presses which correspond to document inserts."""
        key = event.key
        insert_values = {
            "tab": " " * self.indent_width if self.indent_type == "spaces" else "\t",
            "enter": "\n",
        }

        if event.is_printable or key in insert_values:
            event.stop()
            event.prevent_default()
            insert = insert_values.get(key, event.character)
            assert event.character is not None
            start, end = self.selection
            self.insert_text_range(insert, start, end)

    def get_target_document_location(self, event: MouseEvent) -> Location:
        """Given a MouseEvent, return the row and column offset of the event in document-space.

        Args:
            event: The MouseEvent.

        Returns:
            The location of the mouse event within the document.
        """
        scroll_x, scroll_y = self.scroll_offset
        target_x = event.x - self.gutter_width + scroll_x - self.gutter.left
        target_x = max(target_x, 0)
        target_row = clamp(
            event.y + scroll_y - self.gutter.top,
            0,
            self._document.line_count - 1,
        )
        target_column = self.cell_width_to_column_index(target_x, target_row)
        return target_row, target_column

    def _on_mouse_down(self, event: events.MouseDown) -> None:
        """Update the cursor position, and begin a selection using the mouse."""
        target = self.get_target_document_location(event)
        self.selection = Selection.cursor(target)
        self._selecting = True
        # Capture the mouse so that if the cursor moves outside the
        # TextArea widget while selecting, the widget still scrolls.
        self.capture_mouse()

    def _on_mouse_move(self, event: events.MouseMove) -> None:
        """Handles click and drag to expand and contract the selection."""
        if self._selecting:
            target = self.get_target_document_location(event)
            selection_start, _ = self.selection
            self.selection = Selection(selection_start, target)

    def _on_mouse_up(self, event: events.MouseUp) -> None:
        """Finalise the selection that has been made using the mouse."""
        self._selecting = False
        self.release_mouse()
        self.record_cursor_offset()

    def _on_paste(self, event: events.Paste) -> None:
        """When a paste occurs, insert the text from the paste event into the document."""
        text = event.text
        if text:
            self.insert_text_range(text, *self.selection)

    def cell_width_to_column_index(self, cell_width: int, row_index: int) -> int:
        """Return the column that the cell width corresponds to on the given row.

        Args:
            cell_width: The cell width to convert.
            row_index: The index of the row to examine.

        Returns:
            The column corresponding to the cell width on that row.
        """
        tab_width = self.indent_width
        total_cell_offset = 0
        line = self._document[row_index]
        for column_index, character in enumerate(line):
            total_cell_offset += cell_len(character.expandtabs(tab_width))
            if total_cell_offset >= cell_width + 1:
                return column_index
        return len(line)

    # --- Cursor/selection utilities
    def clamp_visitable(self, location: Location) -> Location:
        document = self._document

        row, column = location
        try:
            line_text = document[row]
        except IndexError:
            line_text = ""

        row = clamp(row, 0, document.line_count - 1)
        column = clamp(column, 0, len(line_text))

        return row, column

    def scroll_cursor_visible(self) -> Offset:
        """Scroll the `TextArea` such that the cursor is visible on screen.

        Returns:
            The offset that was scrolled to bring the cursor into view.
        """
        row, column = self.selection.end
        text = self.cursor_line_text[:column]
        column_offset = cell_len(text.expandtabs(self.indent_width))
        scroll_offset = self.scroll_to_region(
            Region(x=column_offset, y=row, width=2, height=1),
            spacing=Spacing(right=self.gutter_width),
            animate=False,
            force=True,
        )
        return scroll_offset

    @property
    def cursor_location(self) -> Location:
        """The current location of the cursor in the document."""
        return self.selection.end

    @cursor_location.setter
    def cursor_location(self, new_location: Location) -> Location:
        """Set the cursor_location to a new location.

        If a selection is in progress, the anchor point will remain.
        """
        start, end = self.selection
        self.selection = Selection(start, new_location)
        return self.selection.end

    @property
    def cursor_at_first_row(self) -> bool:
        return self.selection.end[0] == 0

    @property
    def cursor_at_last_row(self) -> bool:
        return self.selection.end[0] == self._document.line_count - 1

    @property
    def cursor_at_start_of_row(self) -> bool:
        return self.selection.end[1] == 0

    @property
    def cursor_at_end_of_row(self) -> bool:
        cursor_row, cursor_column = self.selection.end
        row_length = len(self._document[cursor_row])
        cursor_at_end = cursor_column == row_length
        return cursor_at_end

    @property
    def cursor_at_start_of_document(self) -> bool:
        return self.cursor_at_first_row and self.cursor_at_start_of_row

    @property
    def cursor_at_end_of_document(self) -> bool:
        """True if the cursor is at the very end of the document."""
        return self.cursor_at_last_row and self.cursor_at_end_of_row

    def cursor_to_line_end(self, select: bool = False) -> None:
        """Move the cursor to the end of the line.

        Args:
            select: Select the text between the old and new cursor locations.
        """

        start, end = self.selection
        cursor_row, cursor_column = end
        target_column = len(self._document[cursor_row])

        if select:
            self.selection = Selection(start, target_column)
        else:
            self.selection = Selection.cursor((cursor_row, target_column))

        self.record_cursor_offset()

    def cursor_to_line_start(self, select: bool = False) -> None:
        """Move the cursor to the start of the line.

        Args:
            select: Select the text between the old and new cursor locations.
        """
        start, end = self.selection
        cursor_row, cursor_column = end
        if select:
            self.selection = Selection(start, (cursor_row, 0))
        else:
            self.selection = Selection.cursor((cursor_row, 0))

        self.record_cursor_offset()

    # ------ Cursor movement actions
    def action_cursor_left(self) -> None:
        """Move the cursor one location to the left.

        If the cursor is at the left edge of the document, try to move it to
        the end of the previous line.
        """
        target = self.get_cursor_left_location()
        self.selection = Selection.cursor(target)
        self.record_cursor_offset()

    def action_cursor_left_select(self):
        """Move the end of the selection one location to the left.

        This will expand or contract the selection.
        """
        new_cursor_location = self.get_cursor_left_location()
        selection_start, selection_end = self.selection
        self.selection = Selection(selection_start, new_cursor_location)
        self.record_cursor_offset()

    def get_cursor_left_location(self) -> Location:
        """Get the location the cursor will move to if it moves left."""
        if self.cursor_at_start_of_document:
            return 0, 0
        cursor_row, cursor_column = self.selection.end
        length_of_row_above = len(self._document[cursor_row - 1])
        target_row = cursor_row if cursor_column != 0 else cursor_row - 1
        target_column = cursor_column - 1 if cursor_column != 0 else length_of_row_above
        return target_row, target_column

    def action_cursor_right(self) -> None:
        """Move the cursor one location to the right.

        If the cursor is at the end of a line, attempt to go to the start of the next line.
        """
        target = self.get_cursor_right_location()
        self.selection = Selection.cursor(target)
        self.record_cursor_offset()

    def action_cursor_right_select(self):
        """Move the end of the selection one location to the right.

        This will expand or contract the selection.
        """
        new_cursor_location = self.get_cursor_right_location()
        selection_start, selection_end = self.selection
        self.selection = Selection(selection_start, new_cursor_location)
        self.record_cursor_offset()

    def get_cursor_right_location(self) -> Location:
        """Get the location the cursor will move to if it moves right."""
        if self.cursor_at_end_of_document:
            return self.selection.end
        cursor_row, cursor_column = self.selection.end
        target_row = cursor_row + 1 if self.cursor_at_end_of_row else cursor_row
        target_column = 0 if self.cursor_at_end_of_row else cursor_column + 1
        return target_row, target_column

    def action_cursor_down(self) -> None:
        """Move the cursor down one cell."""
        target = self.get_cursor_down_location()
        self.selection = Selection.cursor(target)

    def action_cursor_down_select(self) -> None:
        """Move the cursor down one cell, selecting the range between the old and new locations."""
        target = self.get_cursor_down_location()
        start, end = self.selection
        self.selection = Selection(start, target)

    def get_cursor_down_location(self):
        """Get the location the cursor will move to if it moves down."""
        cursor_row, cursor_column = self.selection.end
        if self.cursor_at_last_row:
            return cursor_row, len(self._document[cursor_row])

        target_row = min(self._document.line_count - 1, cursor_row + 1)
        # Attempt to snap last intentional cell length
        target_column = self.cell_width_to_column_index(
            self._last_intentional_cell_width, target_row
        )
        target_column = clamp(target_column, 0, len(self._document[target_row]))
        return target_row, target_column

    def action_cursor_up(self) -> None:
        """Move the cursor up one cell."""
        target = self.get_cursor_up_location()
        self.selection = Selection.cursor(target)

    def action_cursor_up_select(self) -> None:
        """Move the cursor up one cell, selecting the range between the old and new locations."""
        target = self.get_cursor_up_location()
        start, end = self.selection
        self.selection = Selection(start, target)

    def get_cursor_up_location(self) -> Location:
        """Get the location the cursor will move to if it moves up."""
        if self.cursor_at_first_row:
            return 0, 0
        cursor_row, cursor_column = self.selection.end
        target_row = max(0, cursor_row - 1)
        # Attempt to snap last intentional cell length
        target_column = self.cell_width_to_column_index(
            self._last_intentional_cell_width, target_row
        )
        target_column = clamp(target_column, 0, len(self._document[target_row]))
        return target_row, target_column

    def action_cursor_line_end(self) -> None:
        """Move the cursor to the end of the line."""
        self.cursor_to_line_end()

    def action_cursor_line_start(self) -> None:
        """Move the cursor to the start of the line."""
        self.cursor_to_line_start()

    def action_cursor_left_word(self) -> None:
        """Move the cursor left by a single word, skipping spaces."""

        if self.cursor_at_start_of_document:
            return

        cursor_row, cursor_column = self.selection.end

        # Check the current line for a word boundary
        line = self._document[cursor_row][:cursor_column]
        matches = list(re.finditer(self.word_pattern, line))

        if matches:
            # If a word boundary is found, move the cursor there
            cursor_column = matches[-1].start()
        elif cursor_row > 0:
            # If no word boundary is found, and we're not on the first line, move to the end of the previous line
            cursor_row -= 1
            cursor_column = len(self._document[cursor_row])
        else:
            # If we're already on the first line and no word boundary is found, move to the start of the line
            cursor_column = 0

        self.selection = Selection.cursor((cursor_row, cursor_column))
        self.record_cursor_offset()

    def action_cursor_right_word(self) -> None:
        """Move the cursor right by a single word, skipping spaces."""

        if self.cursor_at_end_of_document:
            return

        cursor_row, cursor_column = self.selection.end

        # Check the current line for a word boundary
        line = self._document[cursor_row][cursor_column:]
        matches = list(re.finditer(self.word_pattern, line))

        if matches:
            # If a word boundary is found, move the cursor there
            cursor_column += matches[0].end()
        elif cursor_row < self._document.line_count - 1:
            # If no word boundary is found and we're not on the last line, move to the start of the next line
            cursor_row += 1
            cursor_column = 0
        else:
            # If we're already on the last line and no word boundary is found, move to the end of the line
            cursor_column = len(self._document[cursor_row])

        self.selection = Selection.cursor((cursor_row, cursor_column))
        self.record_cursor_offset()

    def action_cursor_page_up(self) -> None:
        height = self.content_size.height
        _, cursor_location = self.selection
        row, column = cursor_location
        target = (row - height, column)
        self.scroll_y -= height
        self.selection = Selection.cursor(target)

    def action_cursor_page_down(self) -> None:
        height = self.content_size.height
        _, cursor_location = self.selection
        row, column = cursor_location
        target = (row + height, column)
        self.scroll_y += height
        self.selection = Selection.cursor(target)

    @property
    def cursor_line_text(self) -> str:
        return self._document[self.selection.end[0]]

    def get_column_cell_width(self, row: int, column: int) -> int:
        """Given a row and column index within the editor, return the cell offset
        of the column from the start of the row (the left edge of the editor content area).
        """
        line = self._document[row]
        return cell_len(line[:column].expandtabs(self.indent_width))

    def record_cursor_offset(self) -> None:
        row, column = self.selection.end
        column_cell_length = self.get_column_cell_width(row, column)
        self._last_intentional_cell_width = column_cell_length

    # --- Editor operations
    def insert_text(
        self,
        text: str,
        location: Location | None = None,
        cursor_destination: Location | None = None,
    ) -> None:
        if location is None:
            location = self.selection.end
        self.edit(Insert(text, location, location, cursor_destination))

    def insert_text_range(
        self,
        text: str,
        from_location: Location,
        to_location: Location,
        cursor_destination: Location | None = None,
    ) -> None:
        self.edit(Insert(text, from_location, to_location, cursor_destination))

    def delete_range(
        self,
        from_location: Location,
        to_location: Location,
        cursor_destination: Location | None = None,
    ) -> str:
        """Delete text between from_location and to_location."""
        top, bottom = _fix_direction(from_location, to_location)
        deleted_text = self.edit(Delete(top, bottom, cursor_destination))
        return deleted_text

    def clear(self) -> None:
        """Clear the document."""
        document = self._document
        last_line = document[-1]
        document_end_location = (document.line_count, len(last_line))
        self.delete_range((0, 0), document_end_location, cursor_destination=(0, 0))

    def action_delete_left(self) -> None:
        """Deletes the character to the left of the cursor and updates the cursor location.

        If there's a selection, then the selected range is deleted."""

        selection = self.selection

        start, end = selection
        end_row, end_column = end

        if selection.is_empty:
            if self.cursor_at_start_of_document:
                return

            if self.cursor_at_start_of_row:
                end = (end_row - 1, len(self._document[end_row - 1]))
            else:
                end = (end_row, end_column - 1)

        self.delete_range(start, end)

    def action_delete_right(self) -> None:
        """Deletes the character to the right of the cursor and keeps the cursor at the same location.

        If there's a selection, then the selected range is deleted."""

        selection = self.selection
        start, end = selection
        end_row, end_column = end

        if selection.is_empty:
            if self.cursor_at_end_of_document:
                return
            if self.cursor_at_end_of_row:
                end = (end_row + 1, 0)
            else:
                end = (end_row, end_column + 1)

        self.delete_range(start, end)

    def action_delete_line(self) -> None:
        """Deletes the lines which intersect with the selection."""
        start, end = self.selection
        start_row, start_column = start
        end_row, end_column = end

        from_location = (start_row, 0)
        to_location = (end_row + 1, 0)

        self.delete_range(from_location, to_location)

    def action_delete_to_start_of_line(self) -> None:
        """Deletes from the cursor location to the start of the line."""
        from_location = self.selection.end
        cursor_row, cursor_column = from_location
        to_location = (cursor_row, 0)
        self.delete_range(from_location, to_location)

    def action_delete_to_end_of_line(self) -> None:
        """Deletes from the cursor location to the end of the line."""
        from_location = self.selection.end
        cursor_row, cursor_column = from_location
        to_location = (cursor_row, len(self._document[cursor_row]))
        self.delete_range(from_location, to_location)

    def action_delete_word_left(self) -> None:
        """Deletes the word to the left of the cursor and updates the cursor location."""
        if self.cursor_at_start_of_document:
            return

        # If there's a non-zero selection, then "delete word left" typically only
        # deletes the characters within the selection range, ignoring word boundaries.
        start, end = self.selection
        if start != end:
            self.delete_range(start, end)

        cursor_row, cursor_column = end

        # Check the current line for a word boundary
        line = self._document[cursor_row][:cursor_column]
        matches = list(re.finditer(self.word_pattern, line))

        if matches:
            # If a word boundary is found, delete the word
            from_location = (cursor_row, matches[-1].start())
        elif cursor_row > 0:
            # If no word boundary is found, and we're not on the first line, delete to the end of the previous line
            from_location = (cursor_row - 1, len(self._document[cursor_row - 1]))
        else:
            # If we're already on the first line and no word boundary is found, delete to the start of the line
            from_location = (cursor_row, 0)

        self.delete_range(from_location, self.selection.end)

    def action_delete_word_right(self) -> None:
        """Deletes the word to the right of the cursor and keeps the cursor at the same location."""
        if self.cursor_at_end_of_document:
            return

        start, end = self.selection
        if start != end:
            self.delete_range(start, end)

        cursor_row, cursor_column = end

        # Check the current line for a word boundary
        line = self._document[cursor_row][cursor_column:]
        matches = list(re.finditer(self.word_pattern, line))

        if matches:
            # If a word boundary is found, delete the word
            to_location = (cursor_row, cursor_column + matches[0].end())
        elif cursor_row < self._document.line_count - 1:
            # If no word boundary is found, and we're not on the last line, delete to the start of the next line
            to_location = (cursor_row + 1, 0)
        else:
            # If we're already on the last line and no word boundary is found, delete to the end of the line
            to_location = (cursor_row, len(self._document[cursor_row]))

        self.delete_range(end, to_location)
