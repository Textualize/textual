from textual.app import App, ComposeResult
from textual.widgets import Button, Footer, TabbedContent, TabPane


class ExampleApp(App):
    BINDINGS = [("space", "focus_button_2_2", "Focus button 2.2")]

    def compose(self) -> ComposeResult:
        with TabbedContent(id="tabbed-root"):
            with TabPane("[red]Parent 1[/]"):
                with TabbedContent():
                    with TabPane("[red]Child 1.1[/]"):
                        yield Button("Button 1.1", variant="error")
                    with TabPane("[red]Child 1.2[/]"):
                        yield Button("Button 1.2", variant="error")

            with TabPane("[green]Parent 2[/]", id="parent-2"):
                with TabbedContent(id="tabbed-parent-2"):
                    with TabPane("[green]Child 2.1[/]"):
                        yield Button("Button 2.1", variant="success")
                    with TabPane("[green]Child 2.2[/]", id="child-2-2"):
                        yield Button(
                            "Button 2.2",
                            variant="success",
                            id="button-2-2",
                        )

        yield Footer()

    def action_focus_button_2_2(self) -> None:
        self.query_one("#button-2-2", Button).focus()


if __name__ == "__main__":
    app = ExampleApp()
    app.run()
