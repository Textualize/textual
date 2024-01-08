from urllib.parse import quote
from urllib.request import Request, urlopen

from rich.text import Text

from textual import work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Input, Static
from textual.worker import Worker, get_current_worker


class WeatherApp(App):
    """App to display the current weather."""

    CSS_PATH = "weather.tcss"

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter a City")
        with VerticalScroll(id="weather-container"):
            yield Static(id="weather")

    async def on_input_changed(self, message: Input.Changed) -> None:
        """Called when the input changes"""
        self.update_weather(message.value)

    @work(exclusive=True, thread=True)
    def update_weather(self, city: str) -> None:
        """Update the weather for the given city."""
        weather_widget = self.query_one("#weather", Static)
        worker = get_current_worker()
        if city:
            # Query the network API
            url = f"https://wttr.in/{quote(city)}"
            request = Request(url)
            request.add_header("User-agent", "CURL")
            response_text = urlopen(request).read().decode("utf-8")
            weather = Text.from_ansi(response_text)
            if not worker.is_cancelled:
                self.call_from_thread(weather_widget.update, weather)
        else:
            # No city, so just blank out the weather
            if not worker.is_cancelled:
                self.call_from_thread(weather_widget.update, "")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        self.log(event)


if __name__ == "__main__":
    app = WeatherApp()
    app.run()
