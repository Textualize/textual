from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import ClassVar

from rich.text import Text

from textual import events
from textual._cells import cell_len
from textual._fix_direction import _fix_direction
from textual._types import Literal, Protocol, runtime_checkable
from textual.binding import Binding
from textual.document._document import Document, Selection
from textual.geometry import Offset, Region, Size, Spacing, clamp
from textual.reactive import Reactive, reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip


@runtime_checkable
class Edit(Protocol):
    """Protocol for actions performed in the text editor that can be done and undone."""

    def do(self, editor: TextArea) -> object | None:
        """Do the action."""

    def undo(self, editor: TextArea) -> object | None:
        """Undo the action."""

    def post_refresh(self, editor: TextArea) -> None:
        """Code to execute after content size recalculated and repainted."""


@dataclass
class Insert:
    """Implements the Edit protocol for inserting text at some location."""

    text: str
    from_location: tuple[int, int]
    to_location: tuple[int, int]
    cursor_destination: tuple[int, int] | None = None
    _edit_end: tuple[int, int] | None = field(init=False, default=None)

    def do(self, editor: TextArea) -> None:
        self._edit_end = editor._document.insert_range(
            self.from_location,
            self.to_location,
            self.text,
        )

    def undo(self, editor: TextArea) -> None:
        """Undo the action."""

    def post_refresh(self, editor: TextArea) -> None:
        # Update the cursor location
        cursor_destination = self.cursor_destination
        if cursor_destination is not None:
            editor.selection = cursor_destination
        else:
            editor.selection = Selection.cursor(self._edit_end)


@dataclass
class Delete:
    """Performs a delete operation."""

    from_location: tuple[int, int]
    """The location to delete from (inclusive)."""

    to_location: tuple[int, int]
    """The location to delete to (exclusive)."""

    cursor_destination: tuple[int, int] | None = None
    """Where to move the cursor to after the deletion."""

    _deleted_text: str | None = field(init=False, default=None)
    """The text that was deleted, or None if the deletion hasn't occurred yet."""

    def do(self, editor: TextArea) -> str:
        """Do the delete action and record the text that was deleted."""
        self._deleted_text = editor._document.delete_range(
            self.from_location, self.to_location
        )
        return self._deleted_text

    def undo(self, editor: TextArea) -> None:
        """Undo the delete action."""

    def post_refresh(self, editor: TextArea) -> None:
        cursor_destination = self.cursor_destination
        if cursor_destination is not None:
            editor.selection = Selection.cursor(cursor_destination)
        else:
            editor.selection = Selection.cursor(self.from_location)


class TextArea(ScrollView, can_focus=True):
    DEFAULT_CSS = """\
$text-area-active-line-bg: white 8%;
TextArea {
    background: $panel;
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
"""

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "text-area--active-line",
        "text-area--active-line-gutter",
        "text-area--gutter",
        "text-area--cursor",
        "text-area--selection",
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
        Binding("ctrl+d", "delete_right", "delete right", show=False),
        Binding(
            "ctrl+f", "delete_word_right", "delete right to start of word", show=False
        ),
        Binding("ctrl+x", "delete_line", "delete line", show=False),
        Binding(
            "ctrl+u", "delete_to_start_of_line", "delete to line start", show=False
        ),
        Binding("ctrl+k", "delete_to_end_of_line", "delete to line end", show=False),
    ]

    language: Reactive[str | None] = reactive(None)
    """The language to use for syntax highlighting (via tree-sitter)."""

    selection: Reactive[Selection] = reactive(Selection())
    """The selection location (zero-based line_index, offset)."""

    show_line_numbers: Reactive[bool] = reactive(True)
    """True to show line number gutter, otherwise False."""

    indent_width: Reactive[int] = reactive(4)
    """The width of tabs or the number of spaces to insert on pressing the `tab` key."""

    _document_size: Reactive[Size] = reactive(Size(), init=False, always_update=True)
    """Tracks the size of the document.

    This is the width and height of the bounding box of the text.
    Used to update virtual size.
    """

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        # --- Core editor data
        self._document = Document()
        """The document this widget is currently editing."""

        self.indent_type: Literal["tabs", "spaces"] = "spaces"
        """Whether to indent using tabs or spaces."""

        self._last_intentional_cell_width: int = 0
        """Tracks the last column (measured in terms of cell length, since we care here about where the cursor
        visually moves more than the logical characters) the user explicitly navigated to so that we can reset to it
        whenever possible."""

        self._word_pattern = re.compile(r"(?<=\W)(?=\w)|(?<=\w)(?=\W)")
        """Compiled regular expression for what we consider to be a 'word'."""

        self._undo_stack: list[Edit] = []
        """A stack (the end of the list is the top of the stack) for tracking edits."""

        self._selecting = False
        """True if we're currently selecting text, otherwise False."""

    def watch__document_size(self, size: Size) -> None:
        document_width, document_height = size
        self.virtual_size = Size(
            document_width + self.gutter_width + 1, document_height
        )

    def load_text(self, text: str) -> None:
        """Load text from a string into the editor.

        Args:
            text: The text to load into the editor.
        """
        self._document.load_text(text)
        self._refresh_size()

    def _refresh_size(self) -> None:
        # Calculate document
        lines = self._document.lines
        text_width = max(cell_len(line.expandtabs(self.indent_width)) for line in lines)
        height = len(lines)
        self._document_size = Size(text_width, height)

    def render_line(self, widget_y: int) -> Strip:
        document = self._document

        line_index = round(self.scroll_y + widget_y)
        out_of_bounds = line_index >= document.line_count
        if out_of_bounds:
            return Strip.blank(self.size.width)

        line = document.get_line_text(line_index)
        line.tab_size = self.indent_width
        codepoint_count = len(line)
        line.set_length(self.virtual_size.width)

        selection = self.selection
        start, end = selection
        selection_top, selection_bottom = selection.range
        selection_top_row, selection_top_column = selection_top
        selection_bottom_row, selection_bottom_column = selection_bottom

        if start != end and selection_top_row <= line_index <= selection_bottom_row:
            # If this row intersects with the selection range
            selection_style = self.get_component_rich_style("text-area--selection")
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
                        end=codepoint_count,
                    )
                elif line_index == selection_bottom_row:
                    line.stylize_before(selection_style, end=selection_bottom_column)
                else:
                    line.stylize_before(selection_style, end=codepoint_count)

        # Highlight the cursor
        cursor_row, cursor_column = end
        if cursor_row == line_index:
            cursor_style = self.get_component_rich_style("text-area--cursor")
            line.stylize(cursor_style, cursor_column, cursor_column + 1)
            active_line_style = self.get_component_rich_style("text-area--active-line")
            line.stylize_before(active_line_style)

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
            line, self.app.console.options.update_width(self.virtual_size.width)
        )

        # Crop the line to show only the visible part (some may be scrolled out of view)
        virtual_width, virtual_height = self.virtual_size
        text_crop_start = int(self.scroll_x)
        text_crop_end = text_crop_start + virtual_width

        gutter_strip = Strip(gutter_segments)
        text_strip = Strip(text_segments).crop(text_crop_start, text_crop_end)

        # Join and return the gutter and the visible portion of this line
        strip = Strip.join([gutter_strip, text_strip]).simplify()
        return strip

    @property
    def gutter_width(self) -> int:
        # The longest number in the gutter plus two extra characters: `│ `.
        gutter_margin = 2
        gutter_longest_number = (
            len(str(self._document.line_count + 1)) + gutter_margin
            if self.show_line_numbers
            else 0
        )
        return gutter_longest_number

    def edit(self, edit: Edit) -> object | None:
        result = edit.do(self)

        # TODO: Think about this...
        self._undo_stack.append(edit)
        self._undo_stack = self._undo_stack[-20:]

        self._refresh_size()
        edit.post_refresh(self)

        return result

    def undo(self) -> None:
        if self._undo_stack:
            action = self._undo_stack.pop()
            action.undo(self)

    # --- Lower level event/key handling
    def _on_key(self, event: events.Key) -> None:
        key = event.key
        if event.is_printable or key == "tab" or key == "enter":
            event.stop()
            event.prevent_default()
            if key == "tab":
                insert = (
                    " " * self.indent_width if self.indent_type == "spaces" else "\t"
                )
            elif key == "enter":
                insert = "\n"
            else:
                insert = event.character
            assert event.character is not None
            start, end = self.selection
            self.insert_text_range(insert, start, end)

    def get_target_document_location(self, offset: Offset) -> tuple[int, int]:
        target_x = max(offset.x - self.gutter_width + int(self.scroll_x), 0)
        target_row = clamp(
            offset.y + int(self.scroll_y), 0, self._document.line_count - 1
        )
        target_column = self.cell_width_to_column_index(target_x, target_row)

        return target_row, target_column

    def _on_mouse_down(self, event: events.MouseDown) -> None:
        offset = event.get_content_offset_capture(self)
        if offset is not None:
            target = self.get_target_document_location(event)
            self.selection = Selection.cursor(target)
            self._selecting = True
            self.capture_mouse(True)

    def _on_mouse_move(self, event: events.MouseMove) -> None:
        if self._selecting:
            offset = event.get_content_offset_capture(self)
            if offset is not None:
                target = self.get_target_document_location(event)
                selection_start, _ = self.selection
                self.selection = Selection(selection_start, target)

    def _on_mouse_up(self, event: events.MouseUp) -> None:
        self._record_last_intentional_cell_width()
        self._selecting = False
        self.capture_mouse(False)

    def _on_paste(self, event: events.Paste) -> None:
        text = event.text
        if text:
            start, end = self.selection
            self.insert_text_range(text, start, end, end)

    def cell_width_to_column_index(self, cell_width: int, row_index: int) -> int:
        """Return the column that the cell width corresponds to on the given row."""
        tab_width = self.indent_width
        total_cell_offset = 0
        line = self._document[row_index]
        for column_index, character in enumerate(line):
            total_cell_offset += cell_len(character.expandtabs(tab_width))
            if total_cell_offset >= cell_width + 1:
                return column_index
        return len(line)

    def watch_selection(self) -> None:
        self.scroll_cursor_visible()

    def validate_selection(self, selection: Selection) -> Selection:
        start, end = selection
        clamp_visitable = self.clamp_visitable
        return Selection(clamp_visitable(start), clamp_visitable(end))

    # --- Cursor/selection utilities
    def is_visitable(self, location: tuple[int, int]) -> bool:
        """Return True if the location is somewhere that can naturally be reached by the cursor.

        Generally this means it's at a row within the document, and a column which contains a character,
        OR at the resting location at the end of a row."""
        row, column = location
        document = self._document
        row_text = document[row]
        is_valid_row = row < document.line_count
        is_valid_column = column <= len(row_text)
        return is_valid_row and is_valid_column

    def is_visitable_selection(self, selection: Selection) -> bool:
        """Return True if the Selection is valid (start and end in bounds)"""
        visitable = self.is_visitable
        start, end = selection
        return visitable(start) and visitable(end)

    def clamp_visitable(self, location: tuple[int, int]) -> tuple[int, int]:
        document = self._document

        row, column = location
        try:
            line_text = document[row]
        except IndexError:
            line_text = ""

        row = clamp(row, 0, document.line_count - 1)
        column = clamp(column, 0, len(line_text))

        return row, column

    def scroll_cursor_visible(self):
        row, column = self.selection.end
        text = self.cursor_line_text[:column]
        column_offset = cell_len(text.expandtabs(self.indent_width))
        self.scroll_to_region(
            Region(x=column_offset, y=row, width=3, height=1),
            spacing=Spacing(right=self.gutter_width),
            animate=False,
            force=True,
        )

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

        self._record_last_intentional_cell_width()

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

    # ------ Cursor movement actions
    def action_cursor_left(self) -> None:
        """Move the cursor one location to the left.

        If the cursor is at the left edge of the document, try to move it to
        the end of the previous line.
        """
        target = self.get_cursor_left_location()
        self.selection = Selection.cursor(target)
        self._record_last_intentional_cell_width()

    def action_cursor_left_select(self):
        """Move the end of the selection one location to the left.

        This will expand or contract the selection.
        """
        new_cursor_location = self.get_cursor_left_location()
        selection_start, selection_end = self.selection
        self.selection = Selection(selection_start, new_cursor_location)
        self._record_last_intentional_cell_width()

    def get_cursor_left_location(self) -> tuple[int, int]:
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
        self._record_last_intentional_cell_width()

    def action_cursor_right_select(self):
        """Move the end of the selection one location to the right.

        This will expand or contract the selection.
        """
        new_cursor_location = self.get_cursor_right_location()
        selection_start, selection_end = self.selection
        self.selection = Selection(selection_start, new_cursor_location)
        self._record_last_intentional_cell_width()

    def get_cursor_right_location(self) -> tuple[int, int]:
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

    def get_cursor_up_location(self) -> tuple[int, int]:
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
        matches = list(re.finditer(self._word_pattern, line))

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
        self._record_last_intentional_cell_width()

    def action_cursor_right_word(self) -> None:
        """Move the cursor right by a single word, skipping spaces."""

        if self.cursor_at_end_of_document:
            return

        cursor_row, cursor_column = self.selection.end

        # Check the current line for a word boundary
        line = self._document[cursor_row][cursor_column:]
        matches = list(re.finditer(self._word_pattern, line))

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
        self._record_last_intentional_cell_width()

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
        # TODO - consider empty documents
        return self._document[self.selection.end[0]]

    def get_column_cell_width(self, row: int, column: int) -> int:
        """Given a row and column index within the editor, return the cell offset
        of the column from the start of the row (the left edge of the editor content area).
        """
        line = self._document[row]
        return cell_len(line[:column].expandtabs(self.indent_width))

    def _record_last_intentional_cell_width(self) -> None:
        row, column = self.selection.end
        column_cell_length = self.get_column_cell_width(row, column)
        self._last_intentional_cell_width = column_cell_length

    # --- Editor operations
    def insert_text(
        self,
        text: str,
        location: tuple[int, int],
        cursor_destination: tuple[int, int] | None = None,
    ) -> None:
        self.edit(Insert(text, location, location, cursor_destination))

    def insert_text_range(
        self,
        text: str,
        from_location: tuple[int, int],
        to_location: tuple[int, int],
        cursor_destination: tuple[int, int] | None = None,
    ) -> None:
        self.edit(Insert(text, from_location, to_location, cursor_destination))

    def delete_range(
        self,
        from_location: tuple[int, int],
        to_location: tuple[int, int],
        cursor_destination: tuple[int, int] | None = None,
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
        self.delete_range((0, 0), document_end_location)

    def action_delete_left(self) -> None:
        """Deletes the character to the left of the cursor and updates the cursor location."""

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
        """Deletes the character to the right of the cursor and keeps the cursor at the same location."""
        if self.cursor_at_end_of_document:
            return

        start, end = self.selection
        end_row, end_column = end

        if self.cursor_at_end_of_row:
            to_location = (end_row + 1, 0)
        else:
            to_location = (end_row, end_column + 1)

        self.delete_range(start, to_location)

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
        matches = list(re.finditer(self._word_pattern, line))

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
        matches = list(re.finditer(self._word_pattern, line))

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

    # --- Debugging
    @dataclass
    class EditorDebug:
        cursor: tuple[int, int]
        language: str
        document_size: Size
        virtual_size: Size
        scroll: Offset
        undo_stack: list[Edit]
        tree_sexp: str
        active_line_text: str
        active_line_cell_len: int

    def _debug_state(self) -> "EditorDebug":
        return self.EditorDebug(
            cursor=self.selection,
            language=self.language,
            document_size=self._document_size,
            virtual_size=self.virtual_size,
            scroll=self.scroll_offset,
            undo_stack=list(reversed(self._undo_stack)),
            # tree_sexp=self._syntax_tree.root_node.sexp(),
            tree_sexp="",
            active_line_text=repr(self.cursor_line_text),
            active_line_cell_len=cell_len(self.cursor_line_text),
        )
