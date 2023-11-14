from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, Optional, Tuple

from rich.style import Style
from rich.text import Text
from typing_extensions import Literal

from textual._text_editor_theme import TextEditorTheme
from textual._tree_sitter import TREE_SITTER
from textual.color import Color
from textual.document._document import (
    Document,
    DocumentBase,
    Location,
    Selection,
    _utf8_encode,
)
from textual.document._languages import BUILTIN_LANGUAGES
from textual.document._syntax_aware_document import (
    SyntaxAwareDocument,
    SyntaxAwareDocumentError,
)
from textual.expand_tabs import expand_tabs_inline
from textual.widgets._text_area import Edit, TextArea

if TYPE_CHECKING:
    from tree_sitter import Language

from textual import events, log
from textual._cells import cell_len
from textual.binding import Binding
from textual.events import Message, MouseEvent
from textual.geometry import clamp
from textual.reactive import Reactive, reactive
from textual.strip import Strip

_OPENING_BRACKETS = {"{": "}", "[": "]", "(": ")"}
_CLOSING_BRACKETS = {v: k for k, v in _OPENING_BRACKETS.items()}
_TREE_SITTER_PATH = Path(__file__).parent / "../tree-sitter/"
_HIGHLIGHTS_PATH = _TREE_SITTER_PATH / "highlights/"

StartColumn = int
EndColumn = Optional[int]
HighlightName = str
Highlight = Tuple[StartColumn, EndColumn, HighlightName]
"""A tuple representing a syntax highlight within one line."""


class ThemeDoesNotExist(Exception):
    """Raised when the user tries to use a theme which does not exist.
    This means a theme which is not builtin, or has not been registered.
    """


class LanguageDoesNotExist(Exception):
    """Raised when the user tries to use a language which does not exist.
    This means a language which is not builtin, or has not been registered.
    """


@dataclass
class TextEditorLanguage:
    """A container for a language which has been registered with the TextEditor.

    Attributes:
        name: The name of the language.
        language: The tree-sitter Language.
        highlight_query: The tree-sitter highlight query corresponding to the language, as a string.
    """

    name: str
    language: "Language"
    highlight_query: str


class TextEditor(TextArea, can_focus=True):
    DEFAULT_CSS = """\
TextEditor {
    width: 1fr;
    height: 1fr;
}
"""

    BINDINGS = [
        Binding("escape", "screen.focus_next", "Shift Focus", show=False),
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

    language: Reactive[str | None] = reactive(None, always_update=True, init=False)
    """The language to use.

    This must be set to a valid, non-None value for syntax highlighting to work.

    If the value is a string, a built-in language parser will be used if available.

    If you wish to use an unsupported language, you'll have to register
    it first using  [`TextEditor.register_language`][textual.widgets._text_editor.TextEditor.register_language].
    """

    theme: Reactive[str | None] = reactive(None, always_update=True, init=False)
    """The name of the theme to use.

    Themes must be registered using  [`TextEditor.register_theme`][textual.widgets._text_editor.TextEditor.register_theme] before they can be used.

    Syntax highlighting is only possible when the `language` attribute is set.
    """

    selection: Reactive[Selection] = reactive(
        Selection(), always_update=True, init=False
    )
    """The selection start and end locations (zero-based line_index, offset).

    This represents the cursor location and the current selection.

    The `Selection.end` always refers to the cursor location.

    If no text is selected, then `Selection.end == Selection.start` is True.

    The text selected in the document is available via the `TextEditor.selected_text` property.
    """

    show_line_numbers: Reactive[bool] = reactive(True)
    """True to show the line number column on the left edge, otherwise False.

    Changing this value will immediately re-render the `TextEditor`."""

    indent_width: Reactive[int] = reactive(4)
    """The width of tabs or the multiple of spaces to align to on pressing the `tab` key.

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

    @dataclass
    class Changed(Message):
        """Posted when the content inside the TextEditor changes.

        Handle this message using the `on` decorator - `@on(TextEditor.Changed)`
        or a method named `on_text_editor_changed`.
        """

        text_editor: TextEditor
        """The `text_editor` that sent this message."""

        @property
        def control(self) -> TextEditor:
            """The `TextEditor` that sent this message."""
            return self.text_editor

    @dataclass
    class SelectionChanged(Message):
        """Posted when the selection changes.

        This includes when the cursor moves or when text is selected."""

        selection: Selection
        """The new selection."""
        text_editor: TextEditor
        """The `text_editor` that sent this message."""

        @property
        def control(self) -> TextEditor:
            return self.text_editor

    def __init__(
        self,
        text: str = "",
        *,
        language: str | None = None,
        theme: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Construct a new `TextEditor`.

        Args:
            text: The initial text to load into the TextEditor.
            language: The language to use.
            theme: The theme to use.
            name: The name of the `TextEditor` widget.
            id: The ID of the widget, used to refer to it from Textual CSS.
            classes: One or more Textual CSS compatible class names separated by spaces.
            disabled: True if the widget is disabled.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._initial_text = text

        self._languages: dict[str, TextEditorLanguage] = {}
        """Maps language names to TextAreaLanguage."""

        self._themes: dict[str, TextEditorTheme] = {}
        """Maps theme names to TextEditorTheme."""

        self.indent_type: Literal["tabs", "spaces"] = "spaces"
        """Whether to indent using tabs or spaces."""

        self._last_intentional_cell_width: int = 0
        """Tracks the last column (measured in terms of cell length, since we care here about where the cursor
        visually moves rather than logical characters) the user explicitly navigated to so that we can reset to it
        whenever possible."""

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

        self.document: DocumentBase = Document(text)
        """The document this widget is currently editing."""

        self._theme: TextEditorTheme | None = None
        """The `TextEditorTheme` corresponding to the set theme name. When the `theme`
        reactive is set as a string, the watcher will update this attribute to the
        corresponding `TextEditorTheme` object."""

        self.language = language

        self.theme = theme

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
        except OSError as e:
            log.warning(f"Unable to load highlight query. {e}")
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
        cursor_location = selection.end
        cursor_row, cursor_column = cursor_location

        try:
            character = self.document[cursor_row][cursor_column]
        except IndexError:
            character = ""

        # Record the location of a matching closing/opening bracket.
        match_location = self.find_matching_bracket(character, cursor_location)
        self._matching_bracket_location = match_location
        if match_location is not None:
            match_row, match_column = match_location
            if match_row in range(*self._visible_line_indices):
                self.refresh_lines(match_row)

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
        bracket_stack = []
        if bracket in _OPENING_BRACKETS:
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
        if language is not None and language not in self.available_languages:
            raise LanguageDoesNotExist(
                f"{language!r} is not a builtin language, or it has not been registered. "
                f"To use a custom language, register it first using `register_language`, "
                f"then switch to it by setting the `TextEditor.language` attribute."
            )

        self._set_document(
            self.document.text if self.document is not None else self._initial_text,
            language,
        )
        self._initial_text = ""

    def _watch_show_line_numbers(self) -> None:
        """The line number gutter contributes to virtual size, so recalculate."""
        self._refresh_size()

    def _watch_indent_width(self) -> None:
        """Changing width of tabs will change document display width."""
        self._refresh_size()

    def _watch_theme(self, theme: str | None) -> None:
        """We set the styles on this widget when the theme changes, to ensure that
        if padding is applied, the colours match."""

        if theme is None:
            # If the theme is None, use the default.
            theme_object = TextEditorTheme.default()
        else:
            # If the user supplied a string theme name, find it and apply it.
            try:
                theme_object = self._themes[theme]
            except KeyError:
                theme_object = TextEditorTheme.get_builtin_theme(theme)

            if theme_object is None:
                raise ThemeDoesNotExist(
                    f"{theme!r} is not a builtin theme, or it has not been registered. "
                    f"To use a custom theme, register it first using `register_theme`, "
                    f"then switch to that theme by setting the `TextEditor.theme` attribute."
                )

        self._theme = theme_object
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
        """A list of the names of the themes available to the `TextEditor`.

        The values in this list can be assigned `theme` reactive attribute of
        `TextEditor`.

        You can retrieve the full specification for a theme by passing one of
        the strings from this list into `TextEditorTheme.get_by_name(theme_name: str)`.

        Alternatively, you can directly retrieve a list of `TextEditorTheme` objects
        (which contain the full theme specification) by calling
        `TextEditorTheme.builtin_themes()`.
        """
        return {
            theme.name for theme in TextEditorTheme.builtin_themes()
        } | self._themes.keys()

    def register_theme(self, theme: TextEditorTheme) -> None:
        """Register a theme for use by the `TextEditor`.

        After registering a theme, you can set themes by assigning the theme
        name to the `TextEditor.theme` reactive attribute. For example
        `text_editor.theme = "my_custom_theme"` where `"my_custom_theme"` is the
        name of the theme you registered.

        If you supply a theme with a name that already exists that theme
        will be overwritten.
        """
        self._themes[theme.name] = theme

    @property
    def available_languages(self) -> set[str]:
        """A list of the names of languages available to the `TextEditor`.

        The values in this list can be assigned to the `language` reactive attribute
        of `TextEditor`.

        The returned list contains the builtin languages plus those registered via the
        `register_language` method. Builtin languages will be listed before
        user-registered languages, but there are no other ordering guarantees.
        """
        return set(BUILTIN_LANGUAGES) | self._languages.keys()

    def register_language(
        self,
        language: str | "Language",
        highlight_query: str,
    ) -> None:
        """Register a language and corresponding highlight query.

        Calling this method does not change the language of the `TextEditor`.
        On switching to this language (via the `language` reactive attribute),
        syntax highlighting will be performed using the given highlight query.

        If a string `name` is supplied for a builtin supported language, then
        this method will update the default highlight query for that language.

        Registering a language only registers it to this instance of `TextEditor`.

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
        self._languages[language_name] = TextEditorLanguage(
            name=language_name,
            language=language,
            highlight_query=highlight_query,
        )
        # If we updated the currently set language, rebuild the highlights
        # using the newly updated highlights query.
        if language_name == self.language:
            self._set_document(self.text, language_name)

    def _set_document(self, text: str, language: str | None) -> None:
        """Construct and return an appropriate document.

        Args:
            text: The text of the document.
            language: The name of the language to use. This must either be a
                built-in supported language, or a language previously registered
                via the `register_language` method.
        """
        self._highlight_query = None
        if TREE_SITTER and language:
            # Attempt to get the override language.
            text_editor_language = self._languages.get(language, None)
            document_language: str | "Language"
            if text_editor_language:
                document_language = text_editor_language.language
                highlight_query = text_editor_language.highlight_query
            else:
                document_language = language
                highlight_query = self._get_builtin_highlight_query(language)
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
        elif language and not TREE_SITTER:
            log.warning(
                "tree-sitter not available in this environment. Parsing disabled.\n"
                "You may need to install the `syntax` extras alongside textual.\n"
                "Try `pip install 'textual[syntax]'` or '`poetry add textual[syntax]'."
            )
            document = Document(text)
        else:
            document = Document(text)

        self.document = document
        self._build_highlight_map()

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
        """Load text into the TextEditor.

        This will replace the text currently in the TextEditor.

        Args:
            text: The text to load into the TextEditor.
        """
        self._set_document(text, self.language)
        self.move_cursor((0, 0))
        self._refresh_size()

    def load_document(self, document: DocumentBase) -> None:
        """Load a document into the TextEditor.

        Args:
            document: The document to load into the TextEditor.
        """
        self.document = document
        self.move_cursor((0, 0))
        self._refresh_size()

    @property
    def is_syntax_aware(self) -> bool:
        """True if the TextEditor is currently syntax aware - i.e. it's parsing document content."""
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

    def render_line(self, widget_y: int) -> Strip:
        """Render a single line of the TextEditor. Called by Textual.

        Args:
            widget_y: Y Coordinate of line relative to the widget region.

        Returns:
            A rendered line.
        """
        document = self.document
        scroll_x, scroll_y = self.scroll_offset

        # Account for how much the TextEditor is scrolled.
        line_index = widget_y + scroll_y

        # Render the lines beyond the valid line numbers
        out_of_bounds = line_index >= document.line_count
        if out_of_bounds:
            return Strip.blank(self.size.width)

        theme = self._theme

        # Get the line from the Document.
        line_string = document.get_line(line_index)
        line = Text(line_string, end="")

        line_character_count = len(line)
        line.tab_size = self.indent_width
        virtual_width, virtual_height = self.virtual_size
        expanded_length = max(virtual_width, self.size.width)
        line.set_length(expanded_length)

        selection = self.selection
        start, end = selection
        selection_top, selection_bottom = sorted(selection)
        selection_top_row, selection_top_column = selection_top
        selection_bottom_row, selection_bottom_column = selection_bottom

        highlights = self._highlights
        if highlights and theme:
            line_bytes = _utf8_encode(line_string)
            byte_to_codepoint = build_byte_to_codepoint_dict(line_bytes)
            get_highlight_from_theme = theme.syntax_styles.get
            line_highlights = highlights[line_index]
            for highlight_start, highlight_end, highlight_name in line_highlights:
                node_style = get_highlight_from_theme(highlight_name)
                if node_style is not None:
                    line.stylize(
                        node_style,
                        byte_to_codepoint.get(highlight_start, 0),
                        byte_to_codepoint.get(highlight_end) if highlight_end else None,
                    )

        cursor_row, cursor_column = end
        cursor_line_style = theme.cursor_line_style if theme else None
        if cursor_line_style and cursor_row == line_index:
            line.stylize(cursor_line_style)

        # Selection styling
        if start != end and selection_top_row <= line_index <= selection_bottom_row:
            # If this row intersects with the selection range
            selection_style = theme.selection_style if theme else None
            cursor_row, _ = end
            if selection_style:
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

        # Highlight the cursor
        matching_bracket = self._matching_bracket_location
        match_cursor_bracket = self.match_cursor_bracket
        draw_matched_brackets = (
            match_cursor_bracket and matching_bracket is not None and start == end
        )

        if cursor_row == line_index:
            draw_cursor = not self.cursor_blink or (
                self.cursor_blink and self._cursor_blink_visible
            )
            if draw_matched_brackets:
                matching_bracket_style = theme.bracket_matching_style if theme else None
                if matching_bracket_style:
                    line.stylize(
                        matching_bracket_style,
                        cursor_column,
                        cursor_column + 1,
                    )

            if draw_cursor:
                cursor_style = theme.cursor_style if theme else None
                if cursor_style:
                    line.stylize(cursor_style, cursor_column, cursor_column + 1)

        # Highlight the partner opening/closing bracket.
        if draw_matched_brackets:
            # mypy doesn't know matching bracket is guaranteed to be non-None
            assert matching_bracket is not None
            bracket_match_row, bracket_match_column = matching_bracket
            if theme and bracket_match_row == line_index:
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
                gutter_style = theme.cursor_line_gutter_style if theme else None
            else:
                gutter_style = theme.gutter_style if theme else None

            gutter_width_no_margin = gutter_width - 2
            gutter = Text(
                f"{line_index + 1:>{gutter_width_no_margin}}  ",
                style=gutter_style or "",
                end="",
            )
        else:
            gutter = Text("", end="")

        # Render the gutter and the text of this line
        console = self.app.console
        gutter_segments = console.render(gutter)
        text_segments = console.render(
            line,
            console.options.update_width(expanded_length),
        )

        # Crop the line to show only the visible part (some may be scrolled out of view)
        gutter_strip = Strip(gutter_segments, cell_length=gutter_width)
        text_strip = Strip(text_segments).crop(
            scroll_x, scroll_x + virtual_width - gutter_width
        )

        # Stylize the line the cursor is currently on.
        if cursor_row == line_index:
            text_strip = text_strip.extend_cell_length(
                expanded_length, cursor_line_style
            )
        else:
            text_strip = text_strip.extend_cell_length(
                expanded_length, theme.base_style if theme else None
            )

        # Join and return the gutter and the visible portion of this line
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
        """Replace the text currently in the TextEditor. This is an alias of `load_text`.

        Args:
            value: The text to load into the TextEditor.
        """
        self.load_text(value)

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
        self.post_message(self.Changed(self))
        return result

    async def _on_key(self, event: events.Key) -> None:
        """Handle key presses which correspond to document inserts."""
        key = event.key
        insert_values = {
            "tab": " " * self._find_columns_to_next_tab_stop(),
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
        self.app.cursor_position = self.cursor_screen_offset

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
        # TextEditor widget while selecting, the widget still scrolls.
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


@lru_cache(maxsize=128)
def build_byte_to_codepoint_dict(data: bytes) -> dict[int, int]:
    """Build a mapping of utf-8 byte offsets to codepoint offsets for the given data.

    Args:
        data: utf-8 bytes.

    Returns:
        A `dict[int, int]` mapping byte indices to codepoint indices within `data`.
    """
    byte_to_codepoint = {}
    current_byte_offset = 0
    code_point_offset = 0

    while current_byte_offset < len(data):
        byte_to_codepoint[current_byte_offset] = code_point_offset
        first_byte = data[current_byte_offset]

        # Single-byte character
        if (first_byte & 0b10000000) == 0:
            current_byte_offset += 1
        # 2-byte character
        elif (first_byte & 0b11100000) == 0b11000000:
            current_byte_offset += 2
        # 3-byte character
        elif (first_byte & 0b11110000) == 0b11100000:
            current_byte_offset += 3
        # 4-byte character
        elif (first_byte & 0b11111000) == 0b11110000:
            current_byte_offset += 4
        else:
            raise ValueError(f"Invalid UTF-8 byte: {first_byte}")

        code_point_offset += 1

    # Mapping for the end of the string
    byte_to_codepoint[current_byte_offset] = code_point_offset
    return byte_to_codepoint
