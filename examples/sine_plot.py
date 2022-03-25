from rich.align import (
    Align
)
from rich.console import (
    Console,
    ConsoleOptions,
    RenderableType,
    RenderResult
)

from rich.panel import (
    Panel
)
from rich.text import (
    Text
)
from textual.app import (
    App
)
from textual.views import (
    DockView
)
from textual.widget import (
    Widget
)
from textual.widgets import (
    Footer,
    Header
)

try:
    import numpy as np
    from uniplot import (
        plot_to_string
    )
except ImportError:
    print("Please install uniplot, and numpy to run this example!")
from typing import (
    Literal,
    Optional,
)


class RichText:
    """A renderable to generate rich text that adapts to fit the container."""

    def __init__(self, text: str) -> None:
        self.text = text

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Build a Rich renderable to render the text."""
        yield Text(self.text, style="bold")


class Figure(Widget):

    plot: str
    vertical: Optional[Literal['top', 'middle', 'bottom']]
    title: Optional[str] = 'plot'
    _style: str

    def __init__(
        self,
        name: str,
        plot: str,
        style: str,
        vertical: Optional[Literal['top', 'middle', 'bottom']] = "middle"
    ) -> None:
        super().__init__(name)
        self.plot: str = plot
        self.vertical: str = vertical
        self._style: str = style
        self.title = name

    def render(self) -> RenderableType:
        """Build a Rich renderable to render the plot."""
        return Panel(
            renderable=Align.center(RichText(self.plot), vertical=self.vertical),
            style=self._style,
            expand=False,
            title=self.title
        )


class MyApp(App):
    async def on_load(self) -> None:
        """Bind keys here."""
        await self.bind("q", "quit", "Quit")

    async def on_mount(self) -> None:
        view: DockView = await self.push_view(DockView())
        await view.dock(Header(), edge="top")
        await view.dock(Footer(), edge="bottom")
        # initialize plot
        frequency: float = 5.0e2  # 500 Hz
        period: float = 2.0e-3  # 2 ms
        sampling_frequency: float = 50.0e3  # 50 kHz
        sampling_interval: float = 1.0 / sampling_frequency  # 20 us
        samples: int = int(period / sampling_interval)  # 100
        time_domain = np.linspace(0, period, samples)
        signal = np.sin(2 * np.pi * frequency * time_domain)
        # convert plot to list of strings
        plot: str = plot_to_string(signal)
        style: str = "bold white on rgb(58,58,58)"
        figure = Figure(name="Sine Wave Plot", plot="\n".join(plot), style=style)
        await view.dock(figure, edge="right")  # type: ignore


if __name__ == "__main__":
    MyApp.run(title="Plot", log="textual.log", log_verbosity=2)
