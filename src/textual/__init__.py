from typing import Any

__all__ = ["log", "panic"]


def log(*args: Any, verbosity: int = 0, **kwargs) -> None:
    from ._context import active_app

    app = active_app.get()
    app.log(*args, verbosity=verbosity, **kwargs)


def panic(*args: Any) -> None:
    from ._context import active_app

    app = active_app.get()
    app.panic(*args)
