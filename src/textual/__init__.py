from typing import Any

__all__ = ["log", "panic"]


def log(*args: Any) -> None:
    from ._context import active_app

    app = active_app.get()
    app.log(*args)


def panic(*args: Any) -> None:
    from ._context import active_app

    app = active_app.get()
    app.panic(*args)
