from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, Optional, Tuple

from rich.style import Style
from rich.text import Text

from textual._tree_sitter import TREE_SITTER
from textual.expand_tabs import expand_tabs_inline

if TYPE_CHECKING:
    from tree_sitter import Language
    from tree_sitter.binding import Query

from textual import events, log
from textual._cells import cell_len
from textual._types import Literal, Protocol, runtime_checkable
from textual.binding import Binding
from textual.document import (
    Document,
    DocumentBase,
    EditResult,
    Location,
    Selection,
    SyntaxAwareDocument,
    TextAreaTheme,
)
from textual.events import MouseEvent
from textual.geometry import Offset, Region, Size, Spacing, clamp
from textual.reactive import Reactive, reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip

_OPENING_BRACKETS = {"{": "}", "[": "]", "(": ")"}
_CLOSING_BRACKETS = {v: k for k, v in _OPENING_BRACKETS.items()}
_TREE_SITTER_PATH = Path(__file__) / "../../../../tree-sitter/"
_HIGHLIGHTS_PATH = _TREE_SITTER_PATH / "highlights/"


StartColumn = int
EndColumn = Optional[int]
HighlightName = str
Highlight = Tuple[StartColumn, EndColumn, HighlightName]
"""A tuple representing a syntax highlight within one line."""


@dataclass
class TextAreaLanguage:
    name: str
    language: "Language"
    highlight_query: str | "Query"


class TextArea(ScrollView, can_focus=True):
    DEFAULT_CSS = """\
$text-area-active-line-bg: white 8%;

TextArea {
    background: $panel 70%;
    width: 1fr;
    height: 1fr;
}
TextArea:focus {
    background: $panel;
}
TextArea:focus > .text-area--cursor-line {
    background: $text-area-active-line-bg;
}
TextArea > .text-area--cursor-line {
    background: white 5%;
}
TextArea:focus > .text-area--cursor-line-gutter {
    color: $text;
    background: $text-area-active-line-bg;
}
TextArea > .text-area--cursor-line-gutter {
    color: $text 65%;
    background: $text-area-active-line-bg;
}
TextArea:focus > .text-area--gutter {
    color: $text-muted 45%;
}
TextArea > .text-area--gutter {
    color: $text-muted 35%;
}
TextArea:focus > .text-area--cursor {
    color: black 90%;
    background: white 80%;
}
TextArea > .text-area--cursor {
    color: black 90%;
    background: white 25%;
}
TextArea:focus > .text-area--selection {
    background: $primary;
}
TextArea > .text-area--selection {
    background: $primary 65%;
}
TextArea:focus > .text-area--matching-bracket {
    color: $text;
    background: white 20%;
    text-style: bold underline;
}
TextArea > .text-area--matching-bracket {
    background: ;
    text-style: ;
}
"""

    BINDINGS = [
        Binding("escape", "screen.focus_next", "Shift Focus", show=False),
        # Cursor movement
        Binding("up", "cursor_up", "cursor up", show=False),
        Binding("down", "cursor_down", "cursor down", show=False),
        Binding("left", "cursor_left", "cursor left", show=False),
        Binding("right", "cursor_right", "cursor right", show=False),
        Binding("ctrl+left", "cursor_word_left", "cursor word left", show=False),
        Binding("ctrl+right", "cursor_word_right", "cursor word right", show=False),
        Binding("home,ctrl+a", "cursor_line_start", "cursor line start", show=False),
        Binding("end,ctrl+e", "cursor_line_end", "cursor line end", show=False),
        Binding("pageup", "cursor_page_up", "cursor page up", show=False),
        Binding("pagedown", "cursor_page_down", "cursor page down", show=False),
        # Making selections (generally holding the shift key and moving cursor)
        Binding(
            "ctrl+shift+left",
            "cursor_word_left(True)",
            "cursor left word select",
            show=False,
        ),
        Binding(
            "ctrl+shift+right",
            "cursor_word_right(True)",
            "cursor right word select",
            show=False,
        ),
        Binding(
            "shift+home",
            "cursor_line_start(True)",
            "cursor line start select",
            show=False,
        ),
        Binding(
            "shift+end", "cursor_line_end(True)", "cursor line end select", show=False
        ),
        Binding("shift+up", "cursor_up(True)", "cursor up select", show=False),
        Binding("shift+down", "cursor_down(True)", "cursor down select", show=False),
        Binding("shift+left", "cursor_left(True)", "cursor left select", show=False),
        Binding("shift+right", "cursor_right(True)", "cursor right select", show=False),
        # Shortcut ways of making selections
        # Binding("f5", "select_word", "select word", show=False),
        Binding("f6", "select_line", "select line", show=False),
        Binding("f7", "select_all", "select all", show=False),
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
    | ctrl+x                 | Delete the current line.                     |
    | ctrl+u                 | Delete from cursor to the start of the line. |
    | ctrl+k                 | Delete from cursor to the end of the line.   |
    | f6                     | Select the current line.                     |
    | f7                     | Select all text in the document.             |
    """

    language: Reactive[str | None] = reactive(None, always_update=True)
    """The language to use.

    This must be set to a valid, non-None value for syntax highlighting to work.

    If the value is a string, a built-in language parser will be used if available.

    If you wish to use an unsupported language, you'll have to register
    it first using `register_language`.
    """

    theme: Reactive[str | TextAreaTheme] = reactive(
        TextAreaTheme.default(), always_update=True, init=True
    )
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

    match_cursor_bracket: Reactive[bool] = reactive(True)
    """If the cursor is at a bracket, highlight the matching bracket (if found)."""

    cursor_blink: Reactive[bool] = reactive(True)
    """True if the cursor should blink."""

    _cursor_blink_visible: Reactive[bool] = reactive(True, repaint=False)
    """Indicates where the cursor is in the blink cycle. If it's currently
    not visible due to blinking, this is False."""

    def __init__(
        self,
        text: str = "",
        *,
        language: str | None = None,
        theme: str | TextAreaTheme | None = TextAreaTheme.default(),
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Construct a new `TextArea`.

        Args:
            name: The name of the `TextArea` widget.
            id: The ID of the widget, used to refer to it from Textual CSS.
            classes: One or more Textual CSS compatible class names separated by spaces.
            disabled: True if the widget is disabled.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        self.document = self._document_factory(text, language)
        """The document this widget is currently editing."""

        self._languages: dict[str, TextAreaLanguage] = {}
        """Maps language names to their TextAreaLanguage metadata."""

        if isinstance(theme, str):
            theme = TextAreaTheme.get_by_name(theme)

        self.theme: TextAreaTheme = theme
        """The theme of the `TextArea`."""

        self.indent_type: Literal["tabs", "spaces"] = "spaces"
        """Whether to indent using tabs or spaces."""

        self._word_pattern = re.compile(r"(?<=\W)(?=\w)|(?<=\w)(?=\W)")
        """Compiled regular expression for what we consider to be a 'word'."""

        self._last_intentional_cell_width: int = 0
        """Tracks the last column (measured in terms of cell length, since we care here about where the cursor
        visually moves rather than logical characters) the user explicitly navigated to so that we can reset to it
        whenever possible."""

        self._undo_stack: list[Undoable] = []
        """A stack (the end of the list is the top of the stack) for tracking edits."""

        self._selecting = False
        """True if we're currently selecting text using the mouse, otherwise False."""

        self._matching_bracket_location: Location | None = None
        """The location (row, column) of the bracket which matches the bracket the
        cursor is currently at. If the cursor is at a bracket, or there's no matching
        bracket, this will be `None`."""

        self._highlights: dict[int, list[Highlight]] = defaultdict(list)
        """Mapping line numbers to the set of highlights for that line."""

        self._highlight_query: "Query" | None = None
        """The query that's currently being used for highlighting."""

    def _get_builtin_highlight_query(self, language_name: str) -> str:
        try:
            highlight_query_path = (
                Path(_HIGHLIGHTS_PATH.resolve()) / f"{language_name}.scm"
            )
            highlight_query = highlight_query_path.read_text()
        except OSError:
            highlight_query = ""

        return highlight_query

    def _build_highlight_map(self) -> None:
        """Query the tree for ranges to highlights, and update the internal highlights mapping."""

        highlights = self._highlights
        highlights.clear()
        if not self._highlight_query:
            return

        captures = self.document.query_syntax_tree(self._highlight_query)
        for capture in captures:
            node, highlight_name = capture
            node_start_row, node_start_column = node.start_point
            node_end_row, node_end_column = node.end_point

            if node_start_row == node_end_row:
                highlight = (node_start_column, node_end_column, highlight_name)
                highlights[node_start_row].append(highlight)
            else:
                # Add the first line of the node range
                highlights[node_start_row].append(
                    (node_start_column, None, highlight_name)
                )

                # Add the middle lines - entire row of this node is highlighted
                for node_row in range(node_start_row + 1, node_end_row):
                    highlights[node_row].append((0, None, highlight_name))

                # Add the last line of the node range
                highlights[node_end_row].append((0, node_end_column, highlight_name))

    def _watch_selection(self, selection: Selection) -> None:
        """When the cursor moves, scroll it into view."""
        self.scroll_cursor_visible()
        cursor_location = selection.end
        cursor_row, cursor_column = cursor_location

        try:
            character = self.document[cursor_row][cursor_column]
        except IndexError:
            character = None

        # Record the location of a matching closing/opening bracket.
        match_location = None
        bracket_stack = []
        if character in _OPENING_BRACKETS:
            for candidate, candidate_location in self._yield_character_locations(
                cursor_location
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
        elif character in _CLOSING_BRACKETS:
            for (
                candidate,
                candidate_location,
            ) in self._yield_character_locations_reverse(cursor_location):
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

        self._matching_bracket_location = match_location
        if match_location is not None:
            match_row, match_column = match_location
            if match_row in range(*self._visible_line_indices):
                self.refresh_lines(match_row)

    def _validate_selection(self, selection: Selection) -> Selection:
        """Clamp the selection to valid locations."""
        start, end = selection
        clamp_visitable = self.clamp_visitable
        return Selection(clamp_visitable(start), clamp_visitable(end))

    def _watch_language(self, language: str | None) -> None:
        """When the language is updated, update the type of document."""
        self.document = self._document_factory(self.text, language)

    def _watch_show_line_numbers(self) -> None:
        """The line number gutter contributes to virtual size, so recalculate."""
        self._refresh_size()

    def _watch_indent_width(self) -> None:
        """Changing width of tabs will change document display width."""
        self._refresh_size()

    def _validate_theme(self, theme: str | TextAreaTheme) -> TextAreaTheme:
        if isinstance(theme, str):
            theme = TextAreaTheme.get_by_name(theme)
        return theme

    def register_language(
        self,
        language: str | "Language",
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
            language: A string referring to a builtin language or a tree-sitter `Language` object.
            highlight_query: The highlight query to use for syntax highlighting this language.
        """

        # If tree-sitter is unavailable, do nothing.
        if not TREE_SITTER:
            return

        from tree_sitter_languages import get_language

        if isinstance(language, str):
            language_name = language
            language = get_language(language_name)
        else:
            language_name = language.name

        # Update the custom languages. When changing the document,
        # we should first look in here for a language specification.
        # If nothing is found, then we can go to the builtin languages.
        self._languages[language_name] = TextAreaLanguage(
            name=language_name,
            language=language,
            highlight_query=highlight_query,
        )

    #     def _set_document(self, text: str, language: str | None) -> DocumentBase:
    #         if language in self._languages:
    #             # Load the custom language if it exists
    #             language_spec = self._languages[language]
    #             document_language = language_spec.language
    #             highlight_query = language_spec.highlight_query
    #         else:
    #             document_language = language
    #             highlight_query = self._get_builtin_highlight_query(language)
    #
    #         # Update the document and prepare the new query.
    #         self.document = SyntaxAwareDocument(text, document_language)
    #         if highlight_query:
    #             self._highlight_query = self.document.prepare_query(highlight_query)
    #         return self.document

    def _document_factory(self, text: str, language: str | None) -> DocumentBase:
        """Construct and return an appropriate document."""
        if TREE_SITTER and language:
            # Attempt to get the override language.
            text_area_language = self._languages.get(language, None)
            if text_area_language:
                document_language = text_area_language.language
                highlight_query = text_area_language.highlight_query
            else:
                document_language = language
                highlight_query = self._get_builtin_highlight_query(language)

            try:
                document = SyntaxAwareDocument(text, document_language)
            except RuntimeError:
                document = Document(text)
            else:
                self._highlight_query = document.prepare_query(highlight_query)
        elif language and not TREE_SITTER:
            log.warning("Syntax highlighting not available on this architecture.")
            document = Document(text)
        else:
            document = Document(text)

        return document

    @property
    def _visible_line_indices(self) -> tuple[int, int]:
        """Return the visible line indices as a tuple (top, bottom).

        Returns:
            A tuple (top, bottom) indicating the top and bottom visible line indices.
        """
        return self.scroll_offset.y, self.scroll_offset.y + self.size.height

    def load_text(self, text: str) -> None:
        """Load text from a string into the TextArea.

        Args:
            text: The text to load into the TextArea.
        """
        self.document = self._document_factory(text, self.language)
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

        theme = self.theme
        base_style = theme.base_style

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

        matching_bracket = self._matching_bracket_location
        match_cursor_bracket = self.match_cursor_bracket
        draw_matched_brackets = match_cursor_bracket and matching_bracket is not None

        cursor_row, cursor_column = end
        cursor_line_style = theme.cursor_line_style
        if cursor_row == line_index:
            line.stylize(cursor_line_style)

        # Selection styling
        if start != end and selection_top_row <= line_index <= selection_bottom_row:
            # If this row intersects with the selection range
            selection_style = theme.selection_style
            cursor_row, _ = end
            if line_character_count == 0 and line_index != cursor_row:
                # A simple highlight to show empty lines are included in the selection
                line = Text("▌", end="", style=Style(color=selection_style.bgcolor))
                line.set_length(self.virtual_size.width)
            else:
                if line_index == selection_top_row == selection_bottom_row:
                    # Selection within a single line
                    line.stylize(
                        selection_style,
                        start=selection_top_column,
                        end=selection_bottom_column,
                    )
                else:
                    # Selection spanning multiple lines
                    if line_index == selection_top_row:
                        line.stylize(
                            selection_style,
                            start=selection_top_column,
                            end=line_character_count,
                        )
                    elif line_index == selection_bottom_row:
                        line.stylize(selection_style, end=selection_bottom_column)
                    else:
                        line.stylize(selection_style, end=line_character_count)

        virtual_width, virtual_height = self.virtual_size

        # Highlight the cursor
        # active_line_style = self.get_component_rich_style("text-area--cursor-line")
        if cursor_row == line_index:
            draw_cursor = not self.cursor_blink or (
                self.cursor_blink and self._cursor_blink_visible
            )
            if draw_matched_brackets:
                matching_bracket_style = theme.bracket_matching_style
                line.stylize(
                    matching_bracket_style,
                    cursor_column,
                    cursor_column + 1,
                )

            if draw_cursor:
                # cursor_style = self.get_component_rich_style("text-area--cursor")
                cursor_style = theme.cursor_style
                line.stylize(cursor_style, cursor_column, cursor_column + 1)

        # Highlight the partner opening/closing bracket.
        if draw_matched_brackets:
            bracket_match_row, bracket_match_column = matching_bracket
            if bracket_match_row == line_index:
                # matching_bracket_style = self.get_component_rich_style(
                #     "text-area--matching-bracket"
                # )
                matching_bracket_style = theme.bracket_matching_style
                if matching_bracket_style:
                    line.stylize(
                        matching_bracket_style,
                        bracket_match_column,
                        bracket_match_column + 1,
                    )

        # Build the gutter text for this line
        gutter_width = self.gutter_width
        if self.show_line_numbers:
            if cursor_row == line_index:
                gutter_style = theme.cursor_line_gutter_style
                # gutter_style = self.get_component_rich_style(
                #     "text-area--cursor-line-gutter"
                # )
            else:
                # gutter_style = self.get_component_rich_style("text-area--gutter")
                gutter_style = theme.gutter_style

            gutter_width_no_margin = gutter_width - 2
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
        gutter_strip = Strip(gutter_segments, cell_length=gutter_width)
        text_strip = Strip(text_segments).crop(
            scroll_x, scroll_x + virtual_width - gutter_width
        )

        # Stylize the line the cursor is currently on.
        if cursor_row == line_index:
            expanded_length = max(virtual_width, self.size.width)
            text_strip = text_strip.extend_cell_length(expanded_length)

        # Join and return the gutter and the visible portion of this line
        strip = Strip.join([gutter_strip, text_strip]).simplify()
        return strip.apply_style(theme.base_style)

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
        start, end = sorted((start, end))
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
        self._build_highlight_map()
        return result

    async def _on_key(self, event: events.Key) -> None:
        """Handle key presses which correspond to document inserts."""
        key = event.key
        insert_values = {
            "tab": " " * self.indent_width if self.indent_type == "spaces" else "\t",
            "enter": "\n",
        }
        self._restart_blink()
        if event.is_printable or key in insert_values:
            event.stop()
            event.prevent_default()
            insert = insert_values.get(key, event.character)
            # `insert` is not None because event.character cannot be
            # None because we've checked that it's printable.
            assert insert is not None
            start, end = self.selection
            self.replace(insert, start, end, maintain_selection_offset=False)

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

    # --- Lower level event/key handling
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

    def _on_mount(self, _: events.Mount) -> None:
        self.blink_timer = self.set_interval(
            0.5,
            self._toggle_cursor_blink_visible,
            pause=not (self.cursor_blink and self.has_focus),
        )

    def _on_blur(self, _: events.Blur) -> None:
        self._pause_blink(visible=True)

    def _on_focus(self, _: events.Focus) -> None:
        self._restart_blink()

    def _toggle_cursor_blink_visible(self) -> None:
        """Toggle visibility of the cursor for the purposes of 'cursor blink'."""
        self._cursor_blink_visible = not self._cursor_blink_visible
        cursor_row, _ = self.cursor_location
        self.refresh_lines(cursor_row)

    def _restart_blink(self) -> None:
        """Reset the cursor blink timer."""
        if self.cursor_blink:
            self._cursor_blink_visible = True
            self.blink_timer.reset()

    def _pause_blink(self, visible: bool = True) -> None:
        """Pause the cursor blinking but ensure it stays visible."""
        self._cursor_blink_visible = visible
        self.blink_timer.pause()

    async def _on_mouse_down(self, event: events.MouseDown) -> None:
        """Update the cursor position, and begin a selection using the mouse."""
        target = self.get_target_document_location(event)
        self.selection = Selection.cursor(target)
        self._selecting = True
        # Capture the mouse so that if the cursor moves outside the
        # TextArea widget while selecting, the widget still scrolls.
        self.capture_mouse()
        self._pause_blink(visible=True)

    async def _on_mouse_move(self, event: events.MouseMove) -> None:
        """Handles click and drag to expand and contract the selection."""
        if self._selecting:
            target = self.get_target_document_location(event)
            selection_start, _ = self.selection
            self.selection = Selection(selection_start, target)

    async def _on_mouse_up(self, event: events.MouseUp) -> None:
        """Finalise the selection that has been made using the mouse."""
        self._selecting = False
        self.release_mouse()
        self.record_cursor_width()
        self._restart_blink()

    async def _on_paste(self, event: events.Paste) -> None:
        """When a paste occurs, insert the text from the paste event into the document."""
        self.replace(event.text, *self.selection)

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
            total_cell_offset += cell_len(expand_tabs_inline(character, tab_width))
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
        column_offset = cell_len(expand_tabs_inline(text, self.indent_width))
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
    def action_cursor_left(self, select: bool = False) -> None:
        """Move the cursor one location to the left.

        If the cursor is at the left edge of the document, try to move it to
        the end of the previous line.

        Args:
            select: If True, select the text while moving.
        """
        new_cursor_location = self.get_cursor_left_location()
        self.move_cursor(new_cursor_location, select=select)

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

    def action_cursor_right(self, select: bool = False) -> None:
        """Move the cursor one location to the right.

        If the cursor is at the end of a line, attempt to go to the start of the next line.

        Args:
            select: If True, select the text while moving.
        """
        target = self.get_cursor_right_location()
        self.move_cursor(target, select=select)

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

    def action_cursor_line_end(self, select: bool = False) -> None:
        """Move the cursor to the end of the line."""
        location = self.get_cursor_line_end_location()
        self.move_cursor(location, select=select)

    def get_cursor_line_end_location(self) -> Location:
        """Get the location of the end of the current line.

        Returns:
            The (row, column) location of the end of the cursors current line.
        """
        start, end = self.selection
        cursor_row, cursor_column = end
        target_column = len(self.document[cursor_row])
        return cursor_row, target_column

    def action_cursor_line_start(self, select: bool = False) -> None:
        """Move the cursor to the start of the line."""

        cursor_row, cursor_column = self.cursor_location
        line = self.document[cursor_row]

        first_non_whitespace = 0
        for index, code_point in enumerate(line):
            if not code_point.isspace():
                first_non_whitespace = index
                break

        if cursor_column <= first_non_whitespace and cursor_column != 0:
            target = self.get_cursor_line_start_location()
            self.move_cursor(target, select=select)
        else:
            target = cursor_row, first_non_whitespace
            self.move_cursor(target, select=select)

    def get_cursor_line_start_location(self) -> Location:
        """Get the location of the start of the current line.

        Returns:
            The (row, column) location of the start of the cursors current line.
        """
        _start, end = self.selection
        cursor_row, _cursor_column = end
        return cursor_row, 0

    def action_cursor_word_left(self, select: bool = False) -> None:
        """Move the cursor left by a single word, skipping trailing whitespace.

        Args:
            select: Whether to select while moving the cursor.
        """
        if self.cursor_at_start_of_document:
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

        if self.cursor_at_end_of_document:
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
        return cell_len(expand_tabs_inline(line[:column], self.indent_width))

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
        top, bottom = sorted((start, end))
        return self.edit(Edit("", top, bottom, maintain_selection_offset))

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

        if selection.is_empty:
            end = self.get_cursor_left_location()

        self.delete(start, end, maintain_selection_offset=False)

    def action_delete_right(self) -> None:
        """Deletes the character to the right of the cursor and keeps the cursor at the same location.

        If there's a selection, then the selected range is deleted."""

        selection = self.selection
        start, end = selection

        if selection.is_empty:
            end = self.get_cursor_right_location()

        self.delete(start, end, maintain_selection_offset=False)

    def action_delete_line(self) -> None:
        """Deletes the lines which intersect with the selection."""
        start, end = self.selection
        start, end = sorted((start, end))
        start_row, start_column = start
        end_row, end_column = end

        # Generally editors will only delete line the end line of the
        # selection if the cursor is not at column 0 of that line.
        if start_row != end_row and end_column == 0 and end_row >= 0:
            end_row -= 1

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

        to_location = self.get_cursor_word_left_location()
        self.delete(self.selection.end, to_location, maintain_selection_offset=False)

    def action_delete_word_right(self) -> None:
        """Deletes the word to the right of the cursor and keeps the cursor at the same location.

        Note that the location that we delete to using this action is not the same
        as the location we move to when we move the cursor one word to the right.
        This action does not skip leading whitespace, whereas cursor movement does.
        """
        if self.cursor_at_end_of_document:
            return

        start, end = self.selection
        if start != end:
            self.delete(start, end, maintain_selection_offset=False)
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
    _updated_selection: Selection | None = field(init=False, default=None)
    """Where the selection should move to after the replace happens."""

    def do(self, text_area: TextArea) -> EditResult:
        """Perform the edit operation.

        Args:
            text_area: The `TextArea` to perform the edit on.

        Returns:
            An `EditResult` containing information about the replace operation.
        """
        text = self.text

        edit_from = self.from_location
        edit_to = self.to_location

        # This code is mostly handling how we adjust TextArea.selection
        # when an edit is made to the document programmatically.
        # We want a user who is typing away to maintain their relative
        # position in the document even if an insert happens before
        # their cursor position.

        edit_top, edit_bottom = sorted((edit_from, edit_to))
        edit_bottom_row, edit_bottom_column = edit_bottom

        selection_start, selection_end = text_area.selection
        selection_start_row, selection_start_column = selection_start
        selection_end_row, selection_end_column = selection_end

        replace_result = text_area.document.replace_range(edit_from, edit_to, text)

        new_edit_to_row, new_edit_to_column = replace_result.end_location

        # TODO: We could maybe improve the situation where the selection
        #  and the edit range overlap with each other.
        column_offset = new_edit_to_column - edit_bottom_column
        target_selection_start_column = (
            selection_start_column + column_offset
            if edit_bottom_row == selection_start_row
            and edit_bottom_column <= selection_start_column
            else selection_start_column
        )
        target_selection_end_column = (
            selection_end_column + column_offset
            if edit_bottom_row == selection_end_row
            and edit_bottom_column <= selection_end_column
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
        """Undo the edit operation.

        Args:
            text_area: The `TextArea` to undo the insert operation on.

        Returns:
            An `EditResult` containing information about the replace operation.
        """
        raise NotImplementedError()

    def after(self, text_area: TextArea) -> None:
        """Possibly update the cursor location after the widget has been refreshed.

        Args:
            text_area: The `TextArea` this operation was performed on.
        """
        if self._updated_selection is not None:
            text_area.selection = self._updated_selection
        text_area.record_cursor_width()


@runtime_checkable
class Undoable(Protocol):
    """Protocol for actions performed in the text editor which can be done and undone.

    These are typically actions which affect the document (e.g. inserting and deleting
    text), but they can really be anything.

    To perform an edit operation, pass the Edit to `TextArea.edit()`"""

    def do(self, text_area: TextArea) -> Any:
        """Do the action.

        Args:
            The `TextArea` to perform the action on.

        Returns:
            Anything. This protocol doesn't prescribe what is returned.
        """

    def undo(self, text_area: TextArea) -> Any:
        """Undo the action.

        Args:
            The `TextArea` to perform the action on.

        Returns:
            Anything. This protocol doesn't prescribe what is returned.
        """
