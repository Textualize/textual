from __future__ import annotations

import ast
import re

from typing_extensions import Any, TypeAlias

ActionParseResult: TypeAlias = "tuple[str, tuple[Any, ...]]"
"""An action is its name and the arbitrary tuple of its parameters."""


class SkipAction(Exception):
    """Raise in an action to skip the action (and allow any parent bindings to run)."""


class ActionError(Exception):
    pass


re_action_params = re.compile(r"([\w\.]+)(\(.*?\))")


def parse(action: str) -> ActionParseResult:
    """Parses an action string.

    Args:
        action: String containing action.

    Raises:
        ActionError: If the action has invalid syntax.

    Returns:
        Action name and parameters
    """
    params_match = re_action_params.match(action)
    if params_match is not None:
        action_name, action_params_str = params_match.groups()
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
