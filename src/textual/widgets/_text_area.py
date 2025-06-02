from __future__ import annotations

import dataclasses
import re
from array import array
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from functools import lru_cache
from itertools import chain
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    ClassVar,
    ContextManager,
    Iterable,
    MutableSequence,
    Optional,
    Sequence,
    Tuple,
)

from rich.cells import get_character_cell_size
from rich.console import RenderableType
from rich.style import Style
from rich.text import Text
from typing_extensions import Literal

from textual._text_area_theme import TextAreaTheme
from textual._tree_sitter import TREE_SITTER, get_language
from textual.color import Color
from textual.document._document import (
    Document,
    DocumentBase,
    EditResult,
    Location,
    Selection,
)
from textual.document._document_navigator import DocumentNavigator
from textual.document._edit import Edit
from textual.document._history import EditHistory
from textual.document._syntax_aware_document import (
    SyntaxAwareDocument,
    SyntaxAwareDocumentError,
)
from textual.document._wrapped_document import WrappedDocument
from textual.expand_tabs import expand_tabs_inline
from textual.screen import Screen

if TYPE_CHECKING:
    from tree_sitter import Language, Query

from textual import events, log
from textual._cells import cell_len, cell_width_to_column_index
from textual.binding import Binding
from textual.events import Message, MouseEvent
from textual.geometry import LineRegion, Offset, Region, Size, Spacing, clamp
from textual.reactive import Reactive, reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip

_OPENING_BRACKETS = {"{": "}", "[": "]", "(": ")"}
_CLOSING_BRACKETS = {v: k for k, v in _OPENING_BRACKETS.items()}
_TREE_SITTER_PATH = Path(__file__).parent / "../tree-sitter/"
_HIGHLIGHTS_PATH = _TREE_SITTER_PATH / "highlights/"
DISCARDABLE_CONTROL_CHARS: set[str] = set(
    chr(n) for n in chain(range(0x09), range(0x10, 0x20), range(0x7F, 0xA0))
)
TAB = "\t"
EMPTY_RANGE = range(0)

StartColumn = int
EndColumn = Optional[int]
HighlightName = str
Highlight = Tuple[StartColumn, EndColumn, HighlightName]
"""A tuple representing a syntax highlight within one line."""

BUILTIN_LANGUAGES = [
    "python",
    "markdown",
    "json",
    "toml",
    "yaml",
    "html",
    "css",
    "javascript",
    "rust",
    "go",
    "regex",
    "sql",
    "java",
    "bash",
    "xml",
]
"""Languages that are included in the `syntax` extras."""

# This is a pragmatic limitation, which allows some code to be simplified and
# other code to use less memory. This is basically 2**32 so lines of 2**31 less
# a few bytes are technically supported, but I (Paul Ollis) have no intention
# of writing the tests.
#
# This constant can be elimiated at the expense of handling extra corner cases
# in the code and not using array('L') in place of lists.
MAX_LINE_LENGTH_X2 = 0x1_0000_0000


class ThemeDoesNotExist(Exception):
    """Raised when the user tries to use a theme which does not exist.
    This means a theme which is not builtin, or has not been registered.
    """


class LanguageDoesNotExist(Exception):
    """Raised when the user tries to use a language which does not exist.
    This means a language which is not builtin, or has not been registered.
    """


class TextReprString(str):
    """A string 'optimised' for text representation.

    This extends the standard Python 'str' providing support for easily working
    with character cells.

    Use the `create` class method to instantiate instances.
    """

    __slots__ = ["_cell_offsets", "_cells", "_tab_offsets"]

    def __new__(cls, value: str):
        # Create the basic instance. the `create` class method is responsible
        # for assigning the additional attributes.
        inst = super().__new__(cls, value)
        return inst

    @classmethod
    @lru_cache(maxsize=256)
    def create(cls, text: str, tab_size: int = 4, tab_offset: int = 0):
        """Create a TextReprString from the given text.

        Any TAB characters in `text` are expanded before the instance is
        created. Expansion is performed with respect to character cells, taking
        into account wide characters and zero width combining characters.
        Leading zero width characters, all non-TAB control characters and
        combining characters immediately after TAB characters are discarded.

        Args:
            text: The text of the string.
            tab_size: The tab-stop size for the string.
            offset: The offset to the first tabstop position. Zero implies
                tab_size.
        """
        text, cells, cell_offsets, tab_offsets = cls._expand_and_map_string(
            text, tab_size, tab_offset
        )
        inst = cls(text)
        inst._cell_offsets = cell_offsets
        inst._cells = cells
        inst._tab_offsets = tab_offsets
        return inst

    @property
    def cells(self) -> list[tuple[str, ...]]:
        """A list of character tuples for this string's terminal representation.

        Most cells will consist of a 1-tuple holding a single unicode
        character. For double width characters, the first cell is a 1-tuple of
        the character and the following cell is an empty tuple. For TAB
        characters, a 1-tuple of (`\t`,) is followed by zero or more empty
        tuples. When a character is followed by one or more combining (zero
        width) characters, the cell is a tuple of the character and those
        combining characters.
        """
        return self._cells

    def cell_width(self, index) -> int:
        """The number of cells covered by the character at a given index.

        When the index lies on an expanded TAB character, the result is
        number of spaces used in the expansion.
        """
        try:
            cell_index = self._cell_offsets[index]
            n = len(self._cells[cell_index])
        except IndexError:
            return 1
        else:
            if n == 0:
                return 0
            cell_index += 1
            while cell_index < len(self._cells):
                chars = self._cells[cell_index]
                if chars:
                    break
                n += 1
                cell_index += 1
            return n

    def logical_character_width(self, index) -> int:
        """The logical width of the character at a given index.

        For TAB characters this is the number of spaces that the TAB has been
        expannded to. For all other characters this returns 1.
        """
        try:
            cell_index = self._cell_offsets[index]
            cell = self._cells[cell_index]
        except IndexError:
            return 1
        if cell == (TAB,):
            return self.cell_width(index)
        else:
            return 1

    def render_count(self, index) -> int:
        """How many characters combine into the cell for the character index.

        Typically this is 1, but if a character is followed by one or more
        combining (zero width) characters the value is increased accordingly.
        """
        try:
            cell_index = self._cell_offsets[index]
            return len(self._cells[cell_index])
        except IndexError:
            return 1

    def cell_offset(self, index) -> int:
        """Calculate the cell offset for the indexed character."""
        try:
            return self._cell_offsets[index]
        except IndexError:
            return self._cell_offsets[-1]

    def adjust_index_for_tabs(self, index) -> int:
        """Adjust index to allow for TAB character expansion."""
        try:
            return self._tab_offsets[index]
        except IndexError:
            return len(self)

    @staticmethod
    def _expand_and_map_string(
        text: str,
        tab_size: int,
        tab_offset: int,
    ) -> tuple[str, bytearray, bytearray]:
        """Expand TAB characters in text and generate useful mappings.

        Args:
            text: The text of the string.
            tab_size: The tab-stop size for the string.
            offset: An offset to the first tabstop position.
        Returns:
            A tuple of:

            1. The expanded string.
            2. A character cell representation of the string.
            3. Offsets that allow mapping string indices to cell indices.
            4. Offsets that map from the original string to the expanded string.
        """
        expanded_text: list[str] = []
        cell_offsets = array("L")
        tab_offsets = array("L")
        cells: list[tuple[str, ...]] = []

        next_tab_offset = tab_size if tab_offset == 0 else tab_offset
        char_index = 0
        cell_index = 0
        discarding_zero_width = True
        empty_tuple = ()

        for c in text:
            if discarding_zero_width and character_cell_size(c) == 0:
                # Discard invalid zero width/control characters.
                continue

            if c in DISCARDABLE_CONTROL_CHARS:
                continue

            discarding_zero_width = False
            tab_offsets.append(char_index)
            if c == TAB:
                # Replace with a space and add additional spaces so that the
                # next character's cell is tab-aligned.
                expanded_text.append(" ")
                cells.append((TAB,))
                cell_offsets.append(cell_index)
                char_index += 1
                cell_index += 1
                while cell_index < next_tab_offset:
                    expanded_text.append(" ")
                    cells.append(empty_tuple)
                    cell_offsets.append(cell_index)
                    cell_index += 1
                    char_index += 1
                discarding_zero_width = False

            else:
                width = character_cell_size(c)
                if width == 0:
                    cells[-1] = cells[-1] + (c,)
                else:
                    expanded_text.append(c)
                    cells.append((c,))
                    assert width == 1 or width == 2
                    if width == 2:
                        cells.append(())

                cell_offsets.append(cell_index)
                char_index += 1
                cell_index += character_cell_size(c)

                if cell_index >= next_tab_offset:
                    next_tab_offset += tab_size

        # Add a cell offset for the 'cursor-at-end-of-line' position.
        cell_offsets.append(char_index)
        return "".join(expanded_text), cells, cell_offsets, tab_offsets


class DocSelection:

    def __init__(self, selection: Selection, lines: list[str]):
        start, end = selection.start, selection.end
        self.selection = Selection(*sorted((start, end)))
        self.cursor = end
        self.lines = lines
        self.line_range = range(selection.start[0], selection.end[0] + 1)

    def char_range(self, index) -> range:
        """The range of characters covered on a given line."""
        lines = self.lines
        if index in self.line_range and index < len(lines):
            selection = self.selection
            line = lines[index]
            if len(self.line_range) == 1:
                return range(selection.start[1], selection.end[1] + 1)
            elif index == selection.start[0]:
                return range(selection.start[1], len(line))
            elif index == selection.end[0]:
                return range(0, min(selection.end[1] + 1, len(line)))
            else:
                return range(0, len(line))
        else:
            return range(0)

    def __len__(self) -> int:
        return len(self.line_range)


class HighlightMap:
    """Lazy evaluated pseudo dictionary mapping lines to highlight information.

    This represents a snapshot of the TextArea's underlying document.

    Args:
        text_area_widget: The associated `TextArea` widget.
    """

    BLOCK_SIZE = 50

    def __init__(self):
        self._lines: list[str] = []
        """The lines from which the syntax tree was generated."""

        self._tree: Tree | None = None
        """The tree-sitter tree from which to genrate highlights."""

        self._query: Query | None = None
        """The tree-sitter query used to generate highlights from the tree."""

        self._highlighted_blocks: set[int] = set()
        """The set of already highlighted blocks, BLOCK_SIZE lines per block."""

        self._highlights: dict[int, list[Highlight]] = defaultdict(list)
        """A cache mapping line index to a list of Highlight instances."""

        self.tab_size: int = 4
        """The tab size setting in effect."""

    @property
    def line_count(self) -> int:
        """The number of lines in the map."""
        return len(self._lines)

    def copy(self) -> HighlightMap:
        """Create a copy of this highlight map."""
        inst = HighlightMap()
        inst._lines = self._lines
        inst._tree = self._tree
        inst._query = self._query
        inst._highlighted_blocks = self._highlighted_blocks.copy()
        inst._highlights = self._highlights.copy()
        return inst

    def set_snapshot(
        self, lines: list[str], query: Query, tree: Tree, tab_size: int
    ) -> None:
        """Set the snapshot information for this mapping

        Args:
            lines: The lines from which the syntax tree was generated.
            query: The current Query structure used to generate highlights.
            tree: The tree-sitter syntax tree.
            tab_size: The tab_size for the text area.
        ."""
        if self._tree is not tree:
            self._highlights.clear()
            self._highlighted_blocks.clear()
            self._query = query
            self._tree = tree
            self.tab_size = tab_size
            self._lines = [] if None in (query, tree) else lines

    def set_query(self, query: Query) -> None:
        self._query = query
        self._highlights.clear()
        self._highlighted_blocks.clear()

    def difference_region(
        self, index: int, other_map: HighlightMap
    ) -> LineRegion | None:
        """Create a region by comparing highlights for a line with another map.

        Args:
            index: The index of the line to compare.
            other_map: The other HighlightMap to use for comparison.

        Returns:
            None if the highlights are the same. Otherwise a Region
            covering the full extent of the changes.
        """
        highlights = self[index]
        other_highlighs = other_map[index]
        if highlights != other_highlighs:
            min_start = min(
                highlight[0] for highlight in chain(highlights, other_highlighs)
            )
            max_end = max(
                highlight[1] for highlight in chain(highlights, other_highlighs)
            )
            return LineRegion(min_start, index, max_end - min_start + 1)
        else:
            return None

    @staticmethod
    def _highlight_change_range(highlight_list_a, highlight_list_b) -> range:
        min_start = min(
            highlight[0] for highlight in chain(highlight_list_a, highlight_list_b)
        )
        max_end = max(
            highlight[1] for highlight in chain(highlight_list_a, highlight_list_b)
        )
        return range(min_start, max_end + 1)

    def __getitem__(self, index: int) -> list[Highlight]:
        if index >= self.line_count:
            return []

        block_index = index // self.BLOCK_SIZE
        if block_index not in self._highlighted_blocks:
            self._highlighted_blocks.add(block_index)
            self._build_part_of_highlight_map(block_index * self.BLOCK_SIZE)
        return self._highlights[index]

    def _build_part_of_highlight_map(self, start_index: int) -> None:
        """Build part of the highlight map.

        This is invoped by __getitem__, when an uncached highlight list is
        accessed. It generates the highlights for the block of lines containing
        the index and adds them to the cache.

        Args:
            start_index: The start of the block of lines for which to build the
            map.
        """
        start_point = (start_index, 0)
        end_index = min(self.line_count, start_index + self.BLOCK_SIZE)
        end_point = (end_index, 0)
        with temporary_query_point_range(self._query, start_point, end_point):
            captures = self._query.captures(self._tree.root_node)

        highlights = self._highlights
        line_count = len(self._lines)
        for highlight_name, nodes in captures.items():
            for node in nodes:
                node_start_row, node_start_column = node.start_point
                node_end_row, node_end_column = node.end_point
                if node_start_row == node_end_row:
                    if node_start_row < line_count:
                        highlight = node_start_column, node_end_column, highlight_name
                        highlights[node_start_row].append(highlight)
                else:
                    # Add the first line of the node range
                    if node_start_row < line_count:
                        highlights[node_start_row].append(
                            (node_start_column, None, highlight_name)
                        )

                    # Add the middle lines - entire row of this node is highlighted
                    middle_highlight = (0, None, highlight_name)
                    for node_row in range(node_start_row + 1, node_end_row):
                        if node_row < line_count:
                            highlights[node_row].append(middle_highlight)

                    # Add the last line of the node range
                    if node_end_row < line_count:
                        highlights[node_end_row].append(
                            (0, node_end_column, highlight_name)
                        )

        def realign_highlight(highlight):
            start, end, name = highlight
            return mapper[start], mapper[end], name

        # Tree-sitter uses byte offsets, but we want to use characters so we
        # adjust each highlight's offset here to match character positions in
        # the (TAB expanded) line text.
        block_end = min(line_count, start_index + self.BLOCK_SIZE)
        for index in range(start_index, block_end):
            # text, offsets = expand_tabs(self._lines[index])
            text = self._lines[index]
            mapper = build_byte_to_tab_expanded_string_table(text, self.tab_size)
            highlights[index][:] = [
                realign_highlight(highlight) for highlight in highlights[index]
            ]

        # The highlights for each line need to be sorted. Each highlight is of
        # the form:
        #
        #     a, b, highlight-name
        #
        # Where a is a number and b is a number or ``None``. These highlights need
        # to be sorted in ascending order of ``a``. When two highlights have the same
        # value of ``a`` then the one with the larger a--b range comes first, with ``None``
        # being considered larger than any number.
        def sort_key(highlight: Highlight) -> tuple[int, int, int]:
            a, b, _ = highlight
            max_range_index = 1
            if b is None:
                max_range_index = 0
                b = a
            return a, max_range_index, a - b

        for line_index in range(start_index, end_index):
            highlights.get(line_index, []).sort(key=sort_key)


@dataclass
class PreRenderLine:
    """Pre-render information about a physical line in a TextArea.

    This stores enough information to compute difference regions.
    """

    text: TextReprString
    """The plain form of the text on the line."""
    gutter_text: str
    """The text shown in the gutter."""
    select_range: range
    """The range of characters highlighted by the current selection."""
    syntax: list[Highlight]
    """The syntax highlights for the line."""
    cursor_highlighted: bool
    """Set if cursor highlighting is shown for this physical line."""

    def make_diff_regions(
        self,
        text_area: TextArea,
        y: int,
        line: PreRenderLine | None,
        full_width: int,
        gutter_width: int,
        prev_gutter_width: int,
    ) -> list[LineRegion]:
        text_width = full_width - gutter_width
        if line is None:
            return [LineRegion(0, y, text_width)]

        def text_region(x, width):
            return LineRegion(x + gutter_width, y, width)

        regions = []
        if self.cursor_highlighted != line.cursor_highlighted:
            regions.append(LineRegion(0, y, text_width + gutter_width))
            return regions

        if self.text != line.text:
            regions.append(
                build_difference_region(
                    y,
                    self.text.cells,
                    line.text.cells,
                    x_offset=gutter_width,
                )
            )

        if self.gutter_text != line.gutter_text:
            text_a = text_b = ""
            if gutter_width > 1:
                gutter_width_no_margin = gutter_width - 2
                text_a = f"{self.gutter_text:>{gutter_width_no_margin}}"
            if prev_gutter_width > 1:
                gutter_width_no_margin = prev_gutter_width - 2
                text_b = f"{line.gutter_text:>{gutter_width_no_margin}}"
            regions.append(build_difference_region(y, text_a, text_b))

        if self.select_range != line.select_range:
            before, common, after = intersect_ranges(
                self.select_range, line.select_range
            )
            if before:
                regions.append(text_region(before.start, len(before)))
            if after:
                regions.append(text_region(after.start, len(after)))

        if self.syntax != line.syntax:
            min_start = min(hl[0] for hl in chain(self.syntax, line.syntax))
            max_end = max(hl[1] for hl in chain(self.syntax, line.syntax))
            regions.append(text_region(min_start, max_end - min_start + 1))

        return regions


@dataclass
class PreRenderState:
    """Information about the TextArea state at the just before being rendered.

    Attributes:
        lines: A snapshot of the document's lines at the time of rendering.
        cursor: A tuple of (visible, cell_x, cell_y, width, char_x).
        size: The (width, height) of the full text area, including the gutter.
        gutter_width: The width of the gutter.
        bracket: A tuple of (cell_x, cell_y, char_x).
    """

    lines: list[PreRenderLine]
    cursor: tuple[bool, int, int, int] = (False, -1, -1, 1)
    size: tuple[int, int] = 0, 0
    gutter_width: int = 0
    bracket: tuple[int, int, int] = -1, -1, -1

    def make_diff_regions(
        self,
        text_area: TextArea,
        state: PreRenderState,
    ) -> list[LineRegion]:

        def text_region(x, y, width):
            return LineRegion(x + gutter_width, y, width)

        gutter_width = self.gutter_width
        prev_gutter_width = state.gutter_width
        regions = []
        for y, line in enumerate(self.lines):
            try:
                old_line = state.lines[y]
            except IndexError:
                old_line = None
            if not (old_line == line):
                regions.extend(
                    line.make_diff_regions(
                        text_area,
                        y,
                        old_line,
                        self.size.width,
                        gutter_width,
                        prev_gutter_width,
                    )
                )

        if self.cursor != state.cursor:
            if self.cursor[1] >= 0:
                regions.append(text_region(*self.cursor[1:-1]))
            if state.cursor[1] >= 0:
                regions.append(text_region(*state.cursor[1:-1]))
        if self.bracket != state.bracket:
            if self.bracket[0] >= 0:
                regions.append(text_region(*self.bracket[:-1], 1))
            if state.bracket[0] >= 0:
                regions.append(text_region(*state.bracket[:-1], 1))
        return regions


@dataclass
class TextAreaLanguage:
    """A container for a language which has been registered with the TextArea."""

    name: str
    """The name of the language"""

    language: "Language" | None
    """The tree-sitter language object if that has been overridden, or None if it is a built-in language."""

    highlight_query: str
    """The tree-sitter highlight query to use for syntax highlighting."""


class TextArea(ScrollView):
    DEFAULT_CSS = """\
TextArea {
    width: 1fr;
    height: 1fr;
    border: tall $border-blurred;
    padding: 0 1;
    color: $foreground;
    background: $surface;
    &.-textual-compact {
        border: none !important;
    }
    & .text-area--cursor {
        text-style: $input-cursor-text-style;
    }
    & .text-area--gutter {
        color: $foreground 40%;
    }

    & .text-area--cursor-gutter {
        color: $foreground 60%;
        background: $boost;
        text-style: bold;
    }

    & .text-area--cursor-line {
       background: $boost;
    }

    & .text-area--selection {
        background: $input-selection-background;
    }

    & .text-area--matching-bracket {
        background: $foreground 30%;
    }

    &:focus {
        border: tall $border;
    }

    &:ansi {
        & .text-area--selection {
            background: transparent;
            text-style: reverse;
        }
    }

    &:dark {
        .text-area--cursor {
            color: $input-cursor-foreground;
            background: $input-cursor-background;
        }
        &.-read-only .text-area--cursor {
            background: $warning-darken-1;
        }
    }

    &:light {
        .text-area--cursor {
            color: $text 90%;
            background: $foreground 70%;
        }
        &.-read-only .text-area--cursor {
            background: $warning-darken-1;
        }
    }
}
"""

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "text-area--cursor",
        "text-area--gutter",
        "text-area--cursor-gutter",
        "text-area--cursor-line",
        "text-area--selection",
        "text-area--matching-bracket",
    }
    """
    `TextArea` offers some component classes which can be used to style aspects of the widget.

    Note that any attributes provided in the chosen `TextAreaTheme` will take priority here.

    | Class | Description |
    | :- | :- |
    | `text-area--cursor` | Target the cursor. |
    | `text-area--gutter` | Target the gutter (line number column). |
    | `text-area--cursor-gutter` | Target the gutter area of the line the cursor is on. |
    | `text-area--cursor-line` | Target the line the cursor is on. |
    | `text-area--selection` | Target the current selection. |
    | `text-area--matching-bracket` | Target matching brackets. |
    """

    BINDINGS = [
        # Cursor movement
        Binding("up", "cursor_up", "Cursor up", show=False),
        Binding("down", "cursor_down", "Cursor down", show=False),
        Binding("left", "cursor_left", "Cursor left", show=False),
        Binding("right", "cursor_right", "Cursor right", show=False),
        Binding("ctrl+left", "cursor_word_left", "Cursor word left", show=False),
        Binding("ctrl+right", "cursor_word_right", "Cursor word right", show=False),
        Binding("home,ctrl+a", "cursor_line_start", "Cursor line start", show=False),
        Binding("end,ctrl+e", "cursor_line_end", "Cursor line end", show=False),
        Binding("pageup", "cursor_page_up", "Cursor page up", show=False),
        Binding("pagedown", "cursor_page_down", "Cursor page down", show=False),
        # Making selections (generally holding the shift key and moving cursor)
        Binding(
            "ctrl+shift+left",
            "cursor_word_left(True)",
            "Cursor left word select",
            show=False,
        ),
        Binding(
            "ctrl+shift+right",
            "cursor_word_right(True)",
            "Cursor right word select",
            show=False,
        ),
        Binding(
            "shift+home",
            "cursor_line_start(True)",
            "Cursor line start select",
            show=False,
        ),
        Binding(
            "shift+end", "cursor_line_end(True)", "Cursor line end select", show=False
        ),
        Binding("shift+up", "cursor_up(True)", "Cursor up select", show=False),
        Binding("shift+down", "cursor_down(True)", "Cursor down select", show=False),
        Binding("shift+left", "cursor_left(True)", "Cursor left select", show=False),
        Binding("shift+right", "cursor_right(True)", "Cursor right select", show=False),
        # Shortcut ways of making selections
        # Binding("f5", "select_word", "select word", show=False),
        Binding("f6", "select_line", "Select line", show=False),
        Binding("f7", "select_all", "Select all", show=False),
        # Deletion
        Binding("backspace", "delete_left", "Delete character left", show=False),
        Binding(
            "ctrl+w", "delete_word_left", "Delete left to start of word", show=False
        ),
        Binding("delete,ctrl+d", "delete_right", "Delete character right", show=False),
        Binding(
            "ctrl+f", "delete_word_right", "Delete right to start of word", show=False
        ),
        Binding("ctrl+x", "cut", "Cut", show=False),
        Binding("ctrl+c", "copy", "Copy", show=False),
        Binding("ctrl+v", "paste", "Paste", show=False),
        Binding(
            "ctrl+u", "delete_to_start_of_line", "Delete to line start", show=False
        ),
        Binding(
            "ctrl+k",
            "delete_to_end_of_line_or_delete_line",
            "Delete to line end",
            show=False,
        ),
        Binding(
            "ctrl+shift+k",
            "delete_line",
            "Delete line",
            show=False,
        ),
        Binding("ctrl+z", "undo", "Undo", show=False),
        Binding("ctrl+y", "redo", "Redo", show=False),
    ]
    """
    | Key(s)                 | Description                                  |
    | :-                     | :-                                           |
    | up                     | Move the cursor up.                          |
    | down                   | Move the cursor down.                        |
    | left                   | Move the cursor left.                        |
    | ctrl+left              | Move the cursor to the start of the word.    |
    | ctrl+shift+left        | Move the cursor to the start of the word and select.    |
    | right                  | Move the cursor right.                       |
    | ctrl+right             | Move the cursor to the end of the word.      |
    | ctrl+shift+right       | Move the cursor to the end of the word and select.      |
    | home,ctrl+a            | Move the cursor to the start of the line.    |
    | end,ctrl+e             | Move the cursor to the end of the line.      |
    | shift+home             | Move the cursor to the start of the line and select.      |
    | shift+end              | Move the cursor to the end of the line and select.      |
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
    | ctrl+shift+k           | Delete the current line.                     |
    | ctrl+u                 | Delete from cursor to the start of the line. |
    | ctrl+k                 | Delete from cursor to the end of the line.   |
    | f6                     | Select the current line.                     |
    | f7                     | Select all text in the document.             |
    | ctrl+z                 | Undo.                                        |
    | ctrl+y                 | Redo.                                        |
    | ctrl+x                 | Cut selection or line if no selection.       |
    | ctrl+c                 | Copy selection to clipboard.                 |
    | ctrl+v                 | Paste from clipboard.                        |
    """

    language: Reactive[str | None] = reactive(None, always_update=True, init=False)
    """The language to use.

    This must be set to a valid, non-None value for syntax highlighting to work.

    If the value is a string, a built-in language parser will be used if available.

    If you wish to use an unsupported language, you'll have to register
    it first using  [`TextArea.register_language`][textual.widgets._text_area.TextArea.register_language].
    """

    theme: Reactive[str] = reactive("css", always_update=True, init=False)
    """The name of the theme to use.

    Themes must be registered using  [`TextArea.register_theme`][textual.widgets._text_area.TextArea.register_theme] before they can be used.

    Syntax highlighting is only possible when the `language` attribute is set.
    """

    selection: Reactive[Selection] = reactive(
        Selection(),
        init=False,
        always_update=True,
        repaint=False,
    )
    """The selection start and end locations (zero-based line_index, offset).

    This represents the cursor location and the current selection.

    The `Selection.end` always refers to the cursor location.

    If no text is selected, then `Selection.end == Selection.start` is True.

    The text selected in the document is available via the `TextArea.selected_text` property.
    """

    show_line_numbers: Reactive[bool] = reactive(False, init=False)
    """True to show the line number column on the left edge, otherwise False.

    Changing this value will immediately re-render the `TextArea`."""

    line_number_start: Reactive[int] = reactive(1, init=False)
    """The line number the first line should be."""

    indent_width: Reactive[int] = reactive(4, init=False)
    """The width of tabs or the multiple of spaces to align to on pressing the `tab` key.

    If the document currently open contains tabs that are currently visible on screen,
    altering this value will immediately change the display width of the visible tabs.
    """

    match_cursor_bracket: Reactive[bool] = reactive(True, init=False)
    """If the cursor is at a bracket, highlight the matching bracket (if found)."""

    cursor_blink: Reactive[bool] = reactive(True, init=False)
    """True if the cursor should blink."""

    soft_wrap: Reactive[bool] = reactive(True, init=False)
    """True if text should soft wrap."""

    read_only: Reactive[bool] = reactive(False)
    """True if the content is read-only.

    Read-only means end users cannot insert, delete or replace content.

    The document can still be edited programmatically via the API.
    """

    compact: reactive[bool] = reactive(False, toggle_class="-textual-compact")
    """Enable compact display?"""

    _cursor_visible: Reactive[bool] = reactive(False, repaint=False, init=False)
    """Indicates where the cursor is in the blink cycle. If it's currently
    not visible due to blinking, this is False."""

    @dataclass
    class Changed(Message):
        """Posted when the content inside the TextArea changes.

        Handle this message using the `on` decorator - `@on(TextArea.Changed)`
        or a method named `on_text_area_changed`.
        """

        text_area: TextArea
        """The `text_area` that sent this message."""

        @property
        def control(self) -> TextArea:
            """The `TextArea` that sent this message."""
            return self.text_area

    @dataclass
    class SelectionChanged(Message):
        """Posted when the selection changes.

        This includes when the cursor moves or when text is selected."""

        selection: Selection
        """The new selection."""
        text_area: TextArea
        """The `text_area` that sent this message."""

        @property
        def control(self) -> TextArea:
            return self.text_area

    def __init__(
        self,
        text: str = "",
        *,
        language: str | None = None,
        theme: str = "css",
        soft_wrap: bool = True,
        tab_behavior: Literal["focus", "indent"] = "focus",
        read_only: bool = False,
        show_line_numbers: bool = False,
        line_number_start: int = 1,
        max_checkpoints: int = 50,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        tooltip: RenderableType | None = None,
        compact: bool = False,
    ) -> None:
        """Construct a new `TextArea`.

        Args:
            text: The initial text to load into the TextArea.
            language: The language to use.
            theme: The theme to use.
            soft_wrap: Enable soft wrapping.
            tab_behavior: If 'focus', pressing tab will switch focus. If 'indent', pressing tab will insert a tab.
            read_only: Enable read-only mode. This prevents edits using the keyboard.
            show_line_numbers: Show line numbers on the left edge.
            line_number_start: What line number to start on.
            max_checkpoints: The maximum number of undo history checkpoints to retain.
            name: The name of the `TextArea` widget.
            id: The ID of the widget, used to refer to it from Textual CSS.
            classes: One or more Textual CSS compatible class names separated by spaces.
            disabled: True if the widget is disabled.
            tooltip: Optional tooltip.
            compact: Enable compact style (without borders).
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        self._languages: dict[str, TextAreaLanguage] = {}
        """Maps language names to TextAreaLanguage. This is only used for languages
        registered by end-users using `TextArea.register_language`. If a user attempts
        to set `TextArea.language` to a language that is not registered here, we'll
        attempt to get it from the environment. If that fails, we'll fall back to
        plain text.
        """

        self._themes: dict[str, TextAreaTheme] = {}
        """Maps theme names to TextAreaTheme."""

        self.indent_type: Literal["tabs", "spaces"] = "spaces"
        """Whether to indent using tabs or spaces."""

        self._word_pattern = re.compile(r"(?<=\W)(?=\w)|(?<=\w)(?=\W)")
        """Compiled regular expression for what we consider to be a 'word'."""

        self.history: EditHistory = EditHistory(
            max_checkpoints=max_checkpoints,
            checkpoint_timer=2.0,
            checkpoint_max_characters=100,
        )
        """A stack (the end of the list is the top of the stack) for tracking edits."""

        self._selecting = False
        """True if we're currently selecting text using the mouse, otherwise False."""

        self._matching_bracket_location: Location | None = None
        """The location (row, column) of the bracket which matches the bracket the
        cursor is currently at. If the cursor is at a bracket, or there's no matching
        bracket, this will be `None`."""

        self._highlight_query: "Query | None" = None
        """The query that's currently being used for highlighting."""

        self.document: DocumentBase = Document(text)
        """The document this widget is currently editing."""

        self._highlights: HighlightMap = HighlightMap()
        """Mapping of line number to the lists of highlights."""

        self.wrapped_document: WrappedDocument = WrappedDocument(self.document)
        """The wrapped view of the document."""

        self.navigator: DocumentNavigator = DocumentNavigator(self.wrapped_document)
        """Queried to determine where the cursor should move given a navigation
        action, accounting for wrapping etc."""

        self._cursor_offset = (0, 0)
        """The virtual offset of the cursor (not screen-space offset)."""

        self._old_render_state: PreRenderState = PreRenderState(lines=[])
        self._new_render_state: PreRenderState = PreRenderState(lines=[])
        """Saved state for the last time this widget was rendered."""

        self._set_document(text, language)

        self.language = language
        self.theme = theme

        self._theme: TextAreaTheme
        """The `TextAreaTheme` corresponding to the set theme name. When the `theme`
        reactive is set as a string, the watcher will update this attribute to the
        corresponding `TextAreaTheme` object."""

        self.set_reactive(TextArea.soft_wrap, soft_wrap)
        self.set_reactive(TextArea.read_only, read_only)
        self.set_reactive(TextArea.show_line_numbers, show_line_numbers)
        self.set_reactive(TextArea.line_number_start, line_number_start)

        self.tab_behavior = tab_behavior

        if tooltip is not None:
            self.tooltip = tooltip

        self.compact = compact

    @classmethod
    def code_editor(
        cls,
        text: str = "",
        *,
        language: str | None = None,
        theme: str = "monokai",
        soft_wrap: bool = False,
        tab_behavior: Literal["focus", "indent"] = "indent",
        read_only: bool = False,
        show_line_numbers: bool = True,
        line_number_start: int = 1,
        max_checkpoints: int = 50,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        tooltip: RenderableType | None = None,
        compact: bool = False,
    ) -> TextArea:
        """Construct a new `TextArea` with sensible defaults for editing code.

        This instantiates a `TextArea` with line numbers enabled, soft wrapping
        disabled, "indent" tab behavior, and the "monokai" theme.

        Args:
            text: The initial text to load into the TextArea.
            language: The language to use.
            theme: The theme to use.
            soft_wrap: Enable soft wrapping.
            tab_behavior: If 'focus', pressing tab will switch focus. If 'indent', pressing tab will insert a tab.
            show_line_numbers: Show line numbers on the left edge.
            line_number_start: What line number to start on.
            name: The name of the `TextArea` widget.
            id: The ID of the widget, used to refer to it from Textual CSS.
            classes: One or more Textual CSS compatible class names separated by spaces.
            disabled: True if the widget is disabled.
            tooltip: Optional tooltip
            compact: Enable compact style (without borders).
        """
        return cls(
            text,
            language=language,
            theme=theme,
            soft_wrap=soft_wrap,
            tab_behavior=tab_behavior,
            read_only=read_only,
            show_line_numbers=show_line_numbers,
            line_number_start=line_number_start,
            max_checkpoints=max_checkpoints,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            tooltip=tooltip,
            compact=compact,
        )

    @staticmethod
    def _get_builtin_highlight_query(language_name: str) -> str:
        """Get the highlight query for a builtin language.

        Args:
            language_name: The name of the builtin language.

        Returns:
            The highlight query.
        """
        try:
            highlight_query_path = (
                Path(_HIGHLIGHTS_PATH.resolve()) / f"{language_name}.scm"
            )
            highlight_query = highlight_query_path.read_text()
        except OSError as error:
            log.warning(f"Unable to load highlight query. {error}")
            highlight_query = ""

        return highlight_query

    def check_consume_key(self, key: str, character: str | None = None) -> bool:
        """Check if the widget may consume the given key.

        As a textarea we are expecting to capture printable keys.

        Args:
            key: A key identifier.
            character: A character associated with the key, or `None` if there isn't one.

        Returns:
            `True` if the widget may capture the key in it's `Key` message, or `False` if it won't.
        """
        if self.read_only:
            # In read only mode we don't consume any key events
            return False
        if self.tab_behavior == "indent" and key == "tab":
            # If tab_behavior is indent, then we consume the tab
            return True
        # Otherwise we capture all printable keys
        return character is not None and character.isprintable()

    def _handle_syntax_tree_update(self, tree: Tree) -> None:
        """Reflect changes to the syntax tree."""
        self._trigger_repaint()

    def _handle_change_affecting_highlighting(
        self,
        force_update: bool = False,
    ) -> None:
        """Trigger an update of the syntax highlighting tree.

        If the tree is already being updated in the background then that will
        complete first.

        Args:
            force_update: When set, ensure that the syntax tree is regenerated
                unconditionally.
        """
        self.document.trigger_syntax_tree_update(force_update=force_update)

    def _reset_highlights(self) -> None:
        """Reset the lazily evaluated highlight map."""

        if self._highlight_query:
            self._highlights.reset()

    def _watch_has_focus(self, focus: bool) -> None:
        self._cursor_visible = focus
        if focus:
            self._restart_blink()
            self.app.cursor_position = self.cursor_screen_offset
            self.history.checkpoint()
        else:
            self._pause_blink(visible=False)

    def _watch_selection(
        self, previous_selection: Selection, selection: Selection
    ) -> None:
        """When the cursor moves, scroll it into view."""
        # Find the visual offset of the cursor in the document

        if not self.is_mounted:
            return

        self.app.clear_selection()

        cursor_location = selection.end

        self.scroll_cursor_visible()

        if previous_selection != selection:
            self.post_message(self.SelectionChanged(selection, self))

        cursor_row, cursor_column = cursor_location

        try:
            character = self.document[cursor_row][cursor_column]
        except IndexError:
            character = ""

        # Record the location of a matching closing/opening bracket.
        match_location = self.find_matching_bracket(character, cursor_location)
        self._matching_bracket_location = match_location
        self.app.cursor_position = self.cursor_screen_offset
        self._trigger_repaint()

    def _watch_cursor_blink(self, blink: bool) -> None:
        if not self.is_mounted:
            return None
        if blink and self.has_focus:
            self._restart_blink()
        else:
            self._pause_blink(visible=self.has_focus)

    def _watch_read_only(self, read_only: bool) -> None:
        self.set_class(read_only, "-read-only")
        self._set_theme(self._theme.name)

    def _recompute_cursor_offset(self):
        """Recompute the (x, y) coordinate of the cursor in the wrapped document."""
        self._cursor_offset = self.wrapped_document.location_to_offset(
            self.cursor_location
        )

    def find_matching_bracket(
        self, bracket: str, search_from: Location
    ) -> Location | None:
        """If the character is a bracket, find the matching bracket.

        Args:
            bracket: The character we're searching for the matching bracket of.
            search_from: The location to start the search.

        Returns:
            The `Location` of the matching bracket, or `None` if it's not found.
            If the character is not available for bracket matching, `None` is returned.
        """
        match_location = None
        bracket_stack: list[str] = []
        if bracket in _OPENING_BRACKETS:
            # Search forwards for a closing bracket
            for candidate, candidate_location in self._yield_character_locations(
                search_from
            ):
                if candidate in _OPENING_BRACKETS:
                    bracket_stack.append(candidate)
                elif candidate in _CLOSING_BRACKETS:
                    if (
                        bracket_stack
                        and bracket_stack[-1] == _CLOSING_BRACKETS[candidate]
                    ):
                        bracket_stack.pop()
                        if not bracket_stack:
                            match_location = candidate_location
                            break
        elif bracket in _CLOSING_BRACKETS:
            # Search backwards for an opening bracket
            for (
                candidate,
                candidate_location,
            ) in self._yield_character_locations_reverse(search_from):
                if candidate in _CLOSING_BRACKETS:
                    bracket_stack.append(candidate)
                elif candidate in _OPENING_BRACKETS:
                    if (
                        bracket_stack
                        and bracket_stack[-1] == _OPENING_BRACKETS[candidate]
                    ):
                        bracket_stack.pop()
                        if not bracket_stack:
                            match_location = candidate_location
                            break

        return match_location

    def _validate_selection(self, selection: Selection) -> Selection:
        """Clamp the selection to valid locations."""
        start, end = selection
        clamp_visitable = self.clamp_visitable
        return Selection(clamp_visitable(start), clamp_visitable(end))

    def _watch_language(self, language: str | None) -> None:
        """When the language is updated, update the type of document."""
        self._set_document(self.document.text, language)

    def _watch_show_line_numbers(self) -> None:
        """The line number gutter contributes to virtual size, so recalculate."""
        self._rewrap_and_refresh_virtual_size()
        self.scroll_cursor_visible()

    def _watch_line_number_start(self) -> None:
        """The line number gutter max size might change and contributes to virtual size, so recalculate."""
        self._rewrap_and_refresh_virtual_size()
        self.scroll_cursor_visible()

    def _watch_indent_width(self) -> None:
        """Changing width of tabs will change the document display width."""
        self._rewrap_and_refresh_virtual_size()
        self.scroll_cursor_visible()

    def _watch_show_vertical_scrollbar(self) -> None:
        if self.wrap_width:
            self._rewrap_and_refresh_virtual_size()
        self.scroll_cursor_visible()

    def _watch_theme(self, theme: str) -> None:
        """We set the styles on this widget when the theme changes, to ensure that
        if padding is applied, the colors match."""
        self._set_theme(theme)

    def _app_theme_changed(self) -> None:
        self._set_theme(self._theme.name)

    def _set_theme(self, theme: str) -> None:
        theme_object: TextAreaTheme | None

        # If the user supplied a string theme name, find it and apply it.
        try:
            theme_object = self._themes[theme]
        except KeyError:
            theme_object = TextAreaTheme.get_builtin_theme(theme)
            if theme_object is None:
                raise ThemeDoesNotExist(
                    f"{theme!r} is not a builtin theme, or it has not been registered. "
                    f"To use a custom theme, register it first using `register_theme`, "
                    f"then switch to that theme by setting the `TextArea.theme` attribute."
                ) from None

        self._theme = dataclasses.replace(theme_object)
        if theme_object:
            base_style = theme_object.base_style
            if base_style:
                color = base_style.color
                background = base_style.bgcolor
                if color:
                    self.styles.color = Color.from_rich_color(color)
                if background:
                    self.styles.background = Color.from_rich_color(background)

    @property
    def available_themes(self) -> set[str]:
        """A list of the names of the themes available to the `TextArea`.

        The values in this list can be assigned `theme` reactive attribute of
        `TextArea`.

        You can retrieve the full specification for a theme by passing one of
        the strings from this list into `TextAreaTheme.get_by_name(theme_name: str)`.

        Alternatively, you can directly retrieve a list of `TextAreaTheme` objects
        (which contain the full theme specification) by calling
        `TextAreaTheme.builtin_themes()`.
        """
        return {
            theme.name for theme in TextAreaTheme.builtin_themes()
        } | self._themes.keys()

    def register_theme(self, theme: TextAreaTheme) -> None:
        """Register a theme for use by the `TextArea`.

        After registering a theme, you can set themes by assigning the theme
        name to the `TextArea.theme` reactive attribute. For example
        `text_area.theme = "my_custom_theme"` where `"my_custom_theme"` is the
        name of the theme you registered.

        If you supply a theme with a name that already exists that theme
        will be overwritten.
        """
        self._themes[theme.name] = theme

    @property
    def available_languages(self) -> set[str]:
        """A set of the names of languages available to the `TextArea`.

        The values in this set can be assigned to the `language` reactive attribute
        of `TextArea`.

        The returned set contains the builtin languages installed with the syntax extras,
        plus those registered via the `register_language` method.
        """
        return set(BUILTIN_LANGUAGES) | self._languages.keys()

    def register_language(
        self,
        name: str,
        language: "Language",
        highlight_query: str,
    ) -> None:
        """Register a language and corresponding highlight query.

        Calling this method does not change the language of the `TextArea`.
        On switching to this language (via the `language` reactive attribute),
        syntax highlighting will be performed using the given highlight query.

        If a string `name` is supplied for a builtin supported language, then
        this method will update the default highlight query for that language.

        Registering a language only registers it to this instance of `TextArea`.

        Args:
            name: The name of the language.
            language: A tree-sitter `Language` object.
            highlight_query: The highlight query to use for syntax highlighting this language.
        """
        self._languages[name] = TextAreaLanguage(name, language, highlight_query)

    def update_highlight_query(self, name: str, highlight_query: str) -> None:
        """Update the highlight query for an already registered language.

        Args:
            name: The name of the language.
            highlight_query: The highlight query to use for syntax highlighting this language.
        """
        if name not in self._languages:
            self._languages[name] = TextAreaLanguage(name, None, highlight_query)
        else:
            self._languages[name].highlight_query = highlight_query

        # If this is the currently loaded language, reload the document because
        # it could be a different highlight query for the same language.
        if name == self.language:
            self._set_document(self.text, name)
        if self._highlight_query:
            self._highlights.set_query(self._highlight_query)

    def _set_document(self, text: str, language: str | None) -> None:
        """Construct and return an appropriate document.

        Args:
            text: The text of the document.
            language: The name of the language to use. This must correspond to a tree-sitter
                language available in the current environment (e.g. use `python` for `tree-sitter-python`).
                If None, the document will be treated as plain text.
        """
        self._highlight_query = None
        if TREE_SITTER and language:
            if language in self._languages:
                # User-registered languages take priority.
                highlight_query = self._languages[language].highlight_query
                document_language = self._languages[language].language
                if document_language is None:
                    document_language = get_language(language)
            else:
                # No user-registered language, so attempt to use a built-in language.
                highlight_query = self._get_builtin_highlight_query(language)
                document_language = get_language(language)

            # No built-in language, and no user-registered language: use plain text and warn.
            if document_language is None:
                raise LanguageDoesNotExist(
                    f"tree-sitter is available, but no built-in or user-registered language called {language!r}.\n"
                    f"Ensure the language is installed (e.g. `pip install tree-sitter-ruby`)\n"
                    f"Falling back to plain text."
                )
            else:
                document: DocumentBase
                try:
                    document = SyntaxAwareDocument(text, document_language)
                except SyntaxAwareDocumentError:
                    document = Document(text)
                    log.warning(
                        f"Parser not found for language {document_language!r}. Parsing disabled."
                    )
                else:
                    self._highlight_query = document.prepare_query(highlight_query)
                    document.set_syntax_tree_update_callback(
                        self._handle_syntax_tree_update
                    )
        elif language and not TREE_SITTER:
            # User has supplied a language i.e. `TextArea(language="python")`, but they
            # don't have tree-sitter available in the environment. We fallback to plain text.
            log.warning(
                "tree-sitter not available in this environment. Parsing disabled.\n"
                "You may need to install the `syntax` extras alongside textual.\n"
                "Try `pip install 'textual[syntax]'` or '`poetry add textual[syntax]' to get started quickly.\n\n"
                "Alternatively, install tree-sitter manually (`pip install tree-sitter`) and then\n"
                "install the required language (e.g. `pip install tree-sitter-ruby`), then register it.\n"
                "and it's highlight query using TextArea.register_language().\n\n"
                "Falling back to plain text for now."
            )
            document = Document(text)
        else:
            # tree-sitter is available, but the user has supplied None or "" for the language.
            # Use a regular plain-text document.
            document = Document(text)

        if self.document:
            self.document.clean_up()
        self.document = document
        self.wrapped_document = WrappedDocument(document, tab_width=self.indent_width)
        self.navigator = DocumentNavigator(self.wrapped_document)
        self._handle_change_affecting_highlighting(force_update=True)
        self.move_cursor((0, 0))
        self._rewrap_and_refresh_virtual_size()

    @property
    def _visible_line_indices(self) -> tuple[int, int]:
        """Return the visible line indices as a tuple (top, bottom).

        Returns:
            A tuple (top, bottom) indicating the top and bottom visible line indices.
        """
        _, scroll_offset_y = self.scroll_offset
        return scroll_offset_y, scroll_offset_y + self.size.height

    def _watch_scroll_x(self) -> None:
        self.app.cursor_position = self.cursor_screen_offset

    def _watch_scroll_y(self) -> None:
        self.app.cursor_position = self.cursor_screen_offset

    def load_text(self, text: str) -> None:
        """Load text into the TextArea.

        This will replace the text currently in the TextArea and clear the edit history.

        Args:
            text: The text to load into the TextArea.
        """
        self.history.clear()
        self._set_document(text, self.language)
        self.post_message(self.Changed(self).set_sender(self))

    def _on_resize(self) -> None:
        self._rewrap_and_refresh_virtual_size()

    def _watch_soft_wrap(self) -> None:
        self._rewrap_and_refresh_virtual_size()
        self.call_after_refresh(self.scroll_cursor_visible, center=True)

    @property
    def wrap_width(self) -> int:
        """The width which gets used when the document wraps.

        Accounts for gutter, scrollbars, etc.
        """
        width, _ = self.scrollable_content_region.size
        cursor_width = 1
        if self.soft_wrap:
            return width - self.gutter_width - cursor_width
        return 0

    def _rewrap_and_refresh_virtual_size(self) -> None:
        self.wrapped_document.wrap(self.wrap_width, tab_width=self.indent_width)
        self._refresh_size()

    @property
    def is_syntax_aware(self) -> bool:
        """True if the TextArea is currently syntax aware - i.e. it's parsing document content."""
        return isinstance(self.document, SyntaxAwareDocument)

    def _yield_character_locations(
        self, start: Location
    ) -> Iterable[tuple[str, Location]]:
        """Yields character locations starting from the given location.

        Does not yield location of line separator characters like `\\n`.

        Args:
            start: The location to start yielding from.

        Returns:
            Yields tuples of (character, (row, column)).
        """
        row, column = start
        document = self.document
        line_count = document.line_count

        while 0 <= row < line_count:
            line = document[row]
            while column < len(line):
                yield line[column], (row, column)
                column += 1
            column = 0
            row += 1

    def _yield_character_locations_reverse(
        self, start: Location
    ) -> Iterable[tuple[str, Location]]:
        row, column = start
        document = self.document
        line_count = document.line_count

        while line_count > row >= 0:
            line = document[row]
            if column == -1:
                column = len(line) - 1
            while column >= 0:
                yield line[column], (row, column)
                column -= 1
            row -= 1

    def _refresh_size(self) -> None:
        """Update the virtual size of the TextArea."""
        dirty = self._dirty_regions.copy(), self._repaint_regions.copy()
        try:
            if self.soft_wrap:
                self.virtual_size = Size(0, self.wrapped_document.height)
            else:
                # +1 width to make space for the cursor resting at the end of the line
                width, height = self.document.get_size(self.indent_width)
                self.virtual_size = Size(width + self.gutter_width + 1, height)
        finally:
            self._dirty_regions, self._repaint_regions = dirty
        self._trigger_repaint()

    def get_line(self, line_index: int) -> Text:
        """Retrieve the line at the given line index.

        You can stylize the Text object returned here to apply additional
        styling to TextArea content.

        Args:
            line_index: The index of the line.

        Returns:
            A `rich.Text` object containing the requested line.
        """
        line_string = self.document.get_line(line_index)
        return Text(line_string, end="")

    def _prepare_for_repaint(self) -> Collection[Region]:
        with self._preserved_refresh_state():
            return self._do_prepare_for_repaint()

    def _do_prepare_for_repaint(self) -> Collection[Region]:
        is_syntax_aware = self.is_syntax_aware
        if is_syntax_aware:
            highlights = self._highlights
            highlights.set_snapshot(
                lines=self.document.copy_of_lines(),
                query=self._highlight_query,
                tree=self.document.current_syntax_tree,
                tab_size=self.indent_width,
            )

        prev_render_state = self._new_render_state
        render_state = self._pre_render_lines()
        regions = render_state.make_diff_regions(self, prev_render_state)
        self._old_render_state = render_state

        self._repaint_regions.clear()
        self._dirty_regions.clear()

        regions = [r.as_region(0) for r in regions if r.width > 0]
        if regions:
            self.refresh(*regions)

    def render_lines(self, crop: Region) -> list[Strip]:
        if len(self._dirty_regions) == 0:
            self._new_render_state = self._old_render_state
            return super().render_lines(crop)

        ret = super().render_lines(crop)
        self._dirty_regions.clear()

        self._new_render_state = self._old_render_state

        return ret

    @contextmanager
    def _preserved_refresh_state(self) -> ContextManager:
        repaint_required = self._repaint_required
        try:
            yield
        finally:
            self._repaint_required = repaint_required

    def _pre_render_lines(self) -> PreRenderState:

        def build_doc_y_to_render_y_table() -> dict[int, int]:
            """Build a dict mapping document y (row) to text area y."""
            if not visible_line_range:
                return []

            line_index, section_offset = offset_to_line_info[scroll_y]
            line_count = self.document.line_count
            table: dicxt[int, int] = {}
            y = -section_offset
            while line_index < line_count:
                table[line_index] = y
                y += len(wrap_offsets[line_index]) + 1
                if y not in visible_line_range:
                    break
                line_index += 1

            return table

        def doc_pos_to_xy(row, column) -> tuple[int, int]:
            try:
                y = doc_y_to_render_y_table[row]
            except KeyError:
                return -1, -1

            offsets = wrap_offsets[row]
            offset = 0
            physical_column = column
            for offset in offsets:
                if column >= offset:
                    y += 1
                    physical_column = column - offset
                else:
                    break
            return physical_column, y

        def snip_syntax(line_highlights, start, end):
            snipped = []
            for hl_start, hl_end, hl_name in line_highlights:
                if hl_end is None:
                    hl_end = end
                hl_start = max(start, hl_start) - start
                hl_end = min(end, hl_end) - start
                if hl_start <= hl_end:
                    snipped.append((hl_start, hl_end, hl_name))
            return snipped

        def add_pre_renders(y: int) -> None:

            nonlocal cursor_line_text

            def get_line_sections(section_offset):
                sections = get_sections(line_index)
                if not soft_wrap:
                    text = sections[0]
                    if scroll_x > 0:
                        # If horizontally scrolled, 'pretend' this line is the
                        # second of a wrapped line.
                        section_offset = 1
                        sections = [
                            text[:scroll_x],
                            text[scroll_x : text_width + scroll_x],
                        ]
                    else:
                        sections = [text[:text_width]]
                return sections, section_offset

            def calculate_selection_limits() -> tuple[int | None, int | None]:
                """Calculate the selection limits for the current document line."""
                sel_start = sel_end = None
                if line_index in selection_line_range:
                    if len(selection_line_range) == 1:
                        sel_start = selection_top_column
                        sel_len = selection_bottom_column - selection_top_column + 1
                    elif line_index == selection_top_row:
                        sel_start = selection_top_column
                        sel_len = MAX_LINE_LENGTH_X2
                    elif line_index == selection_bottom_row:
                        sel_start = 0
                        sel_len = selection_bottom_column
                    else:
                        sel_start = 0
                        sel_len = MAX_LINE_LENGTH_X2
                    sel_end = sel_start + sel_len
                return sel_start, sel_end

            def create_gutter_text():
                if gutter_width > 0:
                    if section_offset == 0 or not soft_wrap:
                        gutter_content = str(line_index + line_number_start)
                        gutter_text = f"{gutter_content:>{gutter_width_no_margin}}  "
                    else:
                        gutter_text = blank_gutter_text
                else:
                    gutter_text = blank_gutter_text
                return gutter_text

            def create_select_range() -> range:
                """Calculate the selection range for the current line section."""

                nonlocal sel_start, sel_end, line_text

                select_range = EMPTY_RANGE
                if sel_start is not None:
                    if sel_start <= sel_end and 0 <= sel_start <= text_length:
                        range_end = min(sel_end, text_length)
                        if not line_text and yy != cursor_y:
                            # Make sure that empty line show up as selected.
                            line_text = TextReprString.create("▌")
                            select_range = range(1, 0, -1)
                        elif sel_start < sel_end:
                            # The selection covers part of this line section.
                            select_range = range(sel_start, range_end)

                    # Adjust start/end ready for the next line section.
                    sel_start = max(0, sel_start - text_length)
                    sel_end = max(0, sel_end - text_length)

                return select_range

            y_offset = y + scroll_y
            if y_offset >= len(offset_to_line_info):
                repr_line = TextReprString.create("")
                text_repr_strings[y] = repr_line
                rendered_lines.append(PreRenderLine(repr_line, "", range(0), [], False))
                return

            line_index, section_offset = offset_to_line_info[y_offset]
            sections, section_offset = get_line_sections(section_offset)
            sel_start, sel_end = calculate_selection_limits()
            gutter_text = create_gutter_text()
            doc_line_highlights = highlights[line_index] if highlights else []

            syn_start = 0
            line_highlights = []
            tab_offset = 0
            for yy, doc_text in enumerate(sections, y - section_offset):
                line_text = TextReprString.create(
                    doc_text, self.indent_width, tab_offset=tab_offset
                )
                tab_offset = self.indent_width - len(line_text) % self.indent_width
                text_length = len(line_text)
                syn_end = syn_start + len(line_text)
                if yy in visible_line_range and yy not in text_repr_strings:
                    select_range = create_select_range()
                    if highlights:
                        line_highlights = snip_syntax(
                            doc_line_highlights, syn_start, syn_end
                        )
                    if yy == cursor_y:
                        cursor_line_text = line_text
                    rendered_lines.append(
                        PreRenderLine(
                            line_text,
                            gutter_text,
                            select_range,
                            line_highlights,
                            cursor_row == line_index,
                        )
                    )
                    text_repr_strings[yy] = line_text
                    gutter_text = blank_gutter_text
                syn_start = syn_end

        # Create local references to oft-used attributes and methods.
        full_width = self.size.width
        gutter_width = self.gutter_width
        text_width = full_width - gutter_width
        highlights = self._highlights if self._highlights and self.theme else None
        line_count = self.size.height
        if line_count < 1:
            # We have no visible lines.
            return PreRenderState([])

        line_number_start = self.line_number_start
        scroll_x, scroll_y = self.scroll_offset
        selection = self.selection
        soft_wrap = self.soft_wrap
        wrapped_document = self.wrapped_document

        # Local references to the wrapped document attribute and methods
        get_sections = wrapped_document.get_sections
        line_index_to_offsets = wrapped_document._line_index_to_offsets
        offset_to_line_info = wrapped_document._offset_to_line_info
        wrap_offsets = wrapped_document._wrap_offsets
        wrapped_height = wrapped_document.height  # Note: slowish property.

        visible_line_range = range(line_count)
        if self.show_line_numbers:
            gutter_width_no_margin = gutter_width - 2
            blank_gutter_text = " " * (gutter_width_no_margin + 2)
        else:
            gutter_width = 0
            blank_gutter_text = ""

        selection_top, selection_bottom = sorted(selection)
        selection_top_row, selection_top_column = selection_top
        selection_bottom_row, selection_bottom_column = selection_bottom
        if selection.is_empty:
            selection_line_range = EMPTY_RANGE
        else:
            selection_line_range = range(selection_top_row, selection_bottom_row + 1)

        doc_y_to_render_y_table = build_doc_y_to_render_y_table()
        cursor_row, cursor_column = selection.end
        cursor_char_x, cursor_y = doc_pos_to_xy(*selection.end)
        cursor_x = cursor_char_x
        if self._matching_bracket_location is not None:
            bracket_char_x, bracket_y = doc_pos_to_xy(*self._matching_bracket_location)
            bracket_x = bracket_char_x
        else:
            bracket_char_x = bracket_x = bracket_y = -1
        if not soft_wrap:
            cursor_char_x -= scroll_x
            bracket_x -= scroll_x
            bracket_char_x -= scroll_x

        cursor_line_text: str | None = None
        text_repr_strings: dict[int, TextReprString] = {}
        rendered_lines: list[PreRenderLine] = []
        for y in visible_line_range:
            if y not in text_repr_strings:
                add_pre_renders(y)

        if bracket_char_x >= 0:
            try:
                bracket_x = text_repr_strings[bracket_y].cell_offset(bracket_char_x)
            except IndexError:
                # This can occur when the cursor is beyond RHS.
                bracket_x = bracket_char_x = -1
        else:
            bracket_x = -1
        cursor_width = 1
        if cursor_line_text is not None:  # Should always be true.
            cursor_char_x = cursor_line_text.adjust_index_for_tabs(cursor_char_x)
            cursor_x = cursor_line_text.cell_offset(cursor_char_x)
            if cursor_char_x < len(cursor_line_text):
                cursor_width = cursor_line_text.cell_width(cursor_char_x)

        return PreRenderState(
            lines=rendered_lines,
            cursor=(self.cursor_is_on, cursor_x, cursor_y, cursor_width, cursor_char_x),
            size=self.size,
            gutter_width=gutter_width,
            bracket=(bracket_x, bracket_y, bracket_char_x),
        )

    def render_line(self, y: int) -> Strip:
        """Render a single line of the TextArea. Called by Textual.

        Args:
            y: Y Coordinate of line relative to the widget region.

        Returns:
            A rendered line.
        """
        state = self._old_render_state
        if y >= len(state.lines):
            return Strip.blank(self.size.width)
        if y + self.scroll_offset.y >= self.wrapped_document.height:
            return Strip.blank(self.size.width)

        # Get the text for this physical line.
        pre_render = state.lines[y]
        text = pre_render.text
        rich_line = Text(text + " ", end="")
        if theme := self._theme:
            theme.apply_css(self)
        if cursor_highlighted := pre_render.cursor_highlighted:
            cursor_line_style = theme.cursor_line_style if theme else None
            rich_line.stylize(cursor_line_style)

        # If this line is part of the selection, add selection styling.
        if sel_range := pre_render.select_range:
            selection_style = theme.selection_style if theme else None
            if selection_style is not None:
                if sel_range.step < 0:
                    rich_line = Text(
                        "▌", end="", style=Style(color=selection_style.bgcolor)
                    )
                else:
                    rich_line.stylize(
                        selection_style, start=sel_range.start, end=sel_range.stop
                    )

        # Add syntax highlighting.
        if (line_highlights := pre_render.syntax) and theme:
            get_highlight_from_theme = theme.syntax_styles.get
            for highlight_start, highlight_end, highlight_name in line_highlights:
                node_style = get_highlight_from_theme(highlight_name)
                if node_style is not None:
                    rich_line.stylize(node_style, highlight_start, highlight_end)

        # Highlight the cursor, taking care when it is on a bracket.
        draw_matched_brackets = False
        if self._matching_bracket_location is not None:
            if self.match_cursor_bracket:
                draw_matched_brackets = self.selection.is_empty

        cursor_is_on, cell_x, cell_y, _, char_x = state.cursor
        if cell_y == y:
            if draw_matched_brackets:
                matching_bracket_style = theme.bracket_matching_style if theme else None
                if matching_bracket_style:
                    rich_line.stylize(matching_bracket_style, char_x, char_x + 1)
            if cursor_is_on:
                cursor_style = theme.cursor_style if theme else None
                if cursor_style:
                    width = text.logical_character_width(char_x)
                    rich_line.stylize(cursor_style, char_x, char_x + width)

        # Add styling for a matching bracket.
        _, bracket_cell_y, bracket_char_x = state.bracket
        if theme and draw_matched_brackets:
            if bracket_cell_y == y and bracket_char_x >= 0:
                matching_bracket_style = theme.bracket_matching_style
                if matching_bracket_style:
                    rich_line.stylize(
                        matching_bracket_style, bracket_char_x, bracket_char_x + 1
                    )

        # Add gutter text.
        gutter_width = self.gutter_width
        gutter = Text("", end="")
        gutter_style = theme.gutter_style
        if self.show_line_numbers:
            if cursor_highlighted:
                gutter_style = theme.cursor_line_gutter_style
            gutter = Text(pre_render.gutter_text, style=gutter_style or "", end="")

        # Create strips for the gutter and line text.
        base_width = self.scrollable_content_region.size.width
        if not self.soft_wrap:
            base_width = max(self.virtual_size.width, self.region.size.width)
        target_width = base_width - gutter_width
        console = self.app.console
        gutter_segments = console.render(gutter)
        text_segments = list(
            console.render(rich_line, console.options.update_width(target_width))
        )
        gutter_strip = Strip(gutter_segments, cell_length=gutter_width)
        text_strip = Strip(text_segments)

        # Pad the line using the cursor line or base style.
        if cursor_highlighted:
            line_style = cursor_line_style
        else:
            line_style = theme.base_style if theme else None
        text_strip = text_strip.extend_cell_length(target_width, line_style)

        strip = Strip.join([gutter_strip, text_strip]).simplify()
        return strip.apply_style(
            theme.base_style
            if theme and theme.base_style is not None
            else self.rich_style
        )

    @property
    def text(self) -> str:
        """The entire text content of the document."""
        return self.document.text

    @text.setter
    def text(self, value: str) -> None:
        """Replace the text currently in the TextArea. This is an alias of `load_text`.

        Setting this value will clear the edit history.

        Args:
            value: The text to load into the TextArea.
        """
        self.load_text(value)

    @property
    def selected_text(self) -> str:
        """The text between the start and end points of the current selection."""
        start, end = self.selection
        return self.get_text_range(start, end)

    @property
    def matching_bracket_location(self) -> Location | None:
        """The location of the matching bracket, if there is one."""
        return self._matching_bracket_location

    def get_text_range(self, start: Location, end: Location) -> str:
        """Get the text between a start and end location.

        Args:
            start: The start location.
            end: The end location.

        Returns:
            The text between start and end.
        """
        start, end = sorted((start, end))
        return self.document.get_text_range(start, end)

    def edit(self, edit: Edit) -> EditResult:
        """Perform an Edit.

        Args:
            edit: The Edit to perform.

        Returns:
            Data relating to the edit that may be useful. The data returned
            may be different depending on the edit performed.
        """
        old_gutter_width = self.gutter_width
        result = edit.do(self)
        self.history.record(edit)
        new_gutter_width = self.gutter_width

        if old_gutter_width != new_gutter_width:
            self.wrapped_document.wrap(self.wrap_width, self.indent_width)
        else:
            self.wrapped_document.wrap_range(
                edit.top,
                edit.bottom,
                result.end_location,
            )

        self._refresh_size()
        edit.after(self)
        self._handle_change_affecting_highlighting()
        self.post_message(self.Changed(self))
        return result

    def undo(self) -> None:
        """Undo the edits since the last checkpoint (the most recent batch of edits)."""
        if edits := self.history._pop_undo():
            self._undo_batch(edits)

    def action_undo(self) -> None:
        """Undo the edits since the last checkpoint (the most recent batch of edits)."""
        self.undo()

    def redo(self) -> None:
        """Redo the most recently undone batch of edits."""
        if edits := self.history._pop_redo():
            self._redo_batch(edits)

    def action_redo(self) -> None:
        """Redo the most recently undone batch of edits."""
        self.redo()

    def _undo_batch(self, edits: Sequence[Edit]) -> None:
        """Undo a batch of Edits.

        The sequence must be chronologically ordered by edit time.

        There must be no edits missing from the sequence, or the resulting content
        will be incorrect.

        Args:
            edits: The edits to undo, in the order they were originally performed.
        """
        if not edits:
            return

        old_gutter_width = self.gutter_width
        minimum_top = edits[-1].top
        maximum_old_bottom = (0, 0)
        maximum_new_bottom = (0, 0)
        for edit in reversed(edits):
            edit.undo(self)
            end_location = (
                edit._edit_result.end_location if edit._edit_result else (0, 0)
            )
            if edit.top < minimum_top:
                minimum_top = edit.top
            if end_location > maximum_old_bottom:
                maximum_old_bottom = end_location
            if edit.bottom > maximum_new_bottom:
                maximum_new_bottom = edit.bottom

        new_gutter_width = self.gutter_width
        if old_gutter_width != new_gutter_width:
            self.wrapped_document.wrap(self.wrap_width, self.indent_width)
        else:
            self.wrapped_document.wrap_range(
                minimum_top, maximum_old_bottom, maximum_new_bottom
            )

        self._refresh_size()
        for edit in reversed(edits):
            edit.after(self)
        self._handle_change_affecting_highlighting()
        self.post_message(self.Changed(self))

    def _redo_batch(self, edits: Sequence[Edit]) -> None:
        """Redo a batch of Edits in order.

        The sequence must be chronologically ordered by edit time.

        Edits are applied from the start of the sequence to the end.

        There must be no edits missing from the sequence, or the resulting content
        will be incorrect.

        Args:
            edits: The edits to redo.
        """
        if not edits:
            return

        old_gutter_width = self.gutter_width
        minimum_top = edits[0].top
        maximum_old_bottom = (0, 0)
        maximum_new_bottom = (0, 0)
        for edit in edits:
            edit.do(self, record_selection=False)
            end_location = (
                edit._edit_result.end_location if edit._edit_result else (0, 0)
            )
            if edit.top < minimum_top:
                minimum_top = edit.top
            if end_location > maximum_new_bottom:
                maximum_new_bottom = end_location
            if edit.bottom > maximum_old_bottom:
                maximum_old_bottom = edit.bottom

        new_gutter_width = self.gutter_width
        if old_gutter_width != new_gutter_width:
            self.wrapped_document.wrap(self.wrap_width, self.indent_width)
        else:
            self.wrapped_document.wrap_range(
                minimum_top,
                maximum_old_bottom,
                maximum_new_bottom,
            )

        self._refresh_size()
        for edit in edits:
            edit.after(self)
        self._handle_change_affecting_highlighting()
        self.post_message(self.Changed(self))

    async def _on_key(self, event: events.Key) -> None:
        """Handle key presses which correspond to document inserts."""
        self._restart_blink()
        if self.read_only:
            return

        key = event.key
        insert_values = {
            "enter": "\n",
        }
        if self.tab_behavior == "indent":
            if key == "escape":
                event.stop()
                event.prevent_default()
                self.screen.focus_next()
                return
            if self.indent_type == "tabs":
                insert_values["tab"] = TAB
            else:
                insert_values["tab"] = " " * self._find_columns_to_next_tab_stop()

        if event.is_printable or key in insert_values:
            event.stop()
            event.prevent_default()
            insert = insert_values.get(key, event.character)
            # `insert` is not None because event.character cannot be
            # None because we've checked that it's printable.
            assert insert is not None
            start, end = self.selection
            self._replace_via_keyboard(insert, start, end)

    def _find_columns_to_next_tab_stop(self) -> int:
        """Get the location of the next tab stop after the cursors position on the current line.

        If the cursor is already at a tab stop, this returns the *next* tab stop location.

        Returns:
            The number of cells to the next tab stop from the current cursor column.
        """
        cursor_row, cursor_column = self.cursor_location
        line_text = self.document[cursor_row]
        indent_width = self.indent_width
        if not line_text:
            return indent_width

        width_before_cursor = self.get_column_width(cursor_row, cursor_column)
        spaces_to_insert = indent_width - (
            (indent_width + width_before_cursor) % indent_width
        )

        return spaces_to_insert

    def get_target_document_location(self, event: MouseEvent) -> Location:
        """Given a MouseEvent, return the row and column offset of the event in document-space.

        Args:
            event: The MouseEvent.

        Returns:
            The location of the mouse event within the document.
        """
        scroll_x, scroll_y = self.scroll_offset
        target_x = event.x - self.gutter_width + scroll_x - self.gutter.left
        target_y = event.y + scroll_y - self.gutter.top
        location = self.wrapped_document.offset_to_location(Offset(target_x, target_y))
        return location

    @property
    def gutter_width(self) -> int:
        """The width of the gutter (the left column containing line numbers).

        Returns:
            The cell-width of the line number column. If `show_line_numbers` is `False` returns 0.
        """
        # The longest number in the gutter plus two extra characters: `│ `.
        gutter_margin = 2
        gutter_width = (
            len(str(self.document.line_count - 1 + self.line_number_start))
            + gutter_margin
            if self.show_line_numbers
            else 0
        )
        return gutter_width

    def _on_mount(self, event: events.Mount) -> None:

        def text_selection_started(screen: Screen) -> None:
            """Signal callback to unselect when arbitrary text selection starts."""
            self.selection = Selection(self.cursor_location, self.cursor_location)

        self.screen.text_selection_started_signal.subscribe(
            self, text_selection_started, immediate=True
        )

        # When `app.theme` reactive is changed, reset the theme to clear cached styles.
        self.watch(self.app, "theme", self._app_theme_changed, init=False)
        self.blink_timer = self.set_interval(
            0.5,
            self._toggle_cursor_blink_visible,
            pause=not (self.cursor_blink and self.has_focus),
        )

    def _toggle_cursor_blink_visible(self) -> None:
        """Toggle visibility of the cursor for the purposes of 'cursor blink'."""
        self._cursor_visible = not self._cursor_visible
        _, cursor_y = self._cursor_offset
        self._trigger_repaint()

    def _watch__cursor_visible(self) -> None:
        """When the cursor visibility is toggled, ensure the row is refreshed."""
        _, cursor_y = self._cursor_offset
        self._trigger_repaint()

    def _restart_blink(self) -> None:
        """Reset the cursor blink timer."""
        if self.cursor_blink:
            self._cursor_visible = True
            self.blink_timer.reset()

    def _pause_blink(self, visible: bool = True) -> None:
        """Pause the cursor blinking but ensure it stays visible."""
        self._cursor_visible = visible
        self.blink_timer.pause()

    @property
    def cursor_is_on(self) -> bool:
        """True if the cursor currently visible."""
        return self.has_focus and (self._cursor_visible or not self.cursor_blink)

    async def _on_mouse_down(self, event: events.MouseDown) -> None:
        """Update the cursor position, and begin a selection using the mouse."""
        target = self.get_target_document_location(event)
        self.selection = Selection.cursor(target)
        self._selecting = True
        # Capture the mouse so that if the cursor moves outside the
        # TextArea widget while selecting, the widget still scrolls.
        self.capture_mouse()
        self._pause_blink(visible=True)
        self.history.checkpoint()

    async def _on_mouse_move(self, event: events.MouseMove) -> None:
        """Handles click and drag to expand and contract the selection."""
        if self._selecting:
            target = self.get_target_document_location(event)
            selection_start, _ = self.selection
            self.selection = Selection(selection_start, target)

    def _end_mouse_selection(self) -> None:
        """Finalize the selection that has been made using the mouse."""
        if self._selecting:
            self._selecting = False
            self.release_mouse()
            self.record_cursor_width()
            self._restart_blink()

    async def _on_mouse_up(self, event: events.MouseUp) -> None:
        """Finalize the selection that has been made using the mouse."""
        self._end_mouse_selection()

    async def _on_hide(self, event: events.Hide) -> None:
        """Finalize the selection that has been made using the mouse when the widget is hidden."""
        self._end_mouse_selection()

    async def _on_paste(self, event: events.Paste) -> None:
        """When a paste occurs, insert the text from the paste event into the document."""
        if self.read_only:
            return
        if result := self._replace_via_keyboard(event.text, *self.selection):
            self.move_cursor(result.end_location)

    def cell_width_to_column_index(self, cell_width: int, row_index: int) -> int:
        """Return the column that the cell width corresponds to on the given row.

        Args:
            cell_width: The cell width to convert.
            row_index: The index of the row to examine.

        Returns:
            The column corresponding to the cell width on that row.
        """
        line = self.document[row_index]
        return cell_width_to_column_index(line, cell_width, self.indent_width)

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
        self._recompute_cursor_offset()

        x, y = self._cursor_offset
        scroll_offset = self.scroll_to_region(
            Region(x, y, width=3, height=1),
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
            start, _end = self.selection
            self.selection = Selection(start, location)
        else:
            self.selection = Selection.cursor(location)

        if record_width:
            self.record_cursor_width()

        if center:
            self.scroll_cursor_visible(center)

        self.history.checkpoint()
        self._trigger_repaint()

    def move_cursor_relative(
        self,
        rows: int = 0,
        columns: int = 0,
        select: bool = False,
        center: bool = False,
        record_width: bool = True,
    ) -> None:
        """Move the cursor relative to its current location in document-space.

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
        _start, end = self.selection
        current_row, current_column = end
        target = clamp_visitable((current_row + rows, current_column + columns))
        self.move_cursor(target, select, center, record_width)

    def select_line(self, index: int) -> None:
        """Select all the text in the specified line.

        Args:
            index: The index of the line to select (starting from 0).
        """
        try:
            line = self.document[index]
        except IndexError:
            return
        else:
            self.selection = Selection((index, 0), (index, len(line)))
            self.record_cursor_width()

    def action_select_line(self) -> None:
        """Select all the text on the current line."""
        cursor_row, _ = self.cursor_location
        self.select_line(cursor_row)

    def select_all(self) -> None:
        """Select all of the text in the `TextArea`."""
        last_line = self.document.line_count - 1
        length_of_last_line = len(self.document[last_line])
        selection_start = (0, 0)
        selection_end = (last_line, length_of_last_line)
        self.selection = Selection(selection_start, selection_end)
        self.record_cursor_width()

    def action_select_all(self) -> None:
        """Select all the text in the document."""
        self.select_all()

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
    def cursor_screen_offset(self) -> Offset:
        """The offset of the cursor relative to the screen."""
        cursor_x, cursor_y = self._cursor_offset
        scroll_x, scroll_y = self.scroll_offset
        region_x, region_y, _width, _height = self.content_region

        offset_x = region_x + cursor_x - scroll_x + self.gutter_width
        offset_y = region_y + cursor_y - scroll_y

        return Offset(offset_x, offset_y)

    @property
    def cursor_at_first_line(self) -> bool:
        """True if and only if the cursor is on the first line."""
        return self.selection.end[0] == 0

    @property
    def cursor_at_last_line(self) -> bool:
        """True if and only if the cursor is on the last line."""
        return self.selection.end[0] == self.document.line_count - 1

    @property
    def cursor_at_start_of_line(self) -> bool:
        """True if and only if the cursor is at column 0."""
        return self.selection.end[1] == 0

    @property
    def cursor_at_end_of_line(self) -> bool:
        """True if and only if the cursor is at the end of a row."""
        cursor_row, cursor_column = self.selection.end
        row_length = len(self.document[cursor_row])
        cursor_at_end = cursor_column == row_length
        return cursor_at_end

    @property
    def cursor_at_start_of_text(self) -> bool:
        """True if and only if the cursor is at location (0, 0)"""
        return self.selection.end == (0, 0)

    @property
    def cursor_at_end_of_text(self) -> bool:
        """True if and only if the cursor is at the very end of the document."""
        return self.cursor_at_last_line and self.cursor_at_end_of_line

    # ------ Cursor movement actions
    def action_cursor_left(self, select: bool = False) -> None:
        """Move the cursor one location to the left.

        If the cursor is at the left edge of the document, try to move it to
        the end of the previous line.

        If text is selected, move the cursor to the start of the selection.

        Args:
            select: If True, select the text while moving.
        """
        target = (
            self.get_cursor_left_location()
            if select or self.selection.is_empty
            else min(*self.selection)
        )
        self.move_cursor(target, select=select)

    def get_cursor_left_location(self) -> Location:
        """Get the location the cursor will move to if it moves left.

        Returns:
            The location of the cursor if it moves left.
        """
        return self.navigator.get_location_left(self.cursor_location)

    def action_cursor_right(self, select: bool = False) -> None:
        """Move the cursor one location to the right.

        If the cursor is at the end of a line, attempt to go to the start of the next line.

        If text is selected, move the cursor to the end of the selection.

        Args:
            select: If True, select the text while moving.
        """
        target = (
            self.get_cursor_right_location()
            if select or self.selection.is_empty
            else max(*self.selection)
        )
        self.move_cursor(target, select=select)

    def get_cursor_right_location(self) -> Location:
        """Get the location the cursor will move to if it moves right.

        Returns:
            the location the cursor will move to if it moves right.
        """
        return self.navigator.get_location_right(self.cursor_location)

    def action_cursor_down(self, select: bool = False) -> None:
        """Move the cursor down one cell.

        Args:
            select: If True, select the text while moving.
        """
        target = self.get_cursor_down_location()
        self.move_cursor(target, record_width=False, select=select)

    def get_cursor_down_location(self) -> Location:
        """Get the location the cursor will move to if it moves down.

        Returns:
            The location the cursor will move to if it moves down.
        """
        return self.navigator.get_location_below(self.cursor_location)

    def action_cursor_up(self, select: bool = False) -> None:
        """Move the cursor up one cell.

        Args:
            select: If True, select the text while moving.
        """
        target = self.get_cursor_up_location()
        self.move_cursor(target, record_width=False, select=select)

    def get_cursor_up_location(self) -> Location:
        """Get the location the cursor will move to if it moves up.

        Returns:
            The location the cursor will move to if it moves up.
        """
        return self.navigator.get_location_above(self.cursor_location)

    def action_cursor_line_end(self, select: bool = False) -> None:
        """Move the cursor to the end of the line."""
        location = self.get_cursor_line_end_location()
        self.move_cursor(location, select=select)

    def get_cursor_line_end_location(self) -> Location:
        """Get the location of the end of the current line.

        Returns:
            The (row, column) location of the end of the cursors current line.
        """
        return self.navigator.get_location_end(self.cursor_location)

    def action_cursor_line_start(self, select: bool = False) -> None:
        """Move the cursor to the start of the line."""
        target = self.get_cursor_line_start_location(smart_home=True)
        self.move_cursor(target, select=select)

    def get_cursor_line_start_location(self, smart_home: bool = False) -> Location:
        """Get the location of the start of the current line.

        Args:
            smart_home: If True, use "smart home key" behavior - go to the first
                non-whitespace character on the line, and if already there, go to
                offset 0. Smart home only works when wrapping is disabled.

        Returns:
            The (row, column) location of the start of the cursors current line.
        """
        return self.navigator.get_location_home(
            self.cursor_location, smart_home=smart_home
        )

    def action_cursor_word_left(self, select: bool = False) -> None:
        """Move the cursor left by a single word, skipping trailing whitespace.

        Args:
            select: Whether to select while moving the cursor.
        """
        if self.cursor_at_start_of_text:
            return
        target = self.get_cursor_word_left_location()
        self.move_cursor(target, select=select)

    def get_cursor_word_left_location(self) -> Location:
        """Get the location the cursor will jump to if it goes 1 word left.

        Returns:
            The location the cursor will jump on "jump word left".
        """
        cursor_row, cursor_column = self.cursor_location
        if cursor_row > 0 and cursor_column == 0:
            # Going to the previous row
            return cursor_row - 1, len(self.document[cursor_row - 1])

        # Staying on the same row
        line = self.document[cursor_row][:cursor_column]
        search_string = line.rstrip()
        matches = list(re.finditer(self._word_pattern, search_string))
        cursor_column = matches[-1].start() if matches else 0
        return cursor_row, cursor_column

    def action_cursor_word_right(self, select: bool = False) -> None:
        """Move the cursor right by a single word, skipping leading whitespace."""

        if self.cursor_at_end_of_text:
            return

        target = self.get_cursor_word_right_location()
        self.move_cursor(target, select=select)

    def get_cursor_word_right_location(self) -> Location:
        """Get the location the cursor will jump to if it goes 1 word right.

        Returns:
            The location the cursor will jump on "jump word right".
        """
        cursor_row, cursor_column = self.selection.end
        line = self.document[cursor_row]
        if cursor_row < self.document.line_count - 1 and cursor_column == len(line):
            # Moving to the line below
            return cursor_row + 1, 0

        # Staying on the same line
        search_string = line[cursor_column:]
        pre_strip_length = len(search_string)
        search_string = search_string.lstrip()
        strip_offset = pre_strip_length - len(search_string)

        matches = list(re.finditer(self._word_pattern, search_string))
        if matches:
            cursor_column += matches[0].start() + strip_offset
        else:
            cursor_column = len(line)

        return cursor_row, cursor_column

    def action_cursor_page_up(self) -> None:
        """Move the cursor and scroll up one page."""
        height = self.content_size.height
        _, cursor_location = self.selection
        target = self.navigator.get_location_at_y_offset(
            cursor_location,
            -height,
        )
        self.scroll_relative(y=-height, animate=False)
        self.move_cursor(target)

    def action_cursor_page_down(self) -> None:
        """Move the cursor and scroll down one page."""
        height = self.content_size.height
        _, cursor_location = self.selection
        target = self.navigator.get_location_at_y_offset(
            cursor_location,
            height,
        )
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
        return cell_len(expand_tabs_inline(line[:column], self.indent_width))

    def record_cursor_width(self) -> None:
        """Record the current cell width of the cursor.

        This is used where we navigate up and down through rows.
        If we're in the middle of a row, and go down to a row with no
        content, then we go down to another row, we want our cursor to
        jump back to the same offset that we were originally at.
        """
        cursor_x_offset, _ = self.wrapped_document.location_to_offset(
            self.cursor_location
        )
        self.navigator.last_x_offset = cursor_x_offset

    # --- Editor operations
    def insert(
        self,
        text: str,
        location: Location | None = None,
        *,
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
            An `EditResult` containing information about the edit.
        """
        if location is None:
            location = self.cursor_location
        return self.edit(Edit(text, location, location, maintain_selection_offset))

    def delete(
        self,
        start: Location,
        end: Location,
        *,
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
            An `EditResult` containing information about the edit.
        """
        return self.edit(Edit("", start, end, maintain_selection_offset))

    def replace(
        self,
        insert: str,
        start: Location,
        end: Location,
        *,
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
            An `EditResult` containing information about the edit.
        """
        return self.edit(Edit(insert, start, end, maintain_selection_offset))

    def clear(self) -> EditResult:
        """Delete all text from the document.

        Returns:
            An EditResult relating to the deletion of all content.
        """
        return self.delete((0, 0), self.document.end, maintain_selection_offset=False)

    def _delete_via_keyboard(
        self,
        start: Location,
        end: Location,
    ) -> EditResult | None:
        """Handle a deletion performed using a keyboard (as opposed to the API).

        Args:
            start: The start location of the text to delete.
            end: The end location of the text to delete.

        Returns:
            An EditResult or None if no edit was performed (e.g. on read-only mode).
        """
        if self.read_only:
            return None
        return self.delete(start, end, maintain_selection_offset=False)

    def _replace_via_keyboard(
        self,
        insert: str,
        start: Location,
        end: Location,
    ) -> EditResult | None:
        """Handle a replacement performed using a keyboard (as opposed to the API).

        Args:
            insert: The text to insert into the document.
            start: The start location of the text to replace.
            end: The end location of the text to replace.

        Returns:
            An EditResult or None if no edit was performed (e.g. on read-only mode).
        """
        if self.read_only:
            return None
        return self.replace(insert, start, end, maintain_selection_offset=False)

    def action_delete_left(self) -> None:
        """Deletes the character to the left of the cursor and updates the cursor location.

        If there's a selection, then the selected range is deleted."""

        selection = self.selection
        start, end = selection

        if selection.is_empty:
            end = self.get_cursor_left_location()

        self._delete_via_keyboard(start, end)

    def action_delete_right(self) -> None:
        """Deletes the character to the right of the cursor and keeps the cursor at the same location.

        If there's a selection, then the selected range is deleted."""

        selection = self.selection
        start, end = selection

        if selection.is_empty:
            end = self.get_cursor_right_location()

        self._delete_via_keyboard(start, end)

    def action_delete_line(self) -> None:
        """Deletes the lines which intersect with the selection."""
        self._delete_cursor_line()

    def _delete_cursor_line(self) -> EditResult | None:
        """Deletes the line (including the line terminator) that the cursor is on."""
        start, end = self.selection
        start, end = sorted((start, end))
        start_row, _start_column = start
        end_row, end_column = end

        # Generally editors will only delete line the end line of the
        # selection if the cursor is not at column 0 of that line.
        if start_row != end_row and end_column == 0 and end_row >= 0:
            end_row -= 1

        from_location = (start_row, 0)
        to_location = (end_row + 1, 0)

        deletion = self._delete_via_keyboard(from_location, to_location)
        if deletion is not None:
            self.move_cursor_relative(columns=end_column, record_width=False)
        return deletion

    def action_cut(self) -> None:
        """Cut text (remove and copy to clipboard)."""
        if self.read_only:
            return
        start, end = self.selection
        if start == end:
            edit_result = self._delete_cursor_line()
        else:
            edit_result = self._delete_via_keyboard(start, end)

        if edit_result is not None:
            self.app.copy_to_clipboard(edit_result.replaced_text)

    def action_copy(self) -> None:
        """Copy selection to clipboard."""
        selected_text = self.selected_text
        if selected_text:
            self.app.copy_to_clipboard(selected_text)

    def action_paste(self) -> None:
        """Paste from local clipboard."""
        if self.read_only:
            return
        clipboard = self.app.clipboard
        if result := self._replace_via_keyboard(clipboard, *self.selection):
            self.move_cursor(result.end_location)

    def action_delete_to_start_of_line(self) -> None:
        """Deletes from the cursor location to the start of the line."""
        from_location = self.selection.end
        to_location = self.get_cursor_line_start_location()
        self._delete_via_keyboard(from_location, to_location)

    def action_delete_to_end_of_line(self) -> None:
        """Deletes from the cursor location to the end of the line."""
        from_location = self.selection.end
        to_location = self.get_cursor_line_end_location()
        self._delete_via_keyboard(from_location, to_location)

    async def action_delete_to_end_of_line_or_delete_line(self) -> None:
        """Deletes from the cursor location to the end of the line, or deletes the line.

        The line will be deleted if the line is empty.
        """
        # Assume we're just going to delete to the end of the line.
        action = "delete_to_end_of_line"
        if self.get_cursor_line_start_location() == self.get_cursor_line_end_location():
            # The line is empty, so we'll simply remove the line itself.
            action = "delete_line"
        elif (
            self.selection.start
            == self.selection.end
            == self.get_cursor_line_end_location()
        ):
            # We're at the end of the line, so the kill delete operation
            # should join the next line to this.
            action = "delete_right"
        await self.run_action(action)

    def action_delete_word_left(self) -> None:
        """Deletes the word to the left of the cursor and updates the cursor location."""
        if self.cursor_at_start_of_text:
            return

        # If there's a non-zero selection, then "delete word left" typically only
        # deletes the characters within the selection range, ignoring word boundaries.
        start, end = self.selection
        if start != end:
            self._delete_via_keyboard(start, end)
            return

        to_location = self.get_cursor_word_left_location()
        self._delete_via_keyboard(self.selection.end, to_location)

    def action_delete_word_right(self) -> None:
        """Deletes the word to the right of the cursor and keeps the cursor at the same location.

        Note that the location that we delete to using this action is not the same
        as the location we move to when we move the cursor one word to the right.
        This action does not skip leading whitespace, whereas cursor movement does.
        """
        if self.cursor_at_end_of_text:
            return

        start, end = self.selection
        if start != end:
            self._delete_via_keyboard(start, end)
            return

        cursor_row, cursor_column = end

        # Check the current line for a word boundary
        line = self.document[cursor_row][cursor_column:]
        matches = list(re.finditer(self._word_pattern, line))

        current_row_length = len(self.document[cursor_row])
        if matches:
            to_location = (cursor_row, cursor_column + matches[0].end())
        elif (
            cursor_row < self.document.line_count - 1
            and cursor_column == current_row_length
        ):
            to_location = (cursor_row + 1, 0)
        else:
            to_location = (cursor_row, current_row_length)

        self._delete_via_keyboard(end, to_location)


class IndexMapper:
    """An infinite list-like mapping from one index to another."""

    def __init__(self, base_map: MutableSequence[int]):
        self._base_map = base_map or [0]

    def __getitem__(self, index: int | None) -> int | None:
        if index is None:
            return None
        try:
            return self._base_map[index]
        except IndexError:
            return self._base_map[-1] + index - len(self._base_map) + 1


class _IdentityIndexMapper(IndexMapper):
    """A `Mapper` that maps 0->0, 1->1, ..."""

    def __init__(self):
        pass

    def __getitem__(self, index: int | None) -> int | None:
        return index


@lru_cache(maxsize=128)
def build_byte_to_tab_expanded_string_table(text: str, tab_size: int) -> Mapper:
    """Build a mapping of utf-8 byte offsets to TAB-expanded character positions.

    Args:
        text: The string to map.
        tab_size: The size setting to use for TAB expansion.

    Returns:
        A list-like object mapping byte index to character index.
    """
    if not text:
        return identity_index_mapper

    data = text.encode("utf-8")
    if len(data) == len(text) and TAB not in text:
        return identity_index_mapper

    offsets: MutableSequence[int] = array("L")
    char_offset = 0
    next_tabstop = 0
    for c in text:
        offsets.append(char_offset)
        if c == TAB:
            char_offset = next_tabstop
        else:
            ord_c = ord(c)
            if ord_c >= 0x80:
                offsets.append(char_offset)
                if ord_c >= 0x800:
                    offsets.append(char_offset)
                    if ord_c >= 0x10000:
                        offsets.append(char_offset)
            char_offset += 1

        if char_offset >= next_tabstop:
            next_tabstop += tab_size

    return IndexMapper(offsets)


@contextmanager
def temporary_query_point_range(
    query: Query,
    start_point: tuple[int, int] | None,
    end_point: tuple[int, int] | None,
) -> ContextManager[None]:
    """Temporarily change the start and/or end point for a tree-sitter Query.

    Args:
        query: The tree-sitter Query.
        start_point: The (row, column byte) to start the query at.
        end_point: The (row, column byte) to end the query at.
    """
    # Note: Although not documented for the tree-sitter Python API, an
    # end-point of (0, 0) means 'end of document'.
    default_point_range = [(0, 0), (0, 0)]

    point_range = list(default_point_range)
    if start_point is not None:
        point_range[0] = start_point
    if end_point is not None:
        point_range[1] = end_point
    query.set_point_range(point_range)
    try:
        yield None
    finally:
        query.set_point_range(default_point_range)


def build_difference_region(
    line_index: int,
    a: Sequence,
    b: Sequence,
    x_offset: int = 0,
) -> LineRegion:
    """Compare 2 sequences to create a line region covering the differences.

    The caller should only use this if a nd b are known to differ.
    """
    if a is None:
        return LineRegion(x_offset, line_index, len(b))
    elif b is None:
        return LineRegion(x_offset, line_index, len(a))

    start = 0
    for start, (ca, cb) in enumerate(zip(a, b)):
        if ca != cb:
            break
    end = max(len(a), len(b))
    return LineRegion(start + x_offset, line_index, end - start + 1)


def intersect_ranges(range_a, range_b) -> list[range]:
    if range_a.step < 0:
        range_b = range(0)
    if range_b.step < 0:
        range_b = range(0)
    if range_a.start > range_b.start:
        range_a, range_b = range_b, range_a
    elif range_a.start == range_b.start:
        if range_a.stop > range_b.stop:
            range_a, range_b = range_b, range_a
    overlap = range_a.stop - range_b.start
    if overlap <= 0:
        # Ranges do not overlap
        before = range_a
        common = []
        after = range_b
    else:
        before = range(range_a.start, range_a.stop - overlap)
        common = range(range_a.stop - overlap, range_a.stop)
        after = range(range_b.start + overlap, range_b.stop)
    return before, common, after


def character_cell_size(char: str) -> int:
    """Calculate the cell size for a character.

    This is athing wrapper around get_character_cell_size, which treats the TAB
    character as width == 1.
    """
    if char == TAB:
        return 1
    else:
        return get_character_cell_size(char)


identity_index_mapper = _IdentityIndexMapper()
