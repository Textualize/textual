from textual.app import App
from textual.widget import Widget
from textual.widgets import Static


class FocusKeybindsApp(App):
    dark = True

    def on_load(self) -> None:
        self.bind("1", "focus('widget1')")
        self.bind("2", "focus('widget2')")
        self.bind("3", "focus('widget3')")
        self.bind("4", "focus('widget4')")
        self.bind("q", "focus('widgetq')")
        self.bind("w", "focus('widgetw')")
        self.bind("e", "focus('widgete')")
        self.bind("r", "focus('widgetr')")

    def on_mount(self) -> None:
        info = Static(
            "Use keybinds to shift focus between the widgets in the lists below",
        )
        self.mount(info=info)

        self.mount(
            body=Widget(
                Widget(
                    Static("Press 1 to focus", id="widget1", classes="list-item"),
                    Static("Press 2 to focus", id="widget2", classes="list-item"),
                    Static("Press 3 to focus", id="widget3", classes="list-item"),
                    Static("Press 4 to focus", id="widget4", classes="list-item"),
                    classes="list",
                    id="left_list",
                ),
                Widget(
                    Static("Press Q to focus", id="widgetq", classes="list-item"),
                    Static("Press W to focus", id="widgetw", classes="list-item"),
                    Static("Press E to focus", id="widgete", classes="list-item"),
                    Static("Press R to focus", id="widgetr", classes="list-item"),
                    classes="list",
                    id="right_list",
                ),
            ),
        )
        self.mount(footer=Static("No widget focused"))

    def on_descendant_focus(self):
        self.get_child("footer").update(
            f"Focused: {self.focused.id}" or "No widget focused"
        )


app = FocusKeybindsApp(css_path="focus_keybindings.scss", watch_css=True)
app.run()
