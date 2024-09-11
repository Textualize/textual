import os
from textual.app import App
from textual.widgets import RichLog


class RichLogTest(App):
    def compose(self):
        ri = RichLog(auto_scroll=False)
        suffix = "A" * 100
        for i in range(1, 100):
            ri.write(f"This is line number {i} {suffix}")
        yield ri


if __name__ == "__main__":
    app = RichLogTest()
    app.run()
