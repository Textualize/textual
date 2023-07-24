from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, NamedTuple

from rich.style import Style
from rich.text import Text
from tree_sitter import Language, Parser, Tree
from tree_sitter.binding import Query

from textual import events, log
from textual._cells import cell_len
from textual._types import Protocol, runtime_checkable
from textual.binding import Binding
from textual.geometry import Offset, Region, Size, Spacing, clamp
from textual.reactive import Reactive, reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip

TREE_SITTER_PATH = Path(__file__) / "../../../../tree-sitter/"
LANGUAGES_PATH = TREE_SITTER_PATH / "textual-languages.so"

# TODO - remove hardcoded python.scm highlight query file
HIGHLIGHTS_PATH = TREE_SITTER_PATH / "highlights/python.scm"

# TODO - temporary proof of concept approach
HIGHLIGHT_STYLES = {
    "string": Style(color="#E6DB74"),
    "string.documentation": Style(color="yellow"),
    "comment": Style(color="#75715E"),
    "keyword": Style(color="#F92672"),
    "include": Style(color="#F92672"),
    "keyword.function": Style(color="#F92672"),
    "keyword.return": Style(color="#F92672"),
    "conditional": Style(color="#F92672"),
    "number": Style(color="#AE81FF"),
    "class": Style(color="#A6E22E"),
    "function": Style(color="#A6E22E"),
    "function.call": Style(color="#A6E22E"),
    "method": Style(color="#A6E22E"),
    "method.call": Style(color="#A6E22E"),
    # "constant": Style(color="#AE81FF"),
    "variable": Style(color="white"),
    "parameter": Style(color="cyan"),
    "type": Style(color="cyan"),
    "escape": Style(bgcolor="magenta"),
}


class Highlight(NamedTuple):
    """A range to highlight within a single line"""

    start_column: int | None
    end_column: int | None
    highlight_name: str | None


class Selection(NamedTuple):
    """A range of characters within a document from a start point to the end point.
    The position of the cursor is always considered to be the `end` point of the selection.
    The selection is inclusive of the minimum point and exclusive of the maximum point.
    """

    start: tuple[int, int] = (0, 0)
    end: tuple[int, int] = (0, 0)

    @classmethod
    def cursor(cls, position: tuple[int, int]) -> "Selection":
        """Create a Selection with the same start and end point."""
        return cls(position, position)

    @property
    def is_empty(self) -> bool:
        """Return True if the selection has 0 width, i.e. it's just a cursor."""
        start, end = self
        return start == end

    def range(self) -> tuple[tuple[int, int], tuple[int, int]]:
        start, end = self
        return _fix_direction(start, end)


@runtime_checkable
class Edit(Protocol):
    """Protocol for actions performed in the text editor that can be done and undone."""

    def do(self, editor: TextArea) -> object | None:
        """Do the action."""

    def undo(self, editor: TextArea) -> object | None:
        """Undo the action."""


class Insert(NamedTuple):
    """Implements the Edit protocol for inserting text at some position."""

    text: str
    from_position: tuple[int, int]
    to_position: tuple[int, int]
    move_cursor: bool = True

    def do(self, editor: TextArea) -> None:
        if self.text:
            editor._insert_text_range(
                self.text, self.from_position, self.to_position, self.move_cursor
            )

    def undo(self, editor: TextArea) -> None:
        """Undo the action."""


@dataclass
class Delete:
    """Performs a delete operation."""

    from_position: tuple[int, int]
    """The position to delete from (inclusive)."""

    to_position: tuple[int, int]
    """The position to delete to (exclusive)."""

    cursor_destination: tuple[int, int] | None = None
    """Where to move the cursor to after the deletion."""

    def do(self, editor: TextArea) -> None:
        """Do the action."""
        self.deleted_text = editor._delete_range(
            self.from_position, self.to_position, self.cursor_destination
        )
        return self.deleted_text

    def undo(self, editor: TextArea) -> None:
        """Undo the action."""

    def __rich_repr__(self):
        yield "from_position", self.from_position
        yield "to_position", self.to_position
        if hasattr(self, "deleted_text"):
            yield "deleted_text", self.deleted_text


class TextArea(ScrollView, can_focus=True):
    DEFAULT_CSS = """\
$editor-active-line-bg: white 8%;
TextArea {
    background: $panel;
}
TextArea > .text-area--active-line {
    background: $editor-active-line-bg;
}
TextArea > .text-area--active-line-gutter {
    color: $text;
    background: $editor-active-line-bg;
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
        Binding("shift+up", "cursor_up_select", "cursor up select", show=False),
        Binding("down", "cursor_down", "cursor down", show=False),
        Binding("shift+down", "cursor_down_select", "cursor down select", show=False),
        Binding("left", "cursor_left", "cursor left", show=False),
        Binding("shift+left", "cursor_left_select", "cursor left select", show=False),
        Binding("ctrl+left", "cursor_left_word", "cursor left word", show=False),
        Binding("right", "cursor_right", "cursor right", show=False),
        Binding(
            "shift+right", "cursor_right_select", "cursor right select", show=False
        ),
        Binding("ctrl+right", "cursor_right_word", "cursor right word", show=False),
        Binding("home,ctrl+a", "cursor_line_start", "cursor line start", show=False),
        Binding("end,ctrl+e", "cursor_line_end", "cursor line end", show=False),
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
    selection: Reactive[Selection] = reactive(Selection(), always_update=True)
    """The cursor position (zero-based line_index, offset)."""
    show_line_numbers: Reactive[bool] = reactive(True)
    """True to show line number gutter, otherwise False."""
    _document_size: Reactive[Size] = reactive(Size(), init=False)
    """Tracks the width of the document. Used to update virtual size. Do not
    update virtual size directly."""

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        # --- Core editor data
        self.document_lines: list[str] = []
        """Each string in this list represents a line in the document. Includes new line characters."""

        self._highlights: dict[int, list[Highlight]] = defaultdict(list)
        """Mapping line numbers to the set of cached highlights for that line."""

        self._highlights_query: str | None = None
        """The string containing the tree-sitter AST query used for syntax highlighting."""

        self._last_intentional_cell_width: int = 0
        """Tracks the last column (measured in terms of cell length, since we care here about where
         the cursor visually moves more than the logical characters) the user explicitly navigated to so that we can reset
        to it whenever possible."""

        self._word_pattern = re.compile(r"(?<=\W)(?=\w)|(?<=\w)(?=\W)")
        """Compiled regular expression for what we consider to be a 'word'."""

        self._undo_stack: list[Edit] = []
        """A stack (the end of the list is the top of the stack) for tracking edits."""

        self._selecting = False
        """True if we're currently selecting text, otherwise False."""

        # --- Abstract syntax tree and related parsing machinery
        self._language: Language | None = None
        self._parser: Parser | None = None
        """The tree-sitter parser which extracts the syntax tree from the document."""
        self._syntax_tree: Tree | None = None
        """The tree-sitter Tree (AST) built from the document."""

    def watch_language(self, new_language: str | None) -> None:
        """Update the language used in AST parsing.

        When the language reactive string is updated, fetch the Language definition
        from our tree-sitter library file. If the language reactive is set to None,
        then the no parser is used."""
        log.debug(f"updating editor language to {new_language!r}")
        if new_language:
            self._language = Language(LANGUAGES_PATH.resolve(), new_language)
            parser = Parser()
            self._parser = parser
            self._parser.set_language(self._language)
            self._syntax_tree = self._build_ast(parser)
            self._highlights_query = Path(HIGHLIGHTS_PATH.resolve()).read_text()

        log.debug(f"parser set to {self._parser}")

    def watch__document_size(self, size: Size) -> None:
        log.debug(f"document size set to {size!r} ")
        document_width, document_height = size
        self.virtual_size = Size(document_width + self.gutter_width, document_height)

    def _build_ast(
        self,
        parser: Parser,
    ) -> Tree | None:
        """Fully parse the document and build the abstract syntax tree for it.

        Returns None if there's no parser available (e.g. when no language is selected).
        """
        if parser:
            return parser.parse(self._read_callable)
        else:
            return None

    def _read_callable(self, byte_offset: int, point: tuple[int, int]) -> str:
        row, column = point
        lines = self.document_lines
        row_out_of_bounds = row >= len(lines)
        column_out_of_bounds = not row_out_of_bounds and column > len(lines[row])
        if row_out_of_bounds or column_out_of_bounds:
            return_value = None
        elif column == len(lines[row]) and row < len(lines):
            return_value = "\n".encode("utf8")
        else:
            return_value = lines[row][column].encode("utf8")
        # print(f"(point={point!r}) (offset={byte_offset!r}) {return_value!r}")
        return return_value

    def load_text(self, text: str) -> None:
        """Load text from a string into the editor."""
        lines = text.splitlines(keepends=False)
        if text[-1] == "\n":
            lines.append("")
        self.load_lines(lines)

    def load_lines(self, lines: list[str]) -> None:
        """Load text from a list of lines into the editor.

        This will replace any previously loaded lines."""
        self.document_lines = lines
        self._document_size = self._get_document_size(lines)
        if self._parser is not None:
            self._syntax_tree = self._build_ast(self._parser)
            self._prepare_highlights()

        log.debug(f"loaded text. parser = {self._parser} ast = {self._syntax_tree}")

    def clear(self) -> None:
        # TODO: Perform a delete on the whole document.
        self.load_text("")

    # --- Methods for measuring things (e.g. virtual sizes)
    def _get_document_size(self, document_lines: list[str]) -> Size:
        """Return the virtual size of the document - the document only
        refers to the area in which the cursor can move. It does not, for
        example, include the width of the gutter."""
        text_width = max(cell_len(line) for line in document_lines)
        height = len(document_lines)
        # We add one to the text width to leave a space for the cursor, since it
        # can rest at the end of a line where there isn't yet any character.
        # Similarly, the cursor can rest below the bottom line of text, where
        # a line doesn't currently exist.
        return Size(text_width + 1, height)

    def _refresh_size(self) -> None:
        self._document_size = self._get_document_size(self.document_lines)

    def render_line(self, widget_y: int) -> Strip:
        document_lines = self.document_lines

        document_y = round(self.scroll_y + widget_y)
        out_of_bounds = document_y >= len(document_lines)
        if out_of_bounds:
            return Strip.blank(self.size.width)

        line_string = document_lines[document_y].replace("\n", "").replace("\r", "")
        line_text = Text(f"{line_string} ", end="", tab_size=4)
        line_text.set_length(self.virtual_size.width)

        # Apply highlighting
        null_style = Style.null()
        if self._highlights:
            highlights = self._highlights[document_y]
            for start, end, highlight_name in highlights:
                node_style = HIGHLIGHT_STYLES.get(highlight_name, null_style)
                line_text.stylize(node_style, start, end)

        start, end = self.selection
        end_row, end_column = end

        selection_style = self.get_component_rich_style("text-area--selection")

        # Start and end can be before or after each other, depending on the direction
        # you move the cursor during selecting text, but the "top" of the selection
        # is always before the "bottom" of the selection.
        selection_top = min(start, end)
        selection_bottom = max(start, end)
        selection_top_row, selection_top_column = selection_top
        selection_bottom_row, selection_bottom_column = selection_bottom

        if start != end and selection_top_row <= document_y <= selection_bottom_row:
            # If this row is part of the selection
            if document_y == selection_top_row == selection_bottom_row:
                # Selection within a single line
                line_text.stylize_before(
                    selection_style,
                    start=selection_top_column,
                    end=selection_bottom_column,
                )
            else:
                # Selection spanning multiple lines
                if document_y == selection_top_row:
                    line_text.stylize_before(
                        selection_style,
                        start=selection_top_column,
                        end=len(line_string),
                    )
                elif document_y == selection_bottom_row:
                    line_text.stylize_before(
                        selection_style, end=selection_bottom_column
                    )
                else:
                    line_text.stylize_before(selection_style, end=len(line_string))

        # Show the cursor and the selection
        if end_row == document_y:
            cursor_style = self.get_component_rich_style("text-area--cursor")
            line_text.stylize(cursor_style, end_column, end_column + 1)
            active_line_style = self.get_component_rich_style("text-area--active-line")
            line_text.stylize_before(active_line_style)

        # Show the gutter
        if self.show_line_numbers:
            if end_row == document_y:
                gutter_style = self.get_component_rich_style(
                    "text-area--active-line-gutter"
                )
            else:
                gutter_style = self.get_component_rich_style("text-area--gutter")

            gutter_width_no_margin = self.gutter_width - 2
            gutter = Text(
                f"{document_y + 1:>{gutter_width_no_margin}}  ",
                style=gutter_style,
                end="",
            )
        else:
            gutter = Text("", end="")

        gutter_segments = self.app.console.render(gutter)
        text_segments = self.app.console.render(
            line_text, self.app.console.options.update_width(self.virtual_size.width)
        )

        virtual_width, virtual_height = self.virtual_size
        text_crop_start = int(self.scroll_x)
        text_crop_end = text_crop_start + virtual_width

        gutter_strip = Strip(gutter_segments)
        text_strip = Strip(text_segments).crop(text_crop_start, text_crop_end)

        strip = Strip.join([gutter_strip, text_strip]).simplify()

        return strip

    @property
    def gutter_width(self) -> int:
        # The longest number in the gutter plus two extra characters: `│ `.
        gutter_margin = 2
        gutter_longest_number = (
            len(str(len(self.document_lines) + 1)) + gutter_margin
            if self.show_line_numbers
            else 0
        )
        return gutter_longest_number

    # --- Syntax highlighting
    def _prepare_highlights(
        self,
        start_point: tuple[int, int] | None = None,
        end_point: tuple[int, int] = None,
    ) -> None:
        # TODO - we're ignoring get changed ranges for now. Either I'm misunderstanding
        #  it or I've made a mistake somewhere with AST editing.

        highlights = self._highlights
        query: Query = self._language.query(self._highlights_query)

        log.debug(f"capturing nodes in range {start_point!r} -> {end_point!r}")

        captures_kwargs = {}
        if start_point is not None:
            captures_kwargs["start_point"] = start_point
        if end_point is not None:
            captures_kwargs["end_point"] = end_point

        captures = query.captures(self._syntax_tree.root_node, **captures_kwargs)

        highlight_updates: dict[int, list[Highlight]] = defaultdict(list)
        for capture in captures:
            node, highlight_name = capture
            node_start_row, node_start_column = node.start_point
            node_end_row, node_end_column = node.end_point

            if node_start_row == node_end_row:
                highlight = Highlight(
                    node_start_column, node_end_column, highlight_name
                )
                highlight_updates[node_start_row].append(highlight)
            else:
                # Add the first line
                highlight_updates[node_start_row].append(
                    Highlight(node_start_column, None, highlight_name)
                )
                # Add the middle lines - entire row of this node is highlighted
                for node_row in range(node_start_row + 1, node_end_row):
                    highlight_updates[node_row].append(
                        Highlight(0, None, highlight_name)
                    )

                # Add the last line
                highlight_updates[node_end_row].append(
                    Highlight(0, node_end_column, highlight_name)
                )

        for line_index, updated_highlights in highlight_updates.items():
            highlights[line_index] = updated_highlights

    def edit(self, edit: Edit) -> object | None:
        log.debug(f"performing edit {edit!r}")
        result = edit.do(self)
        self._undo_stack.append(edit)

        # TODO: Think about this...
        self._undo_stack = self._undo_stack[-20:]

        return result

    def undo(self) -> None:
        if self._undo_stack:
            action = self._undo_stack.pop()
            action.undo(self)

    # --- Lower level event/key handling
    def _on_key(self, event: events.Key) -> None:
        log.debug(f"{event!r}")
        key = event.key
        if event.is_printable or key == "tab" or key == "enter":
            if key == "tab":
                insert = "    "
            elif key == "enter":
                insert = "\n"
            else:
                insert = event.character
            event.stop()
            assert event.character is not None
            start, end = self.selection
            self.insert_text_range(insert, start, end)
            event.prevent_default()
        elif key == "shift+tab":
            self.dedent_line()
            event.stop()

    def get_target_document_location(self, offset: Offset) -> tuple[int, int]:
        if offset is None:
            return

        target_x = max(offset.x - self.gutter_width + int(self.scroll_x), 0)
        target_row = clamp(
            offset.y + int(self.scroll_y), 0, len(self.document_lines) - 1
        )
        target_column = self.cell_width_to_column_index(target_x, target_row)

        return target_row, target_column

    def _on_mouse_down(self, event: events.MouseDown) -> None:
        event.stop()
        offset = event.get_content_offset(self)
        target_row, target_column = self.get_target_document_location(offset)
        self.selection = Selection.cursor((target_row, target_column))
        log.debug(f"started selection {self.selection!r}")
        self._selecting = True

    def _on_mouse_move(self, event: events.MouseMove) -> None:
        event.stop()
        if self._selecting:
            offset = event.get_content_offset(self)
            target = self.get_target_document_location(offset)
            selection_start, _ = self.selection
            self.selection = Selection(selection_start, target)
            log.debug(f"selection updated {self.selection!r}")

    def _on_mouse_up(self, event: events.MouseUp) -> None:
        event.stop()
        self._record_last_intentional_cell_width()
        self._selecting = False

    def _on_paste(self, event: events.Paste) -> None:
        text = event.text
        if text:
            self.insert_text(text, self.selection)
        event.stop()

    def cell_width_to_column_index(self, cell_width: int, row_index: int) -> int:
        """Return the column that the cell width corresponds to on the given row."""
        total_cell_offset = 0
        line = self.document_lines[row_index]
        for column_index, character in enumerate(line):
            total_cell_offset += cell_len(character)
            if total_cell_offset >= cell_width + 1:
                return column_index
        return len(line)

    def watch_selection(self) -> None:
        self.scroll_cursor_visible()

    # --- Cursor utilities
    def scroll_cursor_visible(self):
        # The end of the selection is always considered to be position of the cursor
        # ... this is a constraint we need to enforce in code.
        row, column = self.selection.end
        text = self.active_line_text[:column]
        column_offset = cell_len(text)
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
        return self.selection.end[0] == len(self.document_lines) - 1

    @property
    def cursor_at_start_of_row(self) -> bool:
        return self.selection.end[1] == 0

    @property
    def cursor_at_end_of_row(self) -> bool:
        cursor_row, cursor_column = self.selection.end
        row_length = len(self.document_lines[cursor_row])
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
        target_column = len(self.document_lines[cursor_row])

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
            print(f"new selection = {self.selection}")

    # ------ Cursor movement actions
    def action_cursor_left(self) -> None:
        """Move the cursor one position to the left.

        If the cursor is at the left edge of the document, try to move it to
        the end of the previous line.
        """
        target = self.get_cursor_left_position()
        self.selection = Selection.cursor(target)
        self._record_last_intentional_cell_width()

    def action_cursor_left_select(self):
        """Move the end of the selection one position to the left.

        This will expand or contract the selection.
        """
        new_cursor_position = self.get_cursor_left_position()
        selection_start, selection_end = self.selection
        self.selection = Selection(selection_start, new_cursor_position)
        self._record_last_intentional_cell_width()

    def get_cursor_left_position(self) -> tuple[int, int]:
        """Get the position the cursor will move to if it moves left."""
        if self.cursor_at_start_of_document:
            return 0, 0
        cursor_row, cursor_column = self.selection.end
        length_of_row_above = len(self.document_lines[cursor_row - 1])
        target_row = cursor_row if cursor_column != 0 else cursor_row - 1
        target_column = cursor_column - 1 if cursor_column != 0 else length_of_row_above
        return target_row, target_column

    def action_cursor_right(self) -> None:
        """Move the cursor one position to the right.

        If the cursor is at the end of a line, attempt to go to the start of the next line.
        """
        target = self.get_cursor_right_position()
        self.selection = Selection.cursor(target)
        self._record_last_intentional_cell_width()

    def action_cursor_right_select(self):
        """Move the end of the selection one position to the right.

        This will expand or contract the selection.
        """
        new_cursor_position = self.get_cursor_right_position()
        selection_start, selection_end = self.selection
        self.selection = Selection(selection_start, new_cursor_position)
        self._record_last_intentional_cell_width()

    def get_cursor_right_position(self) -> tuple[int, int]:
        """Get the position the cursor will move to if it moves right."""
        if self.cursor_at_end_of_document:
            return self.selection.end
        cursor_row, cursor_column = self.selection.end
        target_row = cursor_row + 1 if self.cursor_at_end_of_row else cursor_row
        target_column = 0 if self.cursor_at_end_of_row else cursor_column + 1
        return target_row, target_column

    def action_cursor_down(self) -> None:
        """Move the cursor down one cell."""
        target = self.get_cursor_down_position()
        self.selection = Selection.cursor(target)

    def action_cursor_down_select(self) -> None:
        """Move the cursor down one cell, selecting the range between the old and new positions."""
        target = self.get_cursor_down_position()
        start, end = self.selection
        self.selection = Selection(start, target)

    def get_cursor_down_position(self):
        """Get the position the cursor will move to if it moves down."""
        cursor_row, cursor_column = self.selection.end
        if self.cursor_at_last_row:
            return cursor_row, len(self.document_lines[cursor_row])

        target_row = min(len(self.document_lines) - 1, cursor_row + 1)
        # Attempt to snap last intentional cell length
        target_column = self.cell_width_to_column_index(
            self._last_intentional_cell_width, target_row
        )
        target_column = clamp(target_column, 0, len(self.document_lines[target_row]))
        return target_row, target_column

    def action_cursor_up(self) -> None:
        """Move the cursor up one cell."""
        target = self.get_cursor_up_position()
        self.selection = Selection.cursor(target)

    def action_cursor_up_select(self) -> None:
        """Move the cursor up one cell, selecting the range between the old and new positions."""
        target = self.get_cursor_up_position()
        start, end = self.selection
        self.selection = Selection(start, target)

    def get_cursor_up_position(self) -> tuple[int, int]:
        """Get the position the cursor will move to if it moves up."""
        if self.cursor_at_first_row:
            return 0, 0
        cursor_row, cursor_column = self.selection.end
        target_row = max(0, cursor_row - 1)
        # Attempt to snap last intentional cell length
        target_column = self.cell_width_to_column_index(
            self._last_intentional_cell_width, target_row
        )
        target_column = clamp(target_column, 0, len(self.document_lines[target_row]))
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
        line = self.document_lines[cursor_row][:cursor_column]
        matches = list(re.finditer(self._word_pattern, line))

        if matches:
            # If a word boundary is found, move the cursor there
            cursor_column = matches[-1].start()
        elif cursor_row > 0:
            # If no word boundary is found and we're not on the first line, move to the end of the previous line
            cursor_row -= 1
            cursor_column = len(self.document_lines[cursor_row])
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
        line = self.document_lines[cursor_row][cursor_column:]
        matches = list(re.finditer(self._word_pattern, line))

        if matches:
            # If a word boundary is found, move the cursor there
            cursor_column += matches[0].end()
        elif cursor_row < len(self.document_lines) - 1:
            # If no word boundary is found and we're not on the last line, move to the start of the next line
            cursor_row += 1
            cursor_column = 0
        else:
            # If we're already on the last line and no word boundary is found, move to the end of the line
            cursor_column = len(self.document_lines[cursor_row])

        self.selection = Selection.cursor((cursor_row, cursor_column))
        self._record_last_intentional_cell_width()

    @property
    def active_line_text(self) -> str:
        # TODO - consider empty documents
        return self.document_lines[self.selection.end[0]]

    def get_column_cell_width(self, row: int, column: int) -> int:
        """Given a row and column index within the editor, return the cell offset
        of the column from the start of the row (the left edge of the editor content area).
        """
        line = self.document_lines[row]
        return cell_len(line[:column])

    def _record_last_intentional_cell_width(self) -> None:
        row, column = self.selection.end
        column_cell_length = self.get_column_cell_width(row, column)
        self._last_intentional_cell_width = column_cell_length

    # --- Editor operations
    def insert_text(
        self, text: str, position: tuple[int, int], move_cursor: bool = True
    ) -> None:
        self.edit(Insert(text, position, position, move_cursor))

    def insert_text_range(
        self,
        text: str,
        from_position: tuple[int, int],
        to_position: tuple[int, int],
        move_cursor: bool = True,
    ):
        self.edit(Insert(text, from_position, to_position, move_cursor))

    def _insert_text_range(
        self,
        text: str,
        from_position: tuple[int, int],
        to_position: tuple[int, int],
        move_cursor: bool = True,
    ) -> None:
        """Insert text at a given range and move the cursor to the end of the inserted text."""

        inserted_text = text
        lines = self.document_lines

        from_row, from_column = from_position
        to_row, to_column = to_position

        if from_position > to_position:
            from_row, from_column, to_row, to_column = (
                to_row,
                to_column,
                from_row,
                from_column,
            )

        insert_lines = inserted_text.splitlines()
        if inserted_text.endswith("\n"):
            # Special case where a single newline character is inserted.
            insert_lines.append("")

        before_selection = lines[from_row][:from_column]
        after_selection = lines[to_row][to_column:]

        insert_lines[0] = before_selection + insert_lines[0]
        destination_column = len(insert_lines[-1])
        insert_lines[-1] = insert_lines[-1] + after_selection
        lines[from_row : to_row + 1] = insert_lines
        destination_row = from_row + len(insert_lines) - 1

        cursor_destination = (destination_row, destination_column)

        start_byte = self._position_to_byte_offset(from_position)
        if self._syntax_tree is not None:
            self._syntax_tree.edit(
                start_byte=start_byte,
                old_end_byte=self._position_to_byte_offset(to_position),
                new_end_byte=start_byte + len(inserted_text),
                start_point=from_position,
                old_end_point=to_position,
                new_end_point=cursor_destination,
            )
            self._syntax_tree = self._parser.parse(
                self._read_callable, self._syntax_tree
            )
            self._prepare_highlights()
        self._refresh_size()
        if move_cursor:
            self.selection = Selection.cursor(cursor_destination)

    def _position_to_byte_offset(self, position: tuple[int, int]) -> int:
        """Given a document coordinate, return the byte offset of that coordinate."""

        # TODO - this assumes all line endings are a single byte `\n`
        lines = self.document_lines
        row, column = position
        lines_above = lines[:row]
        bytes_lines_above = sum(len(line.encode("utf-8")) + 1 for line in lines_above)
        bytes_this_line_left_of_cursor = len(lines[row][:column].encode("utf-8"))
        return bytes_lines_above + bytes_this_line_left_of_cursor

    def dedent_line(self) -> None:
        """Reduces the indentation of the current line by one level.

        A dedent is simply a Delete operation on some amount of whitespace
        which may exist at the start of a line.
        """
        cursor_row, cursor_column = self.selection.end

        # Define one level of indentation as four spaces
        indent_level = " " * 4

        current_line = self.document_lines[cursor_row]

        # If the line is indented, reduce the indentation
        # TODO - if the line is less than the indent level we should just dedent as far as possible.
        if current_line.startswith(indent_level):
            self.document_lines[cursor_row] = current_line[len(indent_level) :]

        if cursor_column > len(current_line):
            self.selection = Selection.cursor((cursor_row, len(current_line)))

        self._refresh_size()
        self.refresh()

    def delete_range(
        self,
        from_position: tuple[int, int],
        to_position: tuple[int, int],
        cursor_destination: tuple[int, int] | None = None,
    ) -> str:
        top, bottom = _fix_direction(from_position, to_position)
        print(f"top and bottom: {top, bottom}")
        return self.edit(Delete(top, bottom, cursor_destination))

    def _delete_range(
        self,
        from_position: tuple[int, int],
        to_position: tuple[int, int],
        cursor_destination: tuple[int, int] | None,
    ) -> str:
        """Delete text between `from_position` and `to_position`.

        `from_position` is inclusive. The `to_position` is exclusive.

        Returns:
            A string containing the deleted text.
        """
        from_row, from_column = from_position
        to_row, to_column = to_position

        start_byte = self._position_to_byte_offset(from_position)
        old_end_byte = self._position_to_byte_offset(to_position)

        lines = self.document_lines

        # If the range is within a single line
        if from_row == to_row:
            line = lines[from_row]
            deleted_text = line[from_column:to_column]
            lines[from_row] = line[:from_column] + line[to_column:]
        else:
            # The range spans multiple lines
            start_line = lines[from_row]
            end_line = lines[to_row]

            deleted_text = start_line[from_column:] + "\n"
            for row in range(from_row + 1, to_row):
                deleted_text += lines[row] + "\n"

            deleted_text += end_line[:to_column]
            if to_column == len(end_line):
                deleted_text += "\n"

            # Update the lines at the start and end of the range
            lines[from_row] = start_line[:from_column] + end_line[to_column:]

            # Delete the lines in between
            del lines[from_row + 1 : to_row + 1]

        if self._syntax_tree is not None:
            self._syntax_tree.edit(
                start_byte=start_byte,
                old_end_byte=old_end_byte,
                new_end_byte=old_end_byte - len(deleted_text),
                start_point=from_position,
                old_end_point=to_position,
                new_end_point=from_position,
            )
            self._syntax_tree = self._parser.parse(
                self._read_callable, self._syntax_tree
            )
            self._prepare_highlights()

        self._refresh_size()

        if cursor_destination is not None:
            self.selection = Selection.cursor(cursor_destination)
        else:
            # Move the cursor to the start of the deleted range
            self.selection = Selection.cursor((from_row, from_column))

        return deleted_text

    def action_delete_left(self) -> None:
        """Deletes the character to the left of the cursor and updates the cursor position."""

        selection = self.selection
        empty = selection.is_empty

        if self.cursor_at_start_of_document and empty:
            return

        start, end = selection
        end_row, end_column = end

        if empty:
            if self.cursor_at_start_of_row:
                end = (end_row - 1, len(self.document_lines[end_row - 1]))
            else:
                end = (end_row, end_column - 1)

        self.delete_range(start, end)

    def action_delete_right(self) -> None:
        """Deletes the character to the right of the cursor and keeps the cursor at the same position."""
        if self.cursor_at_end_of_document:
            return

        start, end = self.selection
        end_row, end_column = end

        if self.cursor_at_end_of_row:
            to_position = (end_row + 1, 0)
        else:
            to_position = (end_row, end_column + 1)

        self.delete_range(start, to_position)

    def action_delete_line(self) -> None:
        """Deletes the lines which intersect with the selection."""
        start, end = self.selection
        start_row, start_column = start
        end_row, end_column = end

        from_position = (start_row, 0)
        to_position = (end_row + 1, 0)

        self.delete_range(from_position, to_position)

    def action_delete_to_start_of_line(self) -> None:
        """Deletes from the cursor position to the start of the line."""
        from_position = self.selection.end
        cursor_row, cursor_column = from_position
        to_position = (cursor_row, 0)
        self.delete_range(from_position, to_position)

    def action_delete_to_end_of_line(self) -> None:
        """Deletes from the cursor position to the end of the line."""
        from_position = self.selection.end
        cursor_row, cursor_column = from_position
        to_position = (cursor_row, len(self.document_lines[cursor_row]))
        self.delete_range(from_position, to_position)

    def action_delete_word_left(self) -> None:
        """Deletes the word to the left of the cursor and updates the cursor position."""
        if self.cursor_at_start_of_document:
            return

        # If there's a non-zero selection, then "delete word left" typically only
        # deletes the characters within the selection range, ignoring word boundaries.
        start, end = self.selection
        if start != end:
            self.delete_range(start, end)

        cursor_row, cursor_column = end

        # Check the current line for a word boundary
        line = self.document_lines[cursor_row][:cursor_column]
        matches = list(re.finditer(self._word_pattern, line))

        if matches:
            # If a word boundary is found, delete the word
            from_position = (cursor_row, matches[-1].start())
        elif cursor_row > 0:
            # If no word boundary is found, and we're not on the first line, delete to the end of the previous line
            from_position = (cursor_row - 1, len(self.document_lines[cursor_row - 1]))
        else:
            # If we're already on the first line and no word boundary is found, delete to the start of the line
            from_position = (cursor_row, 0)

        self.delete_range(from_position, self.selection.end)

    def action_delete_word_right(self) -> None:
        """Deletes the word to the right of the cursor and keeps the cursor at the same position."""
        if self.cursor_at_end_of_document:
            return

        start, end = self.selection
        if start != end:
            self.delete_range(start, end)

        cursor_row, cursor_column = end

        # Check the current line for a word boundary
        line = self.document_lines[cursor_row][cursor_column:]
        matches = list(re.finditer(self._word_pattern, line))

        if matches:
            # If a word boundary is found, delete the word
            to_position = (cursor_row, cursor_column + matches[0].end())
        elif cursor_row < len(self.document_lines) - 1:
            # If no word boundary is found, and we're not on the last line, delete to the start of the next line
            to_position = (cursor_row + 1, 0)
        else:
            # If we're already on the last line and no word boundary is found, delete to the end of the line
            to_position = (cursor_row, len(self.document_lines[cursor_row]))

        self.delete_range(end, to_position)

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
        highlight_cache_key_count: int
        highlight_cache_total_size: int
        highlight_cache_current_row_size: int
        highlight_cache_current_row: list[Highlight]

    def debug_state(self) -> "EditorDebug":
        return self.EditorDebug(
            cursor=self.selection,
            language=self.language,
            document_size=self._document_size,
            virtual_size=self.virtual_size,
            scroll=self.scroll_offset,
            undo_stack=list(reversed(self._undo_stack)),
            # tree_sexp=self._syntax_tree.root_node.sexp(),
            tree_sexp="",
            active_line_text=repr(self.active_line_text),
            active_line_cell_len=cell_len(self.active_line_text),
            highlight_cache_key_count=len(self._highlights),
            highlight_cache_total_size=sum(
                len(highlights) for key, highlights in self._highlights.items()
            ),
            highlight_cache_current_row_size=len(
                self._highlights[self.selection.end[0]]
            ),
            highlight_cache_current_row=self._highlights[self.selection.end[0]],
        )


def _fix_direction(
    start: tuple[int, int], end: tuple[int, int]
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Given a range, return a new range (x, y) such
    that x <= y which covers the same characters."""
    if start > end:
        return end, start
    return start, end


def traverse_tree(cursor):
    reached_root = False
    while reached_root == False:
        yield cursor.node

        if cursor.goto_first_child():
            continue

        if cursor.goto_next_sibling():
            continue

        retracing = True
        while retracing:
            if not cursor.goto_parent():
                retracing = False
                reached_root = True

            if cursor.goto_next_sibling():
                retracing = False


# if __name__ == "__main__":
#     language = Language(LANGUAGES_PATH.resolve(), "python")
#     parser = Parser()
#     parser.set_language(language)
#
#     CODE = """\
#     from textual.app import App
#
#
#     class ScreenApp(App):
#         def on_mount(self) -> None:
#             self.screen.styles.background = "darkblue"
#             self.screen.styles.border = ("heavy", "white")
#
#
#     if __name__ == "__main__":
#         app = ScreenApp()
#         app.run()
#     """
#
#     document_lines = CODE.splitlines(keepends=False)
#
#     def read_callable(byte_offset, point):
#         row, column = point
#         if row >= len(document_lines) or column >= len(document_lines[row]):
#             return None
#         return document_lines[row][column:].encode("utf8")
#
#     tree = parser.parse(bytes(CODE, "utf-8"))
#
#     print(list(traverse_tree(tree.walk())))
