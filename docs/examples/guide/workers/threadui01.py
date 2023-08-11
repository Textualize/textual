from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Static


def fibonacci(n: int) -> int:
    if n < 2:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


class ThreadWorkerApp(App):
    def on_ready(self) -> None:
        self.fibonacci()

    @work(thread=True)
    def fibonacci(self) -> None:
        """Calculate and display the 100th value in the Fibonacci sequence."""
        fib = fibonacci(20)
        self.call_from_thread(
            self.screen.mount,
            Static(f"Fibonacci 100 is {fib}"),
        )


if __name__ == "__main__":
    app = ThreadWorkerApp()
    app.run()
