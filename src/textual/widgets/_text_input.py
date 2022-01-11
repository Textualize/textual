from __future__ import annotations
import string

from rich.console import RenderableType
from rich.text import Text
from rich.syntax import Syntax
from rich.style import StyleType

from .. import events
from ..events import Event
from ..reactive import Reactive
from ..widget import Widget
from ..keys import Keys


class TextInput(Widget):
    def __init__(
        self,
        style: StyleType = "gold1 on grey11",
        syntax_theme: str = "ansi_dark",
        lexer_name: str = "python",
    ) -> None:
        super().__init__()
        self.lines = [""]
        self.row = 0
        self.col = 0
        self.style = style
        self.syntax = Syntax("", lexer_name, theme=syntax_theme, word_wrap=True)

    def highlight(self, code: str, start: str = "", end: str = "") -> Text:
        text = self.syntax.highlight(code)
        if not code.endswith("\n"):
            text = text[:-1]
        return Text(start) + text + Text(end)

    def render(self) -> RenderableType:
        text = Text()

        if self.row > 0:
            # text above prompt
            text += self.highlight("\n".join(self.lines[:self.row]), end="\n")

        # prompt
        if self.col == len(self.lines[self.row]):
            # cursor at EOL, add an extra space
            end = " "
        else:
            end = ""
        prompt = self.highlight(self.lines[self.row], end=end)
        prompt.stylize("reverse", self.col, self.col + 1)
        text += prompt

        if self.row < len(self.lines) - 1:
            # text below prompt
            text += self.highlight("\n".join(self.lines[self.row + 1:]), start="\n", end="")

        return text

    async def on_key(self, event: Event) -> None:
        if event.key == Keys.Escape:
            self.has_focus = False
        elif event.key == Keys.Up:
            if self.row > 0:
                self.row -= 1
                self.col = min(len(self.lines[self.row]), self.col)
        elif event.key == Keys.Down:
            if self.row < len(self.lines) - 1:
                self.row += 1
                self.col = min(len(self.lines[self.row]), self.col)
        elif event.key == Keys.Return or event.key == Keys.Enter:
            self.lines.insert(self.row, self.lines[self.row][:self.col])
            self.row += 1
            self.lines[self.row] = self.lines[self.row][self.col:]
            self.col = 0
        elif event.key == Keys.Home:
            self.col = 0
        elif event.key == Keys.End:
            self.col = len(self.lines[self.row])
        elif event.key in [Keys.Backspace, "ctrl+h"]:
            if self.col == 0:
                if self.row != 0:
                    self.row -= 1
                    self.col = len(self.lines[self.row])
                    self.lines[self.row] += self.lines[self.row + 1]
                    del self.lines[self.row + 1]
            else:
                self.lines[self.row] = self.lines[self.row][:self.col - 1] + self.lines[self.row][self.col:]
                self.col -= 1
        elif event.key == Keys.Delete:
            if self.col == len(self.lines[self.row]):
                if self.row < len(self.lines) - 1:
                    self.lines[self.row] += self.lines[self.row + 1]
                    del self.lines[self.row + 1]
            else:
                self.lines[self.row] = self.lines[self.row][:self.col] + self.lines[self.row][self.col + 1:]
        elif event.key == Keys.Left:
            if self.col == 0:
                if self.row != 0:
                    self.row -= 1
                    self.col = len(self.lines[self.row])
            else:
                self.col -= 1
        elif event.key == Keys.Right:
            if self.col == len(self.lines[self.row]):
                if self.row < len(self.lines) - 1:
                    self.row += 1
                    self.col = 0
            else:
                self.col += 1
        elif event.key in string.printable:
            self.lines[self.row] = self.lines[self.row][:self.col] + event.key + self.lines[self.row][self.col:]
            self.col += 1
        self.refresh()
