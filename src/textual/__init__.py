from typing import Any


def log(*args: Any) -> None:
    from ._context import active_app

    app = active_app.get()
    app.log(*args)
