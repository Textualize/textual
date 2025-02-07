from textual.app import App, ComposeResult
from textual.widgets import Label


class ContentApp(App):

    def compose(self) -> ComposeResult:
        yield Label("[bold]Bold[/] [italic]Italic[/] [u]Underline[/]  [s]Strike[/s]")
        yield Label(
            "[$primary]Primary[/]  [$secondary]Secondary[/]  [$warning]Warning[/]  [$error]Error[/]"
        )
        yield Label("[$text on $primary]Text on Primary")
        yield Label("[$primary on $primary-muted]Primary on primary muted")
        yield Label("[$error on $error-muted]Error on error muted")
        yield Label(
            "[on $boost]    [on $boost]    [on $boost]  Three layers of $boost  [/]    [/]    [/]"
        )
        yield Label("[on $primary 20%]On primary twenty percent")
        yield Label("[$text 80% on $primary]Hello")


if __name__ == "__main__":
    app = ContentApp()
    app.run()
