from rich.text import Text

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import TextLog


class MyWidget(Widget):
    def render(self):
        return Text(
            "\n".join(f"{n} 0123456789" for n in range(20)),
            no_wrap=True,
            overflow="hidden",
            justify="left",
        )


class ScrollViewApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    
    TextLog {
        width:13;
        height:10;        
    }

    Vertical{
        width:13;
        height: 10;
        overflow: scroll;
        overflow-x: auto;
    }
    MyWidget {
        width:13;
        height:auto;
    }

    """

    def compose(self) -> ComposeResult:
        yield TextLog()
        yield Vertical(MyWidget())

    def on_ready(self) -> None:
        self.query_one(TextLog).write("\n".join(f"{n} 0123456789" for n in range(20)))
        self.query_one(Vertical).scroll_end(animate=False)


if __name__ == "__main__":
    app = ScrollViewApp()
    app.run()
