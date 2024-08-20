from __future__ import annotations

from rich.cells import cell_len
from rich.console import Console, RenderableType
from rich.protocol import rich_cast


def measure(
    console: Console,
    renderable: RenderableType,
    default: int,
    *,
    container_width: int | None = None,
) -> int:
    """Measure a rich renderable.

    Args:
        console: A console object.
        renderable: Rich renderable.
        default: Default width to use if renderable does not expose dimensions.
        container_width: Width of container or None to use console width.

    Returns:
        Width in cells
    """
    if isinstance(renderable, str):
        return cell_len(renderable)

    width = default
    renderable = rich_cast(renderable)
    get_console_width = getattr(renderable, "__rich_measure__", None)
    if get_console_width is not None:
        options = (
            console.options
            if container_width is None
            else console.options.update_width(container_width)
        )
        render_width = get_console_width(console, options).maximum
        width = max(0, render_width)

    return width
