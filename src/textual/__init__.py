from typing import Any

from rich.console import RenderableType

__all__ = ["log", "panic"]


def log(*args: object, verbosity: int = 0, **kwargs) -> None:
    from ._context import active_app

    app = active_app.get()
    app.log(*args, verbosity=verbosity, **kwargs)


def panic(*args: RenderableType) -> None:
    from ._context import active_app

    app = active_app.get()
    app.panic(*args)
