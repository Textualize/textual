from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.cells import cell_len
from rich.highlighter import Highlighter
from rich.segment import Segment
from rich.text import Text

from .. import events
from ..binding import Binding
from ..geometry import Size
from .._segment_tools import line_crop
from ..message import Message, MessageTarget
from ..reactive import reactive
from ..widget import Widget


class _InputRenderable:
    def __init__(self, input: Input, cursor_visible: bool) -> None:
        self.input = input
        self.cursor_visible = cursor_visible

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":

        input = self.input
        result = input._value
        if input._cursor_at_end:
            result.pad_right(1)
        cursor_style = input.get_component_rich_style("input--cursor")
        if self.cursor_visible and input.has_focus:
            cursor = input.cursor_position
            result.stylize(cursor_style, cursor, cursor + 1)
        width = input.content_size.width
        segments = list(result.render(console))
        line_length = Segment.get_line_length(segments)
        if line_length < width:
            segments = Segment.adjust_line_length(segments, width)
            line_length = width

        line = line_crop(
            list(segments),
            input.view_position,
            input.view_position + width,
            line_length,
        )
        yield from line


class Input(Widget, can_focus=True):
    """A text input widget."""

    DEFAULT_CSS = """
    Input {
        background: $boost;
        color: $text;        
        padding: 0 2;
        border: tall $background;
        width: auto;
        height: 1;
    }
    Input:focus {
       border: tall $accent;
    }
    Input>.input--cursor {
        background: $surface;
        color: $text;
        text-style: reverse;
    }
    Input>.input--placeholder {
        color: $text-disabled;
    }
    """

    BINDINGS = [
        Binding("left", "cursor_left", "cursor left"),
        Binding("right", "cursor_right", "cursor right"),
        Binding("backspace", "delete_left", "delete left"),
    ]

    COMPONENT_CLASSES = {"input--cursor", "input--placeholder"}

    cursor_blink = reactive(True)
    value = reactive("", layout=True)
    input_scroll_offset = reactive(0)
    cursor_position = reactive(0)
    view_position = reactive(0)
    placeholder = reactive("")

    complete = reactive("")
    width = reactive(1)

    _cursor_visible = reactive(True)
    password = reactive(False)
    max_size: reactive[int | None] = reactive(None)

    def __init__(
        self,
        value: str = "",
        placeholder: str = "",
        highlighter: Highlighter | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.value = value
        self.placeholder = placeholder
        self.highlighter = highlighter

    def _position_to_cell(self, position: int) -> int:
        cell_offset = cell_len(self.value[:position])
        return cell_offset

    @property
    def _cursor_offset(self) -> int:
        offset = self._position_to_cell(self.cursor_position)
        if self._cursor_at_end:
            offset += 1
        return offset

    @property
    def _cursor_at_end(self) -> bool:
        """Check if the cursor is at the end"""
        return self.cursor_position >= len(self.value)

    def validate_cursor_position(self, cursor_position: int) -> int:
        return min(max(0, cursor_position), len(self.value))

    def validate_view_position(self, view_position: int) -> int:
        width = self.content_size.width
        new_view_position = max(0, min(view_position, self.cursor_width - width))
        return new_view_position

    def watch_cursor_position(self, old_position: int, new_position: int) -> None:
        width = self.content_size.width
        view_start = self.view_position
        view_end = view_start + width
        cursor_offset = self._cursor_offset

        if cursor_offset >= view_end or cursor_offset < view_start:
            view_position = cursor_offset - width // 2
            self.view_position = view_position
        else:
            self.view_position = self.view_position

    @property
    def cursor_width(self) -> int:
        if self.placeholder and not self.value:

            return cell_len(self.placeholder)
        return self._position_to_cell(len(self.value)) + 1

    def render(self) -> RenderableType:
        self.view_position = self.view_position
        if not self.value:
            placeholder = Text(self.placeholder)
            placeholder.stylize(self.get_component_rich_style("input--placeholder"))
            if self.has_focus:
                cursor_style = self.get_component_rich_style("input--cursor")
                if self._cursor_visible:
                    placeholder.stylize(cursor_style, 0, 1)
            return placeholder
        return _InputRenderable(self, self._cursor_visible)

    class Changed(Message, bubble=True):
        """Value was changed."""

        def __init__(self, sender: MessageTarget, value: str) -> None:
            super().__init__(sender)
            self.value = value

    class Updated(Message, bubble=True):
        """Value was updated via enter key or blur."""

        def __init__(self, sender: MessageTarget, value: str) -> None:
            super().__init__(sender)
            self.value = value

    @property
    def _value(self) -> Text:
        if self.password:
            return Text("•" * len(self.value), no_wrap=True, overflow="ignore")
        else:
            text = Text(self.value, no_wrap=True, overflow="ignore")
            if self.highlighter is not None:
                text = self.highlighter(text)
            return text

    @property
    def _complete(self) -> Text:
        return Text(self.complete, no_wrap=True, overflow="ignore")

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return self.cursor_width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return 1

    def toggle_cursor(self) -> None:
        self._cursor_visible = not self._cursor_visible

    def on_mount(self) -> None:
        self.blink_timer = self.set_interval(
            0.5,
            self.toggle_cursor,
            pause=not (self.cursor_blink and self.has_focus),
        )

    def on_blur(self) -> None:
        self.blink_timer.pause()

    def on_focus(self) -> None:
        self.cursor_position = len(self.value)
        if self.cursor_blink:
            self.blink_timer.resume()

    async def on_key(self, event: events.Key) -> None:
        self._cursor_visible = True
        if self.cursor_blink:
            self.blink_timer.reset()
        event.prevent_default()

        # Do key bindings first
        if await self.handle_key(event):
            return

        if event.char is not None:
            self.insert_text_at_cursor(event.char)

    def insert_text_at_cursor(self, text: str) -> None:
        if self.cursor_position > len(self.value):
            self.value += text
            self.cursor_position = len(self.value)
        else:
            value = self.value
            before = value[: self.cursor_position]
            after = value[self.cursor_position :]
            self.value = f"{before}{text}{after}"
            self.cursor_position += len(text)

    def action_cursor_left(self) -> None:
        self.cursor_position -= 1

    def action_cursor_right(self) -> None:
        self.cursor_position += 1

    def action_delete_left(self) -> None:
        if self.cursor_position == len(self.value):
            self.value = self.value[:-1]
            self.cursor_position = len(self.value)
        else:
            value = self.value
            delete_position = self.cursor_position - 1
            before = value[:delete_position]
            after = value[delete_position + 1 :]
            self.value = f"{before}{after}"
            self.cursor_position = delete_position
