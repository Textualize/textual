from __future__ import annotations

from datetime import datetime

from rich.text import Text

from ..widget import Widget
from ..reactive import Reactive, watch


class HeaderIcon(Widget):
    """Display an 'icon' on the left of the header."""

    CSS = """
    HeaderIcon {
        dock: left;
        padding: 0 1;
        width: 10;
        content-align: left middle;
    }
    """
    icon = Reactive("⭘")

    def render(self):
        return self.icon


class HeaderClock(Widget):
    """Display a clock on the right of the header."""

    CSS = """
    HeaderClock {        
        dock: right;
        width: auto;
        padding: 0 1;
        background: $secondary-background-lighten-1;
        color: $text-secondary-background;
        opacity: 85%;      
        content-align: center middle;  
    }
    """

    def on_mount(self) -> None:
        self.set_interval(1, callback=self.refresh)

    def render(self):
        return Text(datetime.now().time().strftime("%X"))


class HeaderTitle(Widget):
    """Display the title / subtitle in the header."""

    CSS = """
    HeaderTitle {               
        content-align: center middle;
        width: 100%;        
    }
    """

    text: Reactive[str] = Reactive("Hello World")
    sub_text = Reactive("Test")

    def render(self) -> Text:
        text = Text(self.text, no_wrap=True, overflow="ellipsis")
        if self.sub_text:
            text.append(f" - {self.sub_text}", "dim")
        return text


class Header(Widget):
    """A header widget with icon and clock."""

    CSS = """
    Header {
        dock: top;
        width: 100%;
        background: $secondary-background;
        color: $text-secondary-background;
        height: 1;
    }
    Header.tall {
        height: 3;        
    }
    """

    async def on_click(self, event):
        self.toggle_class("tall")

    def on_mount(self) -> None:
        def set_title(title: str) -> None:
            self.query_one(HeaderTitle).text = title

        def set_sub_title(sub_title: str) -> None:
            self.query_one(HeaderTitle).sub_text = sub_title

        watch(self.app, "title", set_title)
        watch(self.app, "sub_title", set_sub_title)
        self.add_class("tall")

    def compose(self):
        yield HeaderIcon()
        yield HeaderTitle()
        yield HeaderClock()
