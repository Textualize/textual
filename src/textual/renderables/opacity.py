from rich.console import ConsoleOptions, Console, RenderResult, RenderableType


class Opacity:
    """Return a renderable with the foreground color blended into the background color.

    Args:
        renderable (RenderableType): The RenderableType to manipulate.
        value (float): The opacity as a float. A value of 1.0 means text is fully visible.
    """

    def __init__(self, renderable: RenderableType, value: float = 1.0) -> None:
        self.renderable = renderable
        self.value = value

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        pass
