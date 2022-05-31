from __future__ import annotations

from rich.console import RenderableType

from .geometry import Size
from .widget import Widget


class ScrollView(Widget):
    CSS = """
    
    ScrollView {
        background: blue;
        overflow-y: scroll;
        overflow-x: scroll;
        scrollbar-size-vertical: 2;
        scrollbar-size-horizontal: 1;
    }

    """

    def __init__(
        self, name: str | None = None, id: str | None = None, classes: str | None = None
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)

    @property
    def is_scrollable(self) -> bool:
        return True

    def on_mount(self):
        self.virtual_size = Size(200, 200)
        self._refresh_scrollbars()
        self.refresh(layout=True)

    def size_updated(
        self, size: Size, virtual_size: Size, container_size: Size
    ) -> None:

        virtual_size = self.virtual_size
        if self._size != size:
            self._size = size
            self._container_size = container_size

            self._refresh_scrollbars()
            width, height = self.container_size
            if self.show_vertical_scrollbar:
                self.vertical_scrollbar.window_virtual_size = virtual_size.height
                self.vertical_scrollbar.window_size = height
            if self.show_horizontal_scrollbar:
                self.horizontal_scrollbar.window_virtual_size = virtual_size.width
                self.horizontal_scrollbar.window_size = width

            self.scroll_x = self.validate_scroll_x(self.scroll_x)
            self.scroll_y = self.validate_scroll_y(self.scroll_y)
            self.refresh(layout=False)
            self.call_later(self.scroll_to, self.scroll_x, self.scroll_y)

    def render(self) -> RenderableType:
        return f"{self.scroll_offset} {self.show_vertical_scrollbar}"

    def watch_scroll_x(self, new_value: float) -> None:
        self.horizontal_scrollbar.position = int(new_value)
        self.refresh()

    def watch_scroll_y(self, new_value: float) -> None:
        self.vertical_scrollbar.position = int(new_value)
        self.refresh()


if __name__ == "__main__":
    from textual.app import App, ComposeResult

    class ScrollApp(App):
        def compose(self) -> ComposeResult:
            yield ScrollView()

    app = ScrollApp()
    app.run()
