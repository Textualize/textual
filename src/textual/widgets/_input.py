from __future__ import annotations

from rich.cells import cell_len
from rich.text import Text

from .. import events
from ..binding import Binding
from ..geometry import Size
from ..message import Message, MessageTarget
from ..reactive import reactive
from ..widget import Widget


class _InputRenderable:
    def __init__(self, input: Input, cursor_visible: bool) -> None:
        self.input = input
        self.cursor_visible = cursor_visible

    def __rich__(self) -> Text:
        input = self.input
        result = input._value
        result.pad_right(input.cursor_width)
        cursor_style = input.get_component_rich_style("input--cursor")
        if self.cursor_visible and input.has_focus:
            cursor = input.cursor_position
            result.stylize(cursor_style, cursor, cursor + 1)
        width = input.size.width
        print(input.view_position, width)
        result = result[input.view_position : input.view_position + width]
        result.pad_right(width)
        return result


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
        text-style: reverse;     
    }
    """

    BINDINGS = [
        Binding("left", "cursor_left", "cursor left"),
        Binding("right", "cursor_right", "cursor right"),
        Binding("backspace", "delete_left", "delete left"),
    ]

    COMPONENT_CLASSES = {"input--cursor"}

    cursor_blink = reactive(False)
    value = reactive("")
    input_scroll_offset = reactive(0)
    cursor_position = reactive(0)
    view_position = reactive(0)
    complete = reactive("")
    width = reactive(1)
    cursor_width = reactive(1, layout=True)
    _cursor_visible = reactive(True)
    password = reactive(False)
    max_size: reactive[int | None] = reactive(None)

    def __init__(
        self,
        value: str,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.value = value
        self.cursor_position = len(value)
        self.view_position = 0

    def _position_to_cell(self, position: int) -> int:
        cell_index = sum(cell_len(char) for char in self.value[:position])
        return cell_index

    def compute_cursor_width(self) -> int:
        return len(self.value) + (self.cursor_position >= len(self.value))

    def validate_cursor_position(self, value: int) -> int:
        return max(0, value)

    def validate_view_position(self, value: int) -> int:
        position = max(0, value)
        width = self.content_size.width
        if position > self.cursor_width:
            position = min(position, self.cursor_width - width)
        return position

    # def validate_view_position(self, view_position: int) -> int:
    #     width = self.content_size.width
    #     position = min(view_position, self.cursor_position)
    #     return max(max(0, position), self.cursor_width - width)

    # def watch_cursor_width(self, value: int) -> None:
    #     self.view_position = self.validate_view_position(self.view_position)

    async def watch_value(self, value: str) -> None:
        self.width = len(value)
        await self.emit(self.Changed(self, value))

    def watch_cursor_position(
        self, before_cursor_position: int, cursor_position: int
    ) -> None:
        last = len(self.value)

        width = self.content_size.width
        print(f"{cursor_position=} {width=}")
        self.view_position = cursor_position - width

        # print(f"{self.view_position=}")

        if before_cursor_position == last or cursor_position == last:
            self.refresh(layout=True)

    def render(self) -> _InputRenderable:
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
        return (
            Text("•" * len(self.value), no_wrap=True, overflow="ignore")
            if self.password
            else Text(self.value, no_wrap=True, overflow="ignore")
        )

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
