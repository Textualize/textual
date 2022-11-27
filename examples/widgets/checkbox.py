from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Checkbox, Static


class CheckboxApp(App):
    def compose(self) -> ComposeResult:
        yield Static("[b]Example checkboxes\n", classes="label")
        yield Horizontal(
            Static("off:     ", classes="label"),
            Checkbox(animate=False),
            classes="container",
        )
        yield Horizontal(
            Static("on:      ", classes="label"),
            Checkbox(value=True),
            classes="container",
        )

        focused_checkbox = Checkbox()
        focused_checkbox.focus()
        yield Horizontal(
            Static("focused: ", classes="label"), focused_checkbox, classes="container"
        )

        yield Horizontal(
            Static("custom:  ", classes="label"),
            Checkbox(id="custom-design"),
            classes="container",
        )


app = CheckboxApp(css_path="checkbox.css")
if __name__ == "__main__":
    app.run()
