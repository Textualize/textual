from __future__ import annotations

from dataclasses import dataclass

from textual.binding import Binding
from textual.document._document import Document, Selection
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip


class TextArea(ScrollView, can_focus=True):
    DEFAULT_CSS = """\
    TextEditor {
        width: 1fr;
        height: 1fr;
    }
    """

    BINDINGS = [
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

    selection: Reactive[Selection] = reactive(
        Selection(), always_update=True, init=False
    )
    """The selection start and end locations (zero-based line_index, offset).

    This represents the cursor location and the current selection.

    The `Selection.end` always refers to the cursor location.

    If no text is selected, then `Selection.end == Selection.start` is True.

    The text selected in the document is available via the `TextArea.selected_text` property.
    """

    cursor_blink: Reactive[bool] = reactive(True)
    """True if the cursor should blink."""

    _cursor_blink_visible: Reactive[bool] = reactive(True, repaint=False)
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
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Construct a new `TextArea`.

        Args:
            text: The initial text to load into the TextArea.
            name: The name of the `TextArea` widget.
            id: The ID of the widget, used to refer to it from Textual CSS.
            classes: One or more Textual CSS compatible class names separated by spaces.
            disabled: True if the widget is disabled.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._initial_text = text

        self._selecting = False
        """True if we're currently selecting text using the mouse, otherwise False."""

        self.document = Document(text)
        """The document this widget is currently editing."""

    def _watch_selection(self, selection: Selection) -> None:
        """When the cursor moves, scroll it into view."""
        # TODO self.scroll_cursor_visible()
        cursor_location = selection.end
        cursor_row, cursor_column = cursor_location

        try:
            character = self.document[cursor_row][cursor_column]
        except IndexError:
            character = ""

        # TODO self.app.cursor_position = self.cursor_screen_offset
        self.post_message(self.SelectionChanged(selection, self))

    def render_line(self, y: int) -> Strip:
        width = self.size.width
