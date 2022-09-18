from rich.console import Console, RenderableType


def measure(console: Console, renderable: RenderableType, default: int) -> int:
    """Measure a rich renderable.

    Args:
        console (Console): A console object.
        renderable (RenderableType): Rich renderable.
        default (int): Default width to use if renderable does not expose dimensions.

    Returns:
        int: Width in cells
    """
    get_console_width = getattr(renderable, "__rich_measure__", None)
    if get_console_width is not None:
        render_width = get_console_width(console, console.options).normalize().maximum
        return max(0, render_width)
    return default
