from __future__ import annotations

from types import GeneratorType
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:

    from .app import ComposeResult
    from .widget import Widget


def _compose(compose_result: ComposeResult) -> Iterable[Widget]:
    """Turns a compose result in to an iterable of Widgets.

    If `compose_result` is a generator, this will run the generator and send
    back the yielded widgets. This allows you to write code such as this:

    ```python
    yes = yield Button("Yes")
    yes.variant = "success"
    ```

    Otherwise `compose_result` is assumed to already be an iterable of Widgets
    and will be returned unmodified.

    Args:
        compose_result (ComposeResult): Either an iterator of widgets,
            or a generator.

    Returns:
        Iterable[Widget]: In iterable if widgets.

    """

    if not isinstance(compose_result, GeneratorType):
        return compose_result

    try:
        widget = next(compose_result)
        while True:
            yield widget
            widget = compose_result.send(widget)
    except StopIteration:
        pass
