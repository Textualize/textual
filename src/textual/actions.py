from __future__ import annotations

import ast
from typing import Any, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from textual.events import Event


class ActionError(Exception):
    pass


re_action_params = re.compile(r"([\w\.]+)(\(.*?\))")
# We use our own "mini language" for dynamic event properties injections:
# e.g. `'$event.key'` will inject the pressed key, `$event.sender` the string representation of the sender, etc.
re_injected_event = re.compile(r"\$(event[\w.]+)")


def parse(action: str, event: Event | None = None) -> tuple[str, tuple[Any, ...]]:
    params_match = re_action_params.match(action)
    if params_match is not None:
        action_name, action_params_str = params_match.groups()
        if event and "$event" in action_params_str:
            # Allows things like: `self.bind("1,2,3", "on_digit('$event.key')")`
            # i.e. the action handler can receive dynamic data from the event
            action_params_str = _process_dynamic_event_params(action_params_str, event)
        try:
            action_params = ast.literal_eval(action_params_str)
        except Exception:
            raise ActionError(
                f"unable to parse {action_params_str!r} in action {action!r}"
            )
    else:
        action_name = action
        action_params = ()

    return (
        action_name,
        action_params if isinstance(action_params, tuple) else (action_params,),
    )


def _process_dynamic_event_params(action_params_str: str, event: Event) -> str:
    for dynamic_event_match in re.finditer(re_injected_event, action_params_str):
        dynamic_event_processed = re.sub(
            # `$event.sender` becomes `{event.sender}`, ready to be process by `str.format`:
            re_injected_event,
            r"{\1}",
            dynamic_event_match[0],
        )
        dynamic_event_processed = dynamic_event_processed.format(event=event)
        action_params_str = action_params_str.replace(
            dynamic_event_match[0], dynamic_event_processed
        )
    return action_params_str


if __name__ == "__main__":

    print(parse("foo"))

    print(parse("view.toggle('side')"))

    print(parse("view.toggle"))
