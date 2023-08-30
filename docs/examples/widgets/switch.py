from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Switch


class SwitchApp(App):
    def compose(self) -> ComposeResult:
        yield Static("[b]Example switches\n", classes="label")
        yield Horizontal(
            Static("off:     ", classes="label"),
            Switch(animate=False),
            classes="container",
        )
        yield Horizontal(
            Static("on:      ", classes="label"),
            Switch(value=True),
            classes="container",
        )

        focused_switch = Switch()
        focused_switch.focus()
        yield Horizontal(
            Static("focused: ", classes="label"), focused_switch, classes="container"
        )

        yield Horizontal(
            Static("custom:  ", classes="label"),
            Switch(id="custom-design"),
            classes="container",
        )


app = SwitchApp(css_path="switch.tcss")
if __name__ == "__main__":
    app.run()
