import os
from textual.app import App
from textual.widgets import RichLog


class RichLogTest(App):
    def compose(self):
        ri = RichLog(auto_scroll=False)
        suffix = os.environ.get("SUFFIX", "A" * 1000)
        for i in range(1, 1000):
            ri.write(f"This is line number {i} {suffix}")
        yield ri


if __name__ == "__main__":
    app = RichLogTest()
    app.run()
