from textual.app import App
from textual.widgets import RichLog


class RichLogLines(App):
    count = 0

    def compose(self):
        yield RichLog(max_lines=3)

    async def on_key(self):
        self.count += 1
        log_widget = self.query_one(RichLog)
        log_widget.write(f"Key press #{self.count}")


app = RichLogLines()

if __name__ == "__main__":
    app.run()
