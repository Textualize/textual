from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.design import ColorSystem
from textual.widget import Widget
from textual.widgets import Button, Footer, Static, Label


class ColorButtons(Vertical):
    def compose(self) -> ComposeResult:
        for border in ColorSystem.COLOR_NAMES:
            if border:
                yield Button(border, id=border)


class ColorBar(Static):
    pass


class ColorItem(Horizontal):
    pass


class ColorGroup(Vertical):
    pass


class Content(Vertical):
    pass


class ColorsView(Vertical):
    def compose(self) -> ComposeResult:

        LEVELS = [
            "darken-3",
            "darken-2",
            "darken-1",
            "",
            "lighten-1",
            "lighten-2",
            "lighten-3",
        ]

        for color_name in ColorSystem.COLOR_NAMES:

            items: list[Widget] = [Label(f'"{color_name}"')]
            for level in LEVELS:
                color = f"{color_name}-{level}" if level else color_name
                item = ColorItem(
                    ColorBar(f"${color}", classes="text label"),
                    ColorBar("$text-muted", classes="muted"),
                    ColorBar("$text-disabled", classes="disabled"),
                    classes=color,
                )
                items.append(item)

            yield ColorGroup(*items, id=f"group-{color_name}")


class ColorsApp(App):
    CSS_PATH = "colors.css"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        yield Content(ColorButtons())
        yield Footer()

    def on_mount(self) -> None:
        self.call_after_refresh(self.update_view)

    def update_view(self) -> None:
        content = self.query_one("Content", Content)
        content.mount(ColorsView())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.bell()
        self.query(ColorGroup).remove_class("-active")
        group = self.query_one(f"#group-{event.button.id}", ColorGroup)
        group.add_class("-active")
        group.scroll_visible(top=True, speed=150)


app = ColorsApp()

if __name__ == "__main__":
    app.run()
