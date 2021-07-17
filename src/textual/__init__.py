from ._context import active_app


def log(*args) -> None:
    app = active_app.get()
    app.log(*args)