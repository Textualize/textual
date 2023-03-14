from __future__ import annotations

from itertools import zip_longest

from rich.text import Text, TextType

from ..app import ComposeResult
from ..widget import Widget
from ._content_switcher import ContentSwitcher
from ._tabs import Tab, Tabs


class _Tab(Tab):
    def __init__(self, label: Text, content_id: str):
        super().__init__(label)
        self.content_id = content_id


class TabPane(Widget):
    DEFAULT_CSS = """
    TabPane {
        height: auto;
        background: $boost;
        padding: 1 2;
    }
    """

    def __init__(
        self,
        title: Text,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        self.title = title
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )


class TabbedContent(Widget):
    DEFAULT_CSS = """
    TabbedContent {
        height: auto;
        background: $boost;
    }
    TabbedContent > ContentSwitcher {
        height: auto;
    }
    """

    def __init__(self, *titles: TextType) -> None:
        self.titles = [self.render_str(title) for title in titles]
        self._tab_content: list[Widget] = []
        super().__init__()

    def compose(self) -> ComposeResult:
        def set_id(content: TabPane, new_id: str) -> TabPane:
            if content.id is None:
                content.id = new_id
            return content

        pane_content = [
            (
                set_id(content, f"tab-{index}")
                if isinstance(content, TabPane)
                else TabPane(
                    title or self.render_str(f"Tab {index}"), content, id=f"tab-{index}"
                )
            )
            for index, (title, content) in enumerate(
                zip_longest(self.titles, self._tab_content), 1
            )
        ]
        tabs = [_Tab(content.title, content.id or "") for content in pane_content]
        yield Tabs(*tabs)
        with ContentSwitcher():
            yield from pane_content

    def compose_add_child(self, widget: Widget) -> None:
        """When using the context manager compose syntax, we want to attach nodes to the switcher."""
        self._tab_content.append(widget)

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        switcher = self.query_one(ContentSwitcher)
        assert isinstance(event.tab, _Tab)
        switcher.current = event.tab.content_id


if __name__ == "__main__":
    from textual.app import App
    from textual.widgets import Label

    class TabbedApp(App):
        def compose(self) -> ComposeResult:
            with TabbedContent("Foo", "Bar", "baz"):
                yield Label("This is foo\nfoo")
                yield Label("This is Bar")
                yield Label("This is Baz")

    app = TabbedApp()
    app.run()
