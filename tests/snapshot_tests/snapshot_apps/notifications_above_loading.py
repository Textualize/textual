from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label


class LoadingOverlayApp(App[None]):
    CSS = """
    VerticalScroll {
        height: 20;
    }
    
    Toast {
        max-width: 100%;
        width: 70%;  /* We need this to cover the dots of the loading indicator
        so that we don't have flakiness in the tests because the screenshot
        might be taken a couple ms earlier or later. */
    }"""

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Label("another big label\n" * 30)  # Ensure there's a scrollbar.

    def on_mount(self):
        self.notify("This is a big notification.\n" * 10, timeout=10)
        self.query_one(VerticalScroll).loading = True


if __name__ == "__main__":
    LoadingOverlayApp().run()
