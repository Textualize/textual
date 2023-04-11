from __future__ import annotations

import ast
import re
from typing import Any

from typing_extensions import TypeAlias

ActionParseResult: TypeAlias = "tuple[str, tuple[Any, ...]]"
"""An action is its name and the arbitrary tuple of its arguments."""


class SkipAction(Exception):
    """Raise in an action to skip the action (and allow any parent bindings to run)."""


class ActionError(Exception):
    pass


re_action_args = re.compile(r"([\w\.]+)\((.*)\)")


def parse(action: str) -> ActionParseResult:
    """Parses an action string.

    Args:
        action: String containing action.

    Raises:
        ActionError: If the action has invalid syntax.

    Returns:
        Action name and arguments.
    """
    args_match = re_action_args.match(action)
    if args_match is not None:
        action_name, action_args_str = args_match.groups()
        if action_args_str:
            try:
                # We wrap `action_args_str` to be able to disambiguate the cases where
                # the list of arguments is a comma-separated list of values from the
                # case where the argument is a single tuple.
                action_args: tuple[Any, ...] = ast.literal_eval(f"({action_args_str},)")
            except Exception:
                raise ActionError(
                    f"unable to parse {action_args_str!r} in action {action!r}"
                )
        else:
            action_args = ()
    else:
        action_name = action
        action_args = ()

    return action_name, action_args
