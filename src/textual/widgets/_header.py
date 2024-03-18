"""Provides a Textual application header widget."""

from __future__ import annotations

from datetime import datetime

from rich.text import Text

from ..app import RenderResult
from ..events import Click, Mount
from ..reactive import Reactive
from ..widget import Widget


class HeaderIcon(Widget):
    """Display an 'icon' on the left of the header."""

    DEFAULT_CSS = """
    HeaderIcon {
        dock: left;
        padding: 0 1;
        width: 8;
        content-align: left middle;
    }

    HeaderIcon:hover {
        background: $foreground 10%;
    }
    """

    icon = Reactive("⭘")
    """The character to use as the icon within the header."""

    async def on_click(self, event: Click) -> None:
        """Launch the command palette when icon is clicked."""
        event.stop()
        await self.run_action("command_palette")

    def render(self) -> RenderResult:
        """Render the header icon.

        Returns:
            The rendered icon.
        """
        return self.icon


class HeaderClockSpace(Widget):
    """The space taken up by the clock on the right of the header."""

    DEFAULT_CSS = """
    HeaderClockSpace {
        dock: right;
        width: 10;
        padding: 0 1;
    }
    """

    def render(self) -> RenderResult:
        """Render the header clock space.

        Returns:
            The rendered space.
        """
        return ""


class HeaderClock(HeaderClockSpace):
    """Display a clock on the right of the header."""

    DEFAULT_CSS = """
    HeaderClock {
        background: $foreground-darken-1 5%;
        color: $text;
        text-opacity: 85%;
        content-align: center middle;
    }
    """

    def _on_mount(self, _: Mount) -> None:
        self.set_interval(1, callback=self.refresh, name=f"update header clock")

    def render(self) -> RenderResult:
        """Render the header clock.

        Returns:
            The rendered clock.
        """
        return Text(datetime.now().time().strftime("%X"))


class HeaderTitle(Widget):
    """Display the title / subtitle in the header."""

    DEFAULT_CSS = """
    HeaderTitle {
        content-align: center middle;
        width: 100%;
    }
    """

    text: Reactive[str] = Reactive("")
    """The main title text."""

    sub_text = Reactive("")
    """The sub-title text."""

    def render(self) -> RenderResult:
        """Render the title and sub-title.

        Returns:
            The value to render.
        """
        text = Text(self.text, no_wrap=True, overflow="ellipsis")
        if self.sub_text:
            text.append(" — ")
            text.append(self.sub_text, "dim")
        return text


class Header(Widget):
    """A header widget with icon and clock."""

    DEFAULT_CSS = """
    Header {
        dock: top;
        width: 100%;
        background: $foreground 5%;
        color: $text;
        height: 1;
    }
    Header.-tall {
        height: 3;
    }
    """

    DEFAULT_CLASSES = ""

    tall: Reactive[bool] = Reactive(False)
    """Set to `True` for a taller header or `False` for a single line header."""

    def __init__(
        self,
        show_clock: bool = False,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        """Initialise the header widget.

        Args:
            show_clock: ``True`` if the clock should be shown on the right of the header.
            name: The name of the header widget.
            id: The ID of the header widget in the DOM.
            classes: The CSS classes of the header widget.
        """
        super().__init__(name=name, id=id, classes=classes)
        self._show_clock = show_clock

    def compose(self):
        yield HeaderIcon()
        yield HeaderTitle()
        yield HeaderClock() if self._show_clock else HeaderClockSpace()

    def watch_tall(self, tall: bool) -> None:
        self.set_class(tall, "-tall")

    def _on_click(self):
        self.toggle_class("-tall")

    @property
    def screen_title(self) -> str:
        """The title that this header will display.

        This depends on [`Screen.title`][textual.screen.Screen.title] and [`App.title`][textual.app.App.title].
        """
        screen_title = self.screen.title
        title = screen_title if screen_title is not None else self.app.title
        return title

    @property
    def screen_sub_title(self) -> str:
        """The sub-title that this header will display.

        This depends on [`Screen.sub_title`][textual.screen.Screen.sub_title] and [`App.sub_title`][textual.app.App.sub_title].
        """
        screen_sub_title = self.screen.sub_title
        sub_title = (
            screen_sub_title if screen_sub_title is not None else self.app.sub_title
        )
        return sub_title

    def _on_mount(self, _: Mount) -> None:
        async def set_title() -> None:
            self.query_one(HeaderTitle).text = self.screen_title

        async def set_sub_title() -> None:
            self.query_one(HeaderTitle).sub_text = self.screen_sub_title

        self.watch(self.app, "title", set_title)
        self.watch(self.app, "sub_title", set_sub_title)
        self.watch(self.screen, "title", set_title)
        self.watch(self.screen, "sub_title", set_sub_title)
