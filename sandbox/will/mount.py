from textual.app import App, ComposeResult

from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Static


class MountWidget(Widget):
    def on_mount(self) -> None:
        print("Widget mounted")


class MountContainer(Container):
    def compose(self) -> ComposeResult:
        yield Container(MountWidget(id="bar"))

    def on_mount(self) -> None:
        bar = self.query_one("#bar")
        print("MountContainer got", bar)


class MountApp(App):
    def compose(self) -> ComposeResult:
        yield MountContainer(id="foo")

    def on_mount(self) -> None:
        foo = self.query_one("#foo")
        print("foo is", foo)
        static = self.query_one("#bar")
        print("App got", static)


if __name__ == "__main__":
    app = MountApp()
    app.run()
