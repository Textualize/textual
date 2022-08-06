import random

from textual import layout
from textual.app import App, ComposeResult
from textual.widgets import Button, Static


class Thing(Static):
    def on_show(self) -> None:
        self.scroll_visible()


class AddRemoveApp(App):
    CSS = """
    #buttons {
        dock: top;
        height: auto;
    }
    Button {
        width: 1fr;
    }
    #items {
        height: 100%;
        
    }
    Thing {
        height: 5;
        background: $panel;
        border: wide $primary;
        margin: 0 1;
        content-align: center middle;
    }
    """

    def on_mount(self) -> None:
        self.count = 0

    def compose(self) -> ComposeResult:
        yield layout.Vertical(
            layout.Horizontal(
                Button("Add", variant="success", id="add"),
                Button("Remove", variant="error", id="remove"),
                Button("Remove random", variant="warning", id="remove_random"),
                id="buttons",
            ),
            layout.Vertical(id="items"),
        )

    def handle_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add":
            self.count += 1
            self.query("#items").first().mount(
                Thing(f"Thing {self.count}", id=f"thing{self.count}")
            )
        elif event.button.id == "remove":
            things = self.query("#items Thing")
            if things:
                things.last().remove()

        elif event.button.id == "remove_random":
            things = self.query("#items Thing")
            if things:
                random.choice(things).remove()

        self.app.bell()


app = AddRemoveApp()

if __name__ == "__main__":
    app.run()
