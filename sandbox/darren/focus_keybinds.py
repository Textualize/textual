from textual import containers as layout
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Input


class Label(Static, can_focus=True):
    pass


class FocusKeybindsApp(App):
    dark = True

    BINDINGS = [Binding("a", "private_handler", "Private Handler")]

    def on_load(self) -> None:
        self.bind("1", "focus('widget1')")
        self.bind("2", "focus('widget2')")
        self.bind("3", "focus('widget3')")
        self.bind("4", "focus('widget4')")
        self.bind("q", "focus('widgetq')")
        self.bind("w", "focus('widgetw')")
        self.bind("e", "focus('widgete')")
        self.bind("r", "focus('widgetr')")

    def compose(self) -> ComposeResult:
        yield Static(
            "Use keybinds to shift focus between the widgets in the lists below",
            id="info",
        )
        yield layout.Horizontal(
            layout.Vertical(
                Label("Press 1 to focus", id="widget1", classes="list-item"),
                Label("Press 2 to focus", id="widget2", classes="list-item"),
                Input(placeholder="Enter some text..."),
                Label("Press 3 to focus", id="widget3", classes="list-item"),
                Label("Press 4 to focus", id="widget4", classes="list-item"),
                classes="list",
                id="left_list",
            ),
            layout.Vertical(
                Label("Press Q to focus", id="widgetq", classes="list-item"),
                Label("Press W to focus", id="widgetw", classes="list-item"),
                Label("Press E to focus", id="widgete", classes="list-item"),
                Label("Press R to focus", id="widgetr", classes="list-item"),
                classes="list",
                id="right_list",
            ),
        )
        yield Static("No widget focused", id="footer")

    def on_descendant_focus(self):
        self.get_child("footer").update(
            f"Focused: {self.focused.id}" or "No widget focused"
        )

    def key_p(self):
        print(self.app.focused.parent)
        print(self.app.focused)

    def _action_private_handler(self):
        print("inside private handler!")


app = FocusKeybindsApp(css_path="focus_keybinds.css", watch_css=True)
app.run()
