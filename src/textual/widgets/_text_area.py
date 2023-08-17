from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from rich.style import Style
from rich.text import Text

from textual.document._document import DocumentBase

if TYPE_CHECKING:
    from tree_sitter import Language

from textual import events, log
from textual._cells import cell_len
from textual._fix_direction import _sort_ascending
from textual._types import Literal, Protocol, runtime_checkable
from textual.binding import Binding
from textual.document import Document, EditResult, Location, Selection, SyntaxTheme
from textual.events import MouseEvent
from textual.geometry import Offset, Region, Size, Spacing, clamp
from textual.reactive import Reactive, reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip


class TextArea(ScrollView, can_focus=True):
    DEFAULT_CSS = """\
$text-area-active-line-bg: white 8%;

TextArea {
    background: $panel;
    width: 1fr;
    height: 1fr;
}
TextArea > .text-area--cursor-line {
    background: $text-area-active-line-bg;
}
TextArea > .text-area--cursor-line-gutter {
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
        "text-area--cursor",
        "text-area--gutter",
        "text-area--cursor-line",
        "text-area--cursor-line-gutter",
        "text-area--selection",
        "text-area--width-guide",
    }
    """| Class                           | Description                                      |
|:--------------------------------|:-------------------------------------------------|
| `text-area--cursor`             | Targets the cursor.                              |
| `text-area--gutter`             | Targets the gutter (line number column).         |
| `text-area--cursor-line`        | Targets the line of text the cursor is on.       |
| `text-area--cursor-line-gutter` | Targets the gutter of the line the cursor is on. |
| `text-area--selection`          | Targets the selected text.                       |
| `text-area--width-guide`        | Targets the width guide.                         |
 """

    BINDINGS = [
        Binding("escape", "screen.focus_next", "focus next", show=False),
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
    """
    | Key(s)                 | Description                                  |
    | :-                     | :-                                           |
    | escape                 | Focus on the next item.                      |
    | up                     | Move the cursor up.                          |
    | down                   | Move the cursor down.                        |
    | left                   | Move the cursor left.                        |
    | ctrl+left              | Move the cursor to the start of the word.    |
    | right                  | Move the cursor right.                       |
    | ctrl+right             | Move the cursor to the end of the word.      |
    | home,ctrl+a            | Move the cursor to the start of the line.    |
    | end,ctrl+e             | Move the cursor to the end of the line.      |
    | pageup                 | Move the cursor one page up.                 |
    | pagedown               | Move the cursor one page down.               |
    | shift+up               | Select while moving the cursor up.           |
    | shift+down             | Select while moving the cursor down.         |
    | shift+left             | Select while moving the cursor left.         |
    | shift+right            | Select while moving the cursor right.        |
    | backspace              | Delete character to the left of cursor.      |
    | ctrl+w                 | Delete from cursor to start of the word.     |
    | delete,ctrl+d          | Delete character to the right of cursor.     |
    | ctrl+f                 | Delete from cursor to end of the word.       |
    | ctrl+x                 | Delete the current line.                     |
    | ctrl+u                 | Delete from cursor to the start of the line. |
    | ctrl+k                 | Delete from cursor to the end of the line.   |
    """

    language: Reactive[str | "Language" | None] = reactive(None, always_update=True)
    """The language to use.

    This must be set to a valid, non-None value for syntax highlighting to work.

    Check valid languages using the `TextArea.valid_languages` property.

    If the value is a string, a built-in parser will be used.

    If you wish to add support for an unsupported language, you'll have to pass in the
    tree-sitter `Language` object directly rather than the string language name.
    """

    theme: Reactive[str | SyntaxTheme] = reactive(SyntaxTheme.default())
    """The theme to syntax highlight with.

    Supply a `SyntaxTheme` object to customise highlighting, or supply a builtin
    theme name as a string.

    Syntax highlighting is only possible when the `language` attribute is set.
    """

    selection: Reactive[Selection] = reactive(Selection(), always_update=True)
    """The selection start and end locations (zero-based line_index, offset).

    This represents the cursor location and the current selection.

    The `Selection.end` always refers to the cursor location.

    If no text is selected, then `Selection.end == Selection.start`.

    The text selected in the document is available via the `TextArea.selected_text` property.
    """

    show_line_numbers: Reactive[bool] = reactive(True)
    """True to show the line number column on the left edge, otherwise False.

    Changing this value will immediately re-render the `TextArea`."""

    indent_width: Reactive[int] = reactive(4)
    """The width of tabs or the number of spaces to insert on pressing the `tab` key.

    If the document currently open contains tabs that are currently visible on screen,
    altering this value will immediately change the display width of the visible tabs.
    """

    _show_width_guide: Reactive[bool] = reactive(False)
    """If True, a vertical line will indicate the width of the document."""

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        self.document = Document("")
        """The document this widget is currently editing."""

        self.indent_type: Literal["tabs", "spaces"] = "spaces"
        """Whether to indent using tabs or spaces."""

        self.word_pattern = re.compile(r"(?<=\W)(?=\w)|(?<=\w)(?=\W)")
        """Compiled regular expression for what we consider to be a 'word'."""

        self._last_intentional_cell_width: int = 0
        """Tracks the last column (measured in terms of cell length, since we care here about where the cursor
        visually moves rather than logical characters) the user explicitly navigated to so that we can reset to it
        whenever possible."""

        self._undo_stack: list[Undoable] = []
        """A stack (the end of the list is the top of the stack) for tracking edits."""

        self._selecting = False
        """True if we're currently selecting text using the mouse, otherwise False."""

    def _watch_selection(self) -> None:
        """When the cursor moves, scroll it into view."""
        self.scroll_cursor_visible()

    def _validate_selection(self, selection: Selection) -> Selection:
        """Clamp the selection to valid locations."""
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
        text = self.document.text
        if not language:
            # If there's no language set, we don't need to use a SyntaxAwareDocument.
            self.document = Document(text)
        else:
            try:
                from textual.document._syntax_aware_document import SyntaxAwareDocument

                self.document = SyntaxAwareDocument(text, language, self.theme)
            except ImportError:
                # SyntaxAwareDocument isn't available on Python 3.7.
                # Fall back to the standard document.
                log.warning("Syntax highlighting isn't available on Python 3.7.")
                self.document = Document(text)

    def load_text(self, text: str) -> None:
        """Load text from a string into the TextArea.

        Args:
            text: The text to load into the TextArea.
        """
        self.document = Document(text)
        self._reload_document()
        self.move_cursor((0, 0))
        self._refresh_size()

    def load_document(self, document: DocumentBase) -> None:
        """Load a document into the TextArea.

        Args:
            document: The document to load into the TextArea.
        """
        self.document = document
        self.move_cursor((0, 0))
        self._refresh_size()

    def _refresh_size(self) -> None:
        """Update the virtual size of the TextArea."""
        width, height = self.document.get_size(self.indent_width)
        # +1 width to make space for the cursor resting at the end of the line
        self.virtual_size = Size(width + self.gutter_width + 1, height)

    def render_line(self, widget_y: int) -> Strip:
        """Render a single line of the TextArea. Called by Textual.

        Args:
            widget_y: Y Coordinate of line relative to the widget region.

        Returns:
            A rendered line.
        """
        document = self.document
        scroll_x, scroll_y = self.scroll_offset

        # Account for how much the TextArea is scrolled.
        line_index = widget_y + scroll_y

        # Render the lines beyond the valid line numbers
        out_of_bounds = line_index >= document.line_count
        if out_of_bounds:
            return Strip.blank(self.size.width)

        # Get the (possibly highlighted) line from the Document.
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
            cursor_row, _ = end
            if line_character_count == 0 and line_index != cursor_row:
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
        active_line_style = self.get_component_rich_style("text-area--cursor-line")
        if cursor_row == line_index:
            cursor_style = self.get_component_rich_style("text-area--cursor")
            line.stylize(cursor_style, cursor_column, cursor_column + 1)
            line.stylize_before(active_line_style)

        # The width guide is a visual indicator showing the virtual width of the TextArea widget.
        if self._show_width_guide:
            width_guide_style = self.get_component_rich_style("text-area--width-guide")
            width_column = virtual_width - self.gutter_width
            line.stylize_before(width_guide_style, width_column - 1, width_column)

        # Build the gutter text for this line
        if self.show_line_numbers:
            if cursor_row == line_index:
                gutter_style = self.get_component_rich_style(
                    "text-area--cursor-line-gutter"
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
        return self.document.text

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
        start, end = _sort_ascending(start, end)
        return self.document.get_text_range(start, end)

    def edit(self, edit: Edit) -> Any:
        """Perform an Edit.

        Args:
            edit: The Edit to perform.

        Returns:
            Data relating to the edit that may be useful. The data returned
            may be different depending on the edit performed.
        """
        result = edit.do(self)
        self._refresh_size()
        edit.after(self)
        return result

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
            start, end = self.selection
            self.replace(insert, start, end, False)

    # --- Lower level event/key handling
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
            self.document.line_count - 1,
        )
        target_column = self.cell_width_to_column_index(target_x, target_row)
        return target_row, target_column

    @property
    def gutter_width(self) -> int:
        """The width of the gutter (the left column containing line numbers).

        Returns:
            The cell-width of the line number column. If `show_line_numbers` is `False` returns 0.
        """
        # The longest number in the gutter plus two extra characters: `│ `.
        gutter_margin = 2
        gutter_width = (
            len(str(self.document.line_count + 1)) + gutter_margin
            if self.show_line_numbers
            else 0
        )
        return gutter_width

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
        self.record_cursor_width()

    def _on_paste(self, event: events.Paste) -> None:
        """When a paste occurs, insert the text from the paste event into the document."""
        text = event.text
        if text:
            self.replace(text, *self.selection)

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
        line = self.document[row_index]
        for column_index, character in enumerate(line):
            total_cell_offset += cell_len(character.expandtabs(tab_width))
            if total_cell_offset >= cell_width + 1:
                return column_index
        return len(line)

    def clamp_visitable(self, location: Location) -> Location:
        """Clamp the given location to the nearest visitable location.

        Args:
            location: The location to clamp.

        Returns:
            The nearest location that we could conceivably navigate to using the cursor.
        """
        document = self.document

        row, column = location
        try:
            line_text = document[row]
        except IndexError:
            line_text = ""

        row = clamp(row, 0, document.line_count - 1)
        column = clamp(column, 0, len(line_text))

        return row, column

    # --- Cursor/selection utilities
    def scroll_cursor_visible(
        self, center: bool = False, animate: bool = False
    ) -> Offset:
        """Scroll the `TextArea` such that the cursor is visible on screen.

        Args:
            center: True if the cursor should be scrolled to the center.
            animate: True if we should animate while scrolling.

        Returns:
            The offset that was scrolled to bring the cursor into view.
        """
        row, column = self.selection.end
        text = self.document[row][:column]
        column_offset = cell_len(text.expandtabs(self.indent_width))
        scroll_offset = self.scroll_to_region(
            Region(x=column_offset, y=row, width=3, height=1),
            spacing=Spacing(right=self.gutter_width),
            animate=animate,
            force=True,
            center=center,
        )
        return scroll_offset

    def move_cursor(
        self,
        location: Location,
        select: bool = False,
        center: bool = False,
        record_width: bool = True,
    ) -> None:
        """Move the cursor to a location.

        Args:
            location: The location to move the cursor to.
            select: If True, select text between the old and new location.
            center: If True, scroll such that the cursor is centered.
            record_width: If True, record the cursor column cell width after navigating
                so that we jump back to the same width the next time we move to a row
                that is wide enough.
        """
        if select:
            start, end = self.selection
            self.selection = Selection(start, location)
        else:
            self.selection = Selection.cursor(location)

        if record_width:
            self.record_cursor_width()

        if center:
            self.scroll_cursor_visible(center)

    def move_cursor_relative(
        self,
        rows: int = 0,
        columns: int = 0,
        select: bool = False,
        center: bool = False,
        record_width: bool = True,
    ) -> None:
        """Move the cursor relative to its current location.

        Args:
            rows: The number of rows to move down by (negative to move up)
            columns:  The number of columns to move right by (negative to move left)
            select: If True, select text between the old and new location.
            center: If True, scroll such that the cursor is centered.
            record_width: If True, record the cursor column cell width after navigating
                so that we jump back to the same width the next time we move to a row
                that is wide enough.
        """
        clamp_visitable = self.clamp_visitable
        start, end = self.selection
        current_row, current_column = end
        target = clamp_visitable(Location(current_row + rows, current_column + columns))
        self.move_cursor(target, select, center, record_width)

    @property
    def cursor_location(self) -> Location:
        """The current location of the cursor in the document.

        This is a utility for accessing the `end` of `TextArea.selection`.
        """
        return self.selection.end

    @cursor_location.setter
    def cursor_location(self, location: Location) -> None:
        """Set the cursor_location to a new location.

        If a selection is in progress, the anchor point will remain.
        """
        self.move_cursor(location, select=not self.selection.is_empty)

    @property
    def cursor_at_first_row(self) -> bool:
        """True if and only if the cursor is on the first row."""
        return self.selection.end[0] == 0

    @property
    def cursor_at_last_row(self) -> bool:
        """True if and only if the cursor is on the last row."""
        return self.selection.end[0] == self.document.line_count - 1

    @property
    def cursor_at_start_of_row(self) -> bool:
        """True if and only if the cursor is at column 0."""
        return self.selection.end[1] == 0

    @property
    def cursor_at_end_of_row(self) -> bool:
        """True if and only if the cursor is at the end of a row."""
        cursor_row, cursor_column = self.selection.end
        row_length = len(self.document[cursor_row])
        cursor_at_end = cursor_column == row_length
        return cursor_at_end

    @property
    def cursor_at_start_of_document(self) -> bool:
        """True if and only if the cursor is at location (0, 0)"""
        return self.selection.end == (0, 0)

    @property
    def cursor_at_end_of_document(self) -> bool:
        """True if and only if the cursor is at the very end of the document."""
        return self.cursor_at_last_row and self.cursor_at_end_of_row

    # ------ Cursor movement actions
    def action_cursor_left(self) -> None:
        """Move the cursor one location to the left.

        If the cursor is at the left edge of the document, try to move it to
        the end of the previous line.
        """
        target = self.get_cursor_left_location()
        self.selection = Selection.cursor(target)
        self.record_cursor_width()

    def action_cursor_left_select(self):
        """Move the end of the selection one location to the left.

        This will expand or contract the selection.
        """
        new_cursor_location = self.get_cursor_left_location()
        selection_start, selection_end = self.selection
        self.selection = Selection(selection_start, new_cursor_location)
        self.record_cursor_width()

    def get_cursor_left_location(self) -> Location:
        """Get the location the cursor will move to if it moves left.

        Returns:
            The location of the cursor if it moves left.
        """
        if self.cursor_at_start_of_document:
            return 0, 0
        cursor_row, cursor_column = self.selection.end
        length_of_row_above = len(self.document[cursor_row - 1])
        target_row = cursor_row if cursor_column != 0 else cursor_row - 1
        target_column = cursor_column - 1 if cursor_column != 0 else length_of_row_above
        return target_row, target_column

    def action_cursor_right(self) -> None:
        """Move the cursor one location to the right.

        If the cursor is at the end of a line, attempt to go to the start of the next line.
        """
        target = self.get_cursor_right_location()
        self.move_cursor(target)
        self.record_cursor_width()

    def action_cursor_right_select(self):
        """Move the end of the selection one location to the right."""
        target = self.get_cursor_right_location()
        self.move_cursor(target, select=True)

    def get_cursor_right_location(self) -> Location:
        """Get the location the cursor will move to if it moves right.

        Returns:
            the location the cursor will move to if it moves right.
        """
        if self.cursor_at_end_of_document:
            return self.selection.end
        cursor_row, cursor_column = self.selection.end
        target_row = cursor_row + 1 if self.cursor_at_end_of_row else cursor_row
        target_column = 0 if self.cursor_at_end_of_row else cursor_column + 1
        return target_row, target_column

    def action_cursor_down(self) -> None:
        """Move the cursor down one cell."""
        target = self.get_cursor_down_location()
        self.move_cursor(target, record_width=False)

    def action_cursor_down_select(self) -> None:
        """Move the cursor down one cell, selecting the range between the old and new locations."""
        target = self.get_cursor_down_location()
        self.move_cursor(target, select=True, record_width=False)

    def get_cursor_down_location(self) -> Location:
        """Get the location the cursor will move to if it moves down.

        Returns:
            the location the cursor will move to if it moves down.
        """
        cursor_row, cursor_column = self.selection.end
        if self.cursor_at_last_row:
            return cursor_row, len(self.document[cursor_row])

        target_row = min(self.document.line_count - 1, cursor_row + 1)
        # Attempt to snap last intentional cell length
        target_column = self.cell_width_to_column_index(
            self._last_intentional_cell_width, target_row
        )
        target_column = clamp(target_column, 0, len(self.document[target_row]))
        return target_row, target_column

    def action_cursor_up(self) -> None:
        """Move the cursor up one cell."""
        target = self.get_cursor_up_location()
        self.move_cursor(target, record_width=False)

    def action_cursor_up_select(self) -> None:
        """Move the cursor up one cell, selecting the range between the old and new locations."""
        target = self.get_cursor_up_location()
        self.move_cursor(target, select=True, record_width=False)

    def get_cursor_up_location(self) -> Location:
        """Get the location the cursor will move to if it moves up.

        Returns:
            the location the cursor will move to if it moves up.
        """
        if self.cursor_at_first_row:
            return 0, 0
        cursor_row, cursor_column = self.selection.end
        target_row = max(0, cursor_row - 1)
        # Attempt to snap last intentional cell length
        target_column = self.cell_width_to_column_index(
            self._last_intentional_cell_width, target_row
        )
        target_column = clamp(target_column, 0, len(self.document[target_row]))
        return target_row, target_column

    def action_cursor_line_end(self) -> None:
        """Move the cursor to the end of the line."""
        location = self.get_cursor_line_end_location()
        self.move_cursor(location)

    def get_cursor_line_end_location(self) -> Location:
        """Get the location of the end of the current line.

        Returns:
            The (row, column) location of the end of the cursors current line.
        """
        start, end = self.selection
        cursor_row, cursor_column = end
        target_column = len(self.document[cursor_row])
        return cursor_row, target_column

    def action_cursor_line_start(self) -> None:
        """Move the cursor to the start of the line."""
        target = self.get_cursor_line_start_location()
        self.move_cursor(target)

    def get_cursor_line_start_location(self) -> Location:
        """Get the location of the start of the current line.

        Returns:
            The (row, column) location of the start of the cursors current line.
        """
        _start, end = self.selection
        cursor_row, _cursor_column = end
        return cursor_row, 0

    def action_cursor_left_word(self) -> None:
        """Move the cursor left by a single word, skipping spaces."""
        if self.cursor_at_start_of_document:
            return
        target = self.get_cursor_left_word_location()
        self.move_cursor(target)

    def get_cursor_left_word_location(self) -> Location:
        """Get the location the cursor will jump to if it goes 1 word left.

        Returns:
            The location the cursor will jump on "jump word left".
        """
        cursor_row, cursor_column = self.cursor_location
        # Check the current line for a word boundary
        line = self.document[cursor_row][:cursor_column]
        matches = list(re.finditer(self.word_pattern, line))
        if matches:
            # If a word boundary is found, move the cursor there
            cursor_column = matches[-1].start()
        elif cursor_row > 0:
            # If no word boundary is found, and we're not on the first line, move to the end of the previous line
            cursor_row -= 1
            cursor_column = len(self.document[cursor_row])
        else:
            # If we're already on the first line and no word boundary is found, move to the start of the line
            cursor_column = 0
        return cursor_row, cursor_column

    def action_cursor_right_word(self) -> None:
        """Move the cursor right by a single word, skipping spaces."""

        if self.cursor_at_end_of_document:
            return

        target = self.get_cursor_right_word_location()
        self.move_cursor(target)

    def get_cursor_right_word_location(self):
        """Get the location the cursor will jump to if it goes 1 word right.

        Returns:
            The location the cursor will jump on "jump word right".
        """
        cursor_row, cursor_column = self.selection.end
        # Check the current line for a word boundary
        line = self.document[cursor_row][cursor_column:]
        matches = list(re.finditer(self.word_pattern, line))
        if matches:
            # If a word boundary is found, move the cursor there
            cursor_column += matches[0].end()
        elif cursor_row < self.document.line_count - 1:
            # If no word boundary is found and we're not on the last line, move to the start of the next line
            cursor_row += 1
            cursor_column = 0
        else:
            # If we're already on the last line and no word boundary is found, move to the end of the line
            cursor_column = len(self.document[cursor_row])
        return cursor_row, cursor_column

    def action_cursor_page_up(self) -> None:
        """Move the cursor and scroll up one page."""
        height = self.content_size.height
        _, cursor_location = self.selection
        row, column = cursor_location
        target = (row - height, column)
        self.scroll_relative(y=-height, animate=False)
        self.move_cursor(target)

    def action_cursor_page_down(self) -> None:
        """Move the cursor and scroll down one page."""
        height = self.content_size.height
        _, cursor_location = self.selection
        row, column = cursor_location
        target = (row + height, column)
        self.scroll_relative(y=height, animate=False)
        self.move_cursor(target)

    def get_column_width(self, row: int, column: int) -> int:
        """Get the cell offset of the column from the start of the row.

        Args:
            row: The row index.
            column: The column index (codepoint offset from start of row).

        Returns:
            The cell width of the column relative to the start of the row.
        """
        line = self.document[row]
        return cell_len(line[:column].expandtabs(self.indent_width))

    def record_cursor_width(self) -> None:
        """Record the current cell width of the cursor.

        This is used where we navigate up and down through rows.
        If we're in the middle of a row, and go down to a row with no
        content, then we go down to another row, we want our cursor to
        jump back to the same offset that we were originally at.
        """
        row, column = self.selection.end
        column_cell_length = self.get_column_width(row, column)
        self._last_intentional_cell_width = column_cell_length

    # --- Editor operations
    def insert(
        self,
        text: str,
        location: Location | None = None,
        maintain_selection_offset: bool = True,
    ) -> EditResult:
        """Insert text into the document.

        Args:
            text: The text to insert.
            location: The location to insert text, or None to use the cursor location.
            maintain_selection_offset: If True, the active Selection will be updated
                such that the same text is selected before and after the selection,
                if possible. Otherwise, the cursor will jump to the end point of the
                edit.

        Returns:
            An EditResult containing information about the edit.
        """
        if location is None:
            location = self.cursor_location
        return self.edit(Edit(text, location, location, maintain_selection_offset))

    def delete(
        self,
        start: Location,
        end: Location,
        maintain_selection_offset: bool = True,
    ) -> EditResult:
        """Delete the text between two locations in the document.

        Args:
            start: The start location.
            end: The end location.
            maintain_selection_offset: If True, the active Selection will be updated
                such that the same text is selected before and after the selection,
                if possible. Otherwise, the cursor will jump to the end point of the
                edit.

        Returns:
            An EditResult containing information about the edit.
        """
        top, bottom = _sort_ascending(start, end)
        return self.edit(Edit("", top, bottom, maintain_selection_offset))

    def replace(
        self,
        insert: str,
        start: Location,
        end: Location,
        maintain_selection_offset: bool = True,
    ) -> EditResult:
        """Replace text in the document with new text.

        Args:
            insert: The text to insert.
            start: The start location
            end: The end location.
            maintain_selection_offset: If True, the active Selection will be updated
                such that the same text is selected before and after the selection,
                if possible. Otherwise, the cursor will jump to the end point of the
                edit.

        Returns:
            An EditResult containing information about the edit.
        """
        return self.edit(Edit(insert, start, end, maintain_selection_offset))

    def clear(self) -> None:
        """Delete all text from the document."""
        document = self.document
        last_line = document[-1]
        document_end = (document.line_count, len(last_line))
        self.delete((0, 0), document_end, maintain_selection_offset=False)

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
                end = (end_row - 1, len(self.document[end_row - 1]))
            else:
                end = (end_row, end_column - 1)

        self.delete(start, end, maintain_selection_offset=False)

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

        self.delete(start, end, maintain_selection_offset=False)

    def action_delete_line(self) -> None:
        """Deletes the lines which intersect with the selection."""
        start, end = self.selection
        start, end = _sort_ascending(start, end)
        start_row, start_column = start
        end_row, end_column = end

        from_location = (start_row, 0)
        to_location = (end_row + 1, 0)

        self.delete(from_location, to_location, maintain_selection_offset=False)

    def action_delete_to_start_of_line(self) -> None:
        """Deletes from the cursor location to the start of the line."""
        from_location = self.selection.end
        cursor_row, cursor_column = from_location
        to_location = (cursor_row, 0)
        self.delete(from_location, to_location, maintain_selection_offset=False)

    def action_delete_to_end_of_line(self) -> None:
        """Deletes from the cursor location to the end of the line."""
        from_location = self.selection.end
        cursor_row, cursor_column = from_location
        to_location = (cursor_row, len(self.document[cursor_row]))
        self.delete(from_location, to_location, maintain_selection_offset=False)

    def action_delete_word_left(self) -> None:
        """Deletes the word to the left of the cursor and updates the cursor location."""
        if self.cursor_at_start_of_document:
            return

        # If there's a non-zero selection, then "delete word left" typically only
        # deletes the characters within the selection range, ignoring word boundaries.
        start, end = self.selection
        if start != end:
            self.delete(start, end, maintain_selection_offset=False)
            return

        cursor_row, cursor_column = end

        # Check the current line for a word boundary
        line = self.document[cursor_row][:cursor_column]
        matches = list(re.finditer(self.word_pattern, line))

        if matches:
            # If a word boundary is found, delete the word
            from_location = (cursor_row, matches[-1].start())
        elif cursor_row > 0:
            # If no word boundary is found, and we're not on the first line, delete to the end of the previous line
            from_location = (cursor_row - 1, len(self.document[cursor_row - 1]))
        else:
            # If we're already on the first line and no word boundary is found, delete to the start of the line
            from_location = (cursor_row, 0)

        self.delete(from_location, self.selection.end, maintain_selection_offset=False)

    def action_delete_word_right(self) -> None:
        """Deletes the word to the right of the cursor and keeps the cursor at the same location."""
        if self.cursor_at_end_of_document:
            return

        start, end = self.selection
        if start != end:
            self.delete(start, end, maintain_selection_offset=False)
            return

        cursor_row, cursor_column = end

        # Check the current line for a word boundary
        line = self.document[cursor_row][cursor_column:]
        matches = list(re.finditer(self.word_pattern, line))

        if matches:
            # If a word boundary is found, delete the word
            to_location = (cursor_row, cursor_column + matches[0].end())
        elif cursor_row < self.document.line_count - 1:
            # If no word boundary is found, and we're not on the last line, delete to the start of the next line
            to_location = (cursor_row + 1, 0)
        else:
            # If we're already on the last line and no word boundary is found, delete to the end of the line
            to_location = (cursor_row, len(self.document[cursor_row]))

        self.delete(end, to_location, maintain_selection_offset=False)


@dataclass
class Edit:
    """Implements the Undoable protocol to replace text at some range within a document."""

    text: str
    """The text to insert. An empty string is equivalent to deletion."""
    from_location: Location
    """The start location of the insert."""
    to_location: Location
    """The end location of the insert"""
    maintain_selection_offset: bool
    """If True, the selection will maintain its offset to the replacement range."""
    _replace_result: EditResult | None = field(init=False, default=None)
    """Contains data relating to the replace operation."""
    _updated_selection: Location | None = field(init=False, default=None)
    """Where the selection should move to after the replace happens."""

    def do(self, text_area: TextArea) -> EditResult:
        """Perform the edit operation.

        Args:
            text_area: The TextArea to perform the edit on.

        Returns:
            An EditResult containing information about the replace operation.
        """
        text = self.text

        edit_from = self.from_location
        edit_to = self.to_location

        # This code is mostly handling how we adjust TextArea.selection
        # when an edit is made to the document programmatically.
        # We want a user who is typing away to maintain their relative
        # position in the document even if an insert happens before
        # their cursor position.

        edit_top, edit_bottom = _sort_ascending(edit_from, edit_to)
        edit_bottom_row, edit_bottom_column = edit_bottom

        selection_start, selection_end = text_area.selection
        selection_start_row, selection_start_column = selection_start
        selection_end_row, selection_end_column = selection_end

        replace_result = text_area.document.replace_range(edit_from, edit_to, text)
        self._replace_result = replace_result

        new_edit_to_row, new_edit_to_column = replace_result.end_location

        # TODO: We could maybe improve the situation where the selection
        #  and the edit range overlap with each other.
        column_offset = new_edit_to_column - edit_bottom_column
        target_selection_start_column = (
            selection_start_column + column_offset
            if edit_bottom_row == selection_start_row
            else selection_start_column
        )
        target_selection_end_column = (
            selection_end_column + column_offset
            if edit_bottom_row == selection_end_row
            else selection_end_column
        )

        row_offset = new_edit_to_row - edit_bottom_row
        target_selection_start_row = selection_start_row + row_offset
        target_selection_end_row = selection_end_row + row_offset

        if self.maintain_selection_offset:
            self._updated_selection = Selection(
                start=(target_selection_start_row, target_selection_start_column),
                end=(target_selection_end_row, target_selection_end_column),
            )
        else:
            self._updated_selection = Selection.cursor(replace_result.end_location)

        return replace_result

    def undo(self, text_area: TextArea) -> EditResult:
        """Undo the Replace operation.

        Args:
            text_area: The TextArea to undo the insert operation on.
        """

    def after(self, text_area: TextArea) -> None:
        """Possibly update the cursor location after the widget has been refreshed.

        Args:
            text_area: The TextArea this operation was performed on.
        """
        text_area.selection = self._updated_selection


@runtime_checkable
class Undoable(Protocol):
    """Protocol for actions performed in the text editor which can be done and undone.

    These are typically actions which affect the document (e.g. inserting and deleting
    text), but they can really be anything.

    To perform an edit operation, pass the Edit to `TextArea.edit()`"""

    def do(self, text_area: TextArea) -> object | None:
        """Do the action."""

    def undo(self, text_area: TextArea) -> object | None:
        """Undo the action."""
