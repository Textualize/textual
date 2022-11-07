from textual.app import App
from textual.widgets import TextLog


class TextLogLines(App):
    count = 0

    def compose(self):
        yield TextLog(max_lines=3)

    async def on_key(self):
        self.count += 1
        log_widget = self.query_one(TextLog)
        log_widget.write(f"Key press #{self.count}")


app = TextLogLines()

if __name__ == "__main__":
    app.run()
