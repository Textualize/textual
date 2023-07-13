from __future__ import annotations

import os
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Iterable, NamedTuple

from rich.cells import get_character_cell_size
from rich.style import Style
from rich.text import Text
from tree_sitter import Language, Node, Parser, Tree
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


@runtime_checkable
class Edit(Protocol):
    """Protocol for actions performed in the text editor that can be done and undone."""

    def do(self, editor: TextEditor) -> None:
        """Do the action."""

    def undo(self, editor: TextEditor) -> None:
        """Undo the action."""


class Insert(NamedTuple):
    """Implements the Edit protocol for inserting text at some position."""

    text: str
    position: tuple[int, int]
    move_cursor: bool = True

    def do(self, editor: TextEditor) -> None:
        editor._insert_text(self.text, self.position, self.move_cursor)

    def undo(self, editor: TextEditor) -> None:
        """Undo the action."""


@dataclass
class Delete:
    from_position: tuple[int, int]
    to_position: tuple[int, int]
    cursor_destination: tuple[int, int] | None = None

    def do(self, editor: TextEditor) -> None:
        """Do the action."""
        self.deleted_text = editor._delete_range(
            self.from_position, self.to_position, self.cursor_destination
        )

    def undo(self, editor: TextEditor) -> None:
        """Undo the action."""

    def __rich_repr__(self):
        yield "from_position", self.from_position
        yield "to_position", self.to_position
        if hasattr(self, "deleted_text"):
            yield "deleted_text", self.deleted_text


class TextEditor(ScrollView, can_focus=True):
    DEFAULT_CSS = """\
$editor-active-line-bg: white 8%;

TextEditor > .text-editor--active-line {
    background: $editor-active-line-bg;
}
TextEditor > .text-editor--active-line-gutter {
    color: $text;
    background: $editor-active-line-bg;
}
TextEditor > .text-editor--gutter {
    color: $text-muted 40%;
}
TextEditor > .text-editor--cursor {
    color: $text;
    background: white 80%;
}
"""

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "text-editor--active-line",
        "text-editor--active-line-gutter",
        "text-editor--gutter",
        "text-editor--cursor",
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
        Binding("backspace", "delete_left", "delete left", show=False),
        Binding("ctrl+d", "delete_right", "delete right", show=False),
        Binding("ctrl+x", "delete_line", "delete line", show=False),
        Binding(
            "ctrl+u", "delete_to_start_of_line", "delete to line start", show=False
        ),
        Binding("ctrl+k", "delete_to_end_of_line", "delete to line end", show=False),
        # Debugging bindings
        Binding("ctrl+s", "print_highlight_cache", "[debug] Print highlight cache"),
        Binding("ctrl+l", "print_line_cache", "[debug] Print line cache"),
    ]

    language: Reactive[str | None] = reactive(None)
    """The language to use for syntax highlighting (via tree-sitter)."""
    cursor_position: Reactive[tuple[int, int]] = reactive((0, 0), always_update=True)
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

        self._last_intentional_column: int = 0
        """Tracks the last column the user explicitly navigated to so that we can reset
        to it whenever possible."""

        self._word_pattern = re.compile(r"(?<=\W)(?=\w)|(?<=\w)(?=\W)")
        """Compiled regular expression for what we consider to be a 'word'."""

        self._undo_stack: list[Edit] = []
        """A stack (the end of the list is the top of the stack) for tracking edits."""

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
        if new_language:
            self._language = Language(LANGUAGES_PATH.resolve(), new_language)
            parser = Parser()
            self._parser = parser
            self._parser.set_language(self._language)
            self._syntax_tree = self._build_ast(parser)
            self._highlights_query = Path(HIGHLIGHTS_PATH.resolve()).read_text()
        else:
            self._syntax_tree = None

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

    def _read_callable(self, byte_offset, point):
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
        """Load text from a list of lines into the editor."""
        self.document_lines = lines

        # TODO Offer maximum line width and wrap if needed
        self._document_size = self._get_document_size(lines)

        # TODO - clear caches
        if self._parser is not None:
            self._syntax_tree = self._build_ast(self._parser)
            self._prepare_highlights()

        log.debug(f"loaded text. parser = {self._parser} ast = {self._syntax_tree}")

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

        # Show the cursor
        cursor_row, cursor_column = self.cursor_position
        if cursor_row == document_y:
            cursor_style = self.get_component_rich_style("text-editor--cursor")
            line_text.stylize(cursor_style, cursor_column, cursor_column + 1)
            active_line_style = self.get_component_rich_style(
                "text-editor--active-line"
            )
            line_text.stylize_before(active_line_style)

        # Show the gutter
        if self.show_line_numbers:
            if cursor_row == document_y:
                gutter_style = self.get_component_rich_style(
                    "text-editor--active-line-gutter"
                )
            else:
                gutter_style = self.get_component_rich_style("text-editor--gutter")

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

    def edit(self, edit: Edit) -> None:
        log.debug(f"performing edit {edit!r}")
        edit.do(self)
        self._undo_stack.append(edit)

        # TODO: Think about this...
        self._undo_stack = self._undo_stack[-20:]

    def undo(self) -> None:
        if self._undo_stack:
            action = self._undo_stack.pop()
            action.undo(self)

    # --- Lower level event/key handling
    def _on_key(self, event: events.Key) -> None:
        log.debug(f"{event!r}")
        key = event.key
        if event.is_printable or key == "tab":
            if key == "tab":
                insert = "    "
            else:
                insert = event.character
            event.stop()
            assert event.character is not None

            self.insert_text(insert, self.cursor_position)
            event.prevent_default()
        elif key == "enter":
            self.split_line()
        elif key == "shift+tab":
            self.dedent_line()
            event.stop()

    def _on_click(self, event: events.Click) -> None:
        """Clicking the content body moves the cursor."""

        offset = event.get_content_offset(self)
        if offset is None:
            return

        event.stop()

        target_x = max(offset.x - self.gutter_width + int(self.scroll_x), 0)
        target_y = clamp(offset.y + int(self.scroll_y), 0, len(self.document_lines) - 1)

        line = self.document_lines[target_y]
        cell_offset = 0
        for index, character in enumerate(line):
            if cell_offset >= target_x:
                self.cursor_position = (target_y, index)
                break
            cell_offset += get_character_cell_size(character)
        else:
            self.cursor_position = (target_y, len(line))

        new_row, new_column = self.cursor_position
        self._last_intentional_column = new_column

    def _on_paste(self, event: events.Paste) -> None:
        text = event.text
        if text:
            self._insert_text(text, self.cursor_position)
        event.stop()

    # --- Reactive watchers and validators
    # def validate_cursor_position(self, new_position: tuple[int, int]) -> tuple[int, int]:
    #     new_row, new_column = new_position
    #     clamped_row = clamp(new_row, 0, len(self.document_lines) - 1)
    #     clamped_column = clamp(new_column, 0, len(self.document_lines[clamped_row]) - 1)
    #     return clamped_row, clamped_column

    def watch_cursor_position(
        self, old_position: tuple[int, int], new_position: tuple[int, int]
    ) -> None:
        log.debug("scrolling cursor into view")
        self.scroll_cursor_visible()

    def watch_virtual_size(self, vs):
        log.debug(f"new virtual_size = {vs!r}")

    # --- Cursor utilities
    def scroll_cursor_visible(self):
        row, column = self.cursor_position
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
        return self.cursor_position[0] == 0

    @property
    def cursor_at_last_row(self) -> bool:
        return self.cursor_position[0] == len(self.document_lines) - 1

    @property
    def cursor_at_start_of_row(self) -> bool:
        return self.cursor_position[1] == 0

    @property
    def cursor_at_end_of_row(self) -> bool:
        cursor_row, cursor_column = self.cursor_position
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

    def cursor_to_line_end(self) -> None:
        cursor_row, cursor_column = self.cursor_position
        target_column = len(self.document_lines[cursor_row])
        self.cursor_position = (cursor_row, target_column)
        self._last_intentional_column = target_column

    def cursor_to_line_start(self) -> None:
        cursor_row, cursor_column = self.cursor_position
        self.cursor_position = (cursor_row, 0)

    # ------ Cursor movement actions
    def action_cursor_left(self) -> None:
        """Move the cursor one position to the left.

        If the cursor is at the left edge of the document, try to move it to
        the end of the previous line.
        """
        if self.cursor_at_start_of_document:
            return

        cursor_row, cursor_column = self.cursor_position
        length_of_row_above = len(self.document_lines[cursor_row - 1])

        target_row = cursor_row if cursor_column != 0 else cursor_row - 1
        target_column = cursor_column - 1 if cursor_column != 0 else length_of_row_above

        self.cursor_position = (target_row, target_column)
        self._last_intentional_column = target_column

    def action_cursor_right(self) -> None:
        """Move the cursor one position to the right.

        If the cursor is at the end of a line, attempt to go to the start of the next line.
        """
        if self.cursor_at_end_of_document:
            return

        cursor_row, cursor_column = self.cursor_position

        target_row = cursor_row + 1 if self.cursor_at_end_of_row else cursor_row
        target_column = 0 if self.cursor_at_end_of_row else cursor_column + 1

        self.cursor_position = (target_row, target_column)
        self._last_intentional_column = target_column

    def action_cursor_down(self) -> None:
        """Move the cursor down one cell."""
        if self.cursor_at_last_row:
            self.cursor_to_line_end()

        cursor_row, cursor_column = self.cursor_position
        cursor_column = max(self._last_intentional_column, cursor_column)

        target_row = min(len(self.document_lines) - 1, cursor_row + 1)
        target_column = clamp(cursor_column, 0, len(self.document_lines[target_row]))

        self.cursor_position = (target_row, target_column)

    def action_cursor_up(self) -> None:
        """Move the cursor up one cell."""
        if self.cursor_at_first_row:
            self.cursor_to_line_start()

        cursor_row, cursor_column = self.cursor_position
        cursor_column = max(self._last_intentional_column, cursor_column)

        target_row = max(0, cursor_row - 1)
        target_column = clamp(cursor_column, 0, len(self.document_lines[target_row]))

        self.cursor_position = (target_row, target_column)

    def action_cursor_line_end(self) -> None:
        self.cursor_to_line_end()

    def action_cursor_line_start(self) -> None:
        self.cursor_to_line_start()

    def action_cursor_left_word(self) -> None:
        """Move the cursor left by a single word, skipping spaces."""

        if self.cursor_at_start_of_document:
            return

        cursor_row, cursor_column = self.cursor_position

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

        self.cursor_position = (cursor_row, cursor_column)
        self._last_intentional_column = cursor_column

    def action_cursor_right_word(self) -> None:
        """Move the cursor right by a single word, skipping spaces."""

        if self.cursor_at_end_of_document:
            return

        cursor_row, cursor_column = self.cursor_position

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

        self.cursor_position = (cursor_row, cursor_column)
        self._last_intentional_column = cursor_column

    @property
    def active_line_text(self) -> str:
        # TODO - consider empty documents
        return self.document_lines[self.cursor_position[0]]

    # --- Editor operations
    def insert_text(
        self, text: str, position: tuple[int, int], move_cursor: bool = True
    ) -> None:
        self.edit(Insert(text, position, move_cursor))

    def _insert_text(
        self, text: str, position: tuple[int, int], move_cursor: bool = True
    ) -> None:
        log.debug(f"insert {text!r} at {self.cursor_position!r}")

        start_byte = self._position_to_byte_offset(self.cursor_position)
        start_point = position

        target_row, target_column = position

        lines = self.document_lines

        line = lines[target_row]
        text_before_cursor = line[:target_column]
        text_after_cursor = line[target_column:]

        replacement_lines = text.splitlines(keepends=False)
        replacement_lines[0] = text_before_cursor + replacement_lines[0]
        end_column = len(replacement_lines[-1])
        replacement_lines[-1] += text_after_cursor

        self.document_lines[target_row : target_row + 1] = replacement_lines

        longest_modified_line = max(cell_len(line) for line in replacement_lines)
        document_width, document_height = self._document_size

        # The virtual width of the row is the cell length of the text in the row
        # plus 1 to accommodate for a cursor potentially "resting" at the end of the row
        insertion_width = longest_modified_line + 1

        self._refresh_size()

        if move_cursor:
            self.cursor_position = (target_row + len(replacement_lines) - 1, end_column)

        edit_args = {
            "start_byte": start_byte,
            "old_end_byte": start_byte,
            "new_end_byte": start_byte + len(text),  # TODO - what about newlines?
            "start_point": start_point,
            "old_end_point": start_point,
            "new_end_point": self.cursor_position,
        }
        log.debug(edit_args)

        # Edit the tree in place
        old_tree = self._syntax_tree
        old_tree.edit(**edit_args)
        new_tree = self._parser.parse(self._read_callable, old_tree)

        changed_ranges = old_tree.get_changed_ranges(new_tree)

        self._syntax_tree = new_tree
        log.debug(f"changed = {changed_ranges!r}")

        # Limit the range, rather arbitrarily for now.
        # Perhaps we do the incremental parsing within a window here, then have some
        # heuristic for wider parsing inside on_idle?
        scroll_y = max(0, int(self.scroll_y))

        visible_start_line = scroll_y
        height = self.region.height or len(self.document_lines) - 1
        visible_end_line = scroll_y + height

        highlight_window_leeway = 10
        start_point = (max(0, visible_start_line - highlight_window_leeway), 0)

        end_row_index = min(
            len(self.document_lines) - 1, visible_end_line + highlight_window_leeway
        )
        end_line = self.document_lines[end_row_index]
        end_point = (end_row_index, len(end_line) - 1)

        self._prepare_highlights(start_point, end_point)

    def insert_text_range(
        self, text: str, from_position: tuple[int, int], to_position: tuple[int, int]
    ) -> None:
        """Insert text at a given range and move the cursor to the end of the inserted text."""

        # If we're inserting a single newline character, this is just a split.
        # Delete the range first
        self._delete_range(from_position, to_position, None)
        if text == os.linesep:
            self.split_line(from_position)

        # Split the inserted text into lines
        lines = text.splitlines()

    def _position_to_byte_offset(self, position: tuple[int, int]) -> int:
        """Given a document coordinate, return the byte offset of that coordinate."""

        # TODO - this assumes all line endings are a single byte `\n`
        lines = self.document_lines
        row, column = position
        lines_above = lines[:row]
        bytes_lines_above = sum(len(line) + 1 for line in lines_above)
        bytes_this_line_left_of_cursor = len(lines[row][:column])
        return bytes_lines_above + bytes_this_line_left_of_cursor

    def split_line(self, position: tuple[int, int]) -> None:
        """
        Splits the current line at the cursor's position and updates the cursor position.

        This method splits the current line into two at the cursor's column position,
        effectively inserting a newline character at the cursor's position. The part of the
        line after the cursor becomes a new line below the current line. The cursor then
        moves to the start of this new line.
        """
        cursor_row, cursor_column = position

        # Get the current line's indentation (leading whitespace)
        current_line = self.document_lines[cursor_row]
        indentation = len(current_line) - len(current_line.lstrip())

        # Split the current line into two lines at the cursor position
        line_before = current_line[:cursor_column]
        line_after = current_line[cursor_column:]

        # If the line ends with ':' or '{', add additional indentation to the new line
        additional_indent = "    "  # Four spaces
        if line_before.rstrip().endswith((":", "{")):
            indentation += len(additional_indent)
        elif cursor_row < len(self.document_lines) - 1:
            # If there is a line below, match its indentation
            next_line = self.document_lines[cursor_row + 1]
            next_line_indentation = len(next_line) - len(next_line.lstrip())
            indentation = next_line_indentation

        # Add the indentation to the start of the new line
        line_after = " " * indentation + line_after

        # Update the lines in the document
        self.document_lines[cursor_row] = line_before
        self.document_lines.insert(cursor_row + 1, line_after)

        self._refresh_size()
        # Move the cursor to the start of the new line
        self.cursor_position = (cursor_row + 1, indentation)

    def dedent_line(self) -> None:
        """Reduces the indentation of the current line by one level.

        A dedent is simply a Delete operation on some amount of whitespace
        which may exist at the start of a line.
        """
        cursor_row, cursor_column = self.cursor_position

        # Define one level of indentation as four spaces
        indent_level = " " * 4

        current_line = self.document_lines[cursor_row]

        # If the line is indented, reduce the indentation
        if current_line.startswith(indent_level):
            self.document_lines[cursor_row] = current_line[len(indent_level) :]

        if cursor_column > len(current_line):
            self.cursor_position = (cursor_row, len(current_line))

        self._refresh_size()
        self.refresh()

    def _delete_range(
        self,
        from_position: tuple[int, int],
        to_position: tuple[int, int],
        cursor_destination: tuple[int, int] | None,
    ) -> str:
        """Delete text between `from_position` and `to_position`.

        Returns:
            A string containing the deleted text.
        """

        from_row, from_column = from_position
        to_row, to_column = to_position

        lines = self.document_lines

        # Ensure that from_position is before to_position
        if from_position > to_position:
            from_row, from_column, to_row, to_column = (
                to_row,
                to_column,
                from_row,
                from_column,
            )

        # If the range is within a single line
        if from_row == to_row:
            line = lines[from_row]
            deleted_text = line[from_column:to_column]
            lines[from_row] = line[:from_column] + line[to_column:]
        else:
            # The range spans multiple lines
            start_line = lines[from_row]
            end_line = lines[to_row]

            # TODO - I think this might be slightly off.
            #  When you delete a line, it records the deleted text with two newlines at the end instead of 1.
            # Add the deleted segments from the start and end lines to the deleted text
            deleted_text = (
                start_line[from_column:]
                + "\n"
                + "\n".join(self.document_lines[from_row + 1 : to_row])
                + "\n"
                + end_line[:to_column]
            )

            # Update the lines at the start and end of the range
            lines[from_row] = start_line[:from_column] + end_line[to_column:]

            # Delete the lines in between
            del lines[from_row + 1 : to_row + 1]

        if cursor_destination is not None:
            self.cursor_position = cursor_destination
        else:
            # Move the cursor to the start of the deleted range
            self.cursor_position = (from_row, from_column)

        self._refresh_size()
        return deleted_text

    def action_delete_left(self) -> None:
        """Deletes the character to the left of the cursor and updates the cursor position."""
        if self.cursor_at_start_of_document:
            return

        cursor_row, cursor_column = self.cursor_position
        lines = self.document_lines
        from_position = self.cursor_position
        if self.cursor_at_start_of_row:
            to_position = (cursor_row - 1, len(lines[cursor_row - 1]))
        else:
            to_position = (cursor_row, cursor_column - 1)

        self.edit(Delete(from_position, to_position))

    def action_delete_right(self) -> None:
        """Deletes the character to the right of the cursor and keeps the cursor at the same position."""
        if self.cursor_at_end_of_document:
            return

        cursor_row, cursor_column = self.cursor_position
        from_position = self.cursor_position
        if self.cursor_at_end_of_row:
            to_position = (cursor_row + 1, 0)
        else:
            to_position = (cursor_row, cursor_column + 1)

        self.edit(Delete(from_position, to_position))

    def action_delete_line(self) -> None:
        """Deletes the line the cursor is on."""
        cursor_row, _ = self.cursor_position
        from_position = (cursor_row, 0)
        to_position = (cursor_row + 1, 0)
        self.edit(Delete(from_position, to_position))

    def action_delete_to_start_of_line(self) -> None:
        """Deletes from the cursor position to the start of the line."""
        cursor_row, cursor_column = self.cursor_position
        from_position = self.cursor_position
        to_position = (cursor_row, 0)
        self.edit(Delete(from_position, to_position))

    def action_delete_to_end_of_line(self) -> None:
        """Deletes from the cursor position to the end of the line."""
        cursor_row, cursor_column = self.cursor_position
        from_position = self.cursor_position
        to_position = (cursor_row, len(self.document_lines[cursor_row]))
        self.edit(Delete(from_position, to_position))

    # --- Debug actions
    def action_print_line_cache(self) -> None:
        log.debug(self._line_cache)

        def traverse(cursor) -> Iterable[Node]:
            yield cursor.node

            if cursor.goto_first_child():
                yield from traverse(cursor)
                while cursor.goto_next_sibling():
                    yield from traverse(cursor)
                cursor.goto_parent()

        log.debug(list(traverse(self._syntax_tree.walk())))

    def action_print_highlight_cache(self) -> None:
        log.debug(self._highlights)

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
            cursor=self.cursor_position,
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
                self._highlights[self.cursor_position[0]]
            ),
            highlight_cache_current_row=self._highlights[self.cursor_position[0]],
        )


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


if __name__ == "__main__":
    language = Language(LANGUAGES_PATH.resolve(), "python")
    parser = Parser()
    parser.set_language(language)

    CODE = """\
    from textual.app import App


    class ScreenApp(App):
        def on_mount(self) -> None:
            self.screen.styles.background = "darkblue"
            self.screen.styles.border = ("heavy", "white")


    if __name__ == "__main__":
        app = ScreenApp()
        app.run()
    """

    document_lines = CODE.splitlines(keepends=False)

    def read_callable(byte_offset, point):
        row, column = point
        if row >= len(document_lines) or column >= len(document_lines[row]):
            return None
        return document_lines[row][column:].encode("utf8")

    tree = parser.parse(bytes(CODE, "utf-8"))

    print(list(traverse_tree(tree.walk())))
