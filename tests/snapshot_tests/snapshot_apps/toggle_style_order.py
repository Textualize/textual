from textual.app import App
from textual.widgets import Checkbox, Label


class CheckboxApp(App):
    CSS = """
    Checkbox > .toggle--label, Label {
        color: white;
        text-opacity: 50%;
    }
    """

    def compose(self):
        yield Checkbox("[red bold]This is just[/] some text.")
        yield Label("[bold red]This is just[/] some text.")


if __name__ == "__main__":
    CheckboxApp().run()
