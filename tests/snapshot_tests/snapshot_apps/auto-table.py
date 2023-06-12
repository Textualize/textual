from textual.app import App
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Header, Label


class LabeledBox(Container):
    DEFAULT_CSS = """
    LabeledBox {
        layers: base_ top_;
        width: 100%;
        height: 100%;
    }

    LabeledBox > Container {
        layer: base_;
        border: round $primary;
        width: 100%;
        height: 100%;
        layout: vertical;
    }

    LabeledBox > Label {
        layer: top_;
        offset-x: 2;
    }
    """

    def __init__(self, title, *args, **kwargs):
        self.__label = Label(title)

        super().__init__(self.__label, Container(*args, **kwargs))

    @property
    def label(self):
        return self.__label


class StatusTable(DataTable):
    def __init__(self):
        super().__init__()

        self.cursor_type = "row"
        self.show_cursor = False
        self.add_column("Foo")
        self.add_column("Bar")
        self.add_column("Baz")

        for _ in range(50):
            self.add_row(
                "ABCDEFGH",
                "0123456789",
                "IJKLMNOPQRSTUVWXYZ",
            )


class Status(LabeledBox):
    DEFAULT_CSS = """
    Status {
        width: auto;
    }

    Status Container {
        width: auto;
    }

    Status StatusTable {
        width: auto;
        height: 100%;
        margin-top: 1;
        scrollbar-gutter: stable;
        overflow-x: hidden;
    }
    """

    def __init__(self, name: str):
        self.__name = name
        self.__table = StatusTable()

        super().__init__(f" {self.__name} ", self.__table)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def table(self) -> StatusTable:
        return self.__table


class Rendering(LabeledBox):
    DEFAULT_CSS = """
    #issue-info {
        height: auto;
        border-bottom: dashed #632CA6;
    }

    #statuses-box {
        height: 1fr;
        width: auto;
    }
    """

    def __init__(self):
        self.__info = Label("test")

        super().__init__(
            "",
            ScrollableContainer(
                Horizontal(self.__info, id="issue-info"),
                Horizontal(*[Status(str(i)) for i in range(4)], id="statuses-box"),
                id="issues-box",
            ),
        )

    @property
    def info(self) -> Label:
        return self.__info


class Sidebar(LabeledBox):
    DEFAULT_CSS = """
    #sidebar-status {
        height: auto;
        border-bottom: dashed #632CA6;
    }

    #sidebar-options {
        height: 1fr;
    }
    """

    def __init__(self):
        self.__status = Label("ok")
        self.__options = Vertical()

        super().__init__(
            "",
            Container(self.__status, id="sidebar-status"),
            Container(self.__options, id="sidebar-options"),
        )

    @property
    def status(self) -> Label:
        return self.__status

    @property
    def options(self) -> Vertical:
        return self.__options


class MyScreen(Screen):
    DEFAULT_CSS = """
    #main-content {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 5fr;
        grid-rows: 1fr;
    }

    #main-content-sidebar {
        height: 100%;
    }

    #main-content-rendering {
        height: 100%;
    }
    """

    def compose(self):
        yield Header()
        yield Container(
            Container(Sidebar(), id="main-content-sidebar"),
            Container(Rendering(), id="main-content-rendering"),
            id="main-content",
        )


class MyApp(App):
    async def on_mount(self):
        self.install_screen(MyScreen(), "myscreen")
        await self.push_screen("myscreen")


if __name__ == "__main__":
    app = MyApp()
    app.run()
