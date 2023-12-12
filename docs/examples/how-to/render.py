from textual.app import App, ComposeResult
from textual.widget import Widget


class Custom(Widget):
    def compose(self) -> ComposeResult:
        scrollbar = ScrollBar(vertical=False, thickness=2)
        scrollbar.window_size = 1
        scrollbar.window_virtual_size = 100
        yield scrollbar


class MyApp(App):
    CSS = """
    Custom {
        border: solid red;
    }    
    """

    def compose(self) -> ComposeResult:
        yield Custom()


if __name__ == "__main__":
    MyApp().run()
