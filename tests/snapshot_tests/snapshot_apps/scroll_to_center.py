from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, VerticalScroll
from textual.widgets import Label


class MyApp(App[None]):
    CSS = """
    VerticalScroll, HorizontalScroll {
        border: round $primary;
    }
    #vertical {
        height: 21;
    }
    HorizontalScroll {
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Label(("SPAM\n" * 205)[:-1])
            with VerticalScroll():
                yield Label(("SPAM\n" * 53)[:-1])
                with VerticalScroll(id="vertical"):
                    yield Label(("SPAM\n" * 78)[:-1])
                    with HorizontalScroll():
                        yield Label(("v\n" * 17)[:-1])
                        yield Label("@" * 302)
                        yield Label("[red]>>bullseye<<[/red]", id="bullseye")
                        yield Label("@" * 99)
                    yield Label(("SPAM\n" * 49)[:-1])
                yield Label(("SPAM\n" * 51)[:-1])
            yield Label(("SPAM\n" * 59)[:-1])

    def key_s(self) -> None:
        self.screen.scroll_to_center(self.query_one("#bullseye"))


if __name__ == "__main__":
    MyApp().run()
