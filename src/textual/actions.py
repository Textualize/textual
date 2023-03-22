from __future__ import annotations

import ast
import re

from typing_extensions import Any, TypeAlias

ActionParseResult: TypeAlias = "tuple[str, tuple[Any, ...]]"
"""An action is its name and the arbitrary tuple of its arguments."""


class SkipAction(Exception):
    """Raise in an action to skip the action (and allow any parent bindings to run)."""


class ActionError(Exception):
    pass


re_action_args = re.compile(r"([\w\.]+)\((.*)\)")


def _is_single_tuple_argument(evals_to_tuple: str) -> bool:
    """Is this tuple a single argument tuple?

    If `evals_to_tuple` is such that `ast.literal_eval` evaluates it to a tuple,
    is that because it is a comma-separated list of values, like `"1, 2, (False, 3)"`,
    or is it because it is a single tuple, like `"(1, 2, False)"`?

    If it is a single tuple, the string must start with "(", must end with ")", and after
    removing those two parenthesis, `ast.literal_eval` must still be able to parse it
    into the same valid tuple.

    This function must also be able to handle strings like `"(1, 2), (3, 4)"`, which is
    a 2-item tuple in a string that starts with "(" and ends with ")", but that
    represents two arguments for our action.

    Args:
        evals_to_tuple: A string representing action arguments and that is of the type
            `tuple` when evaluated by `ast.literal_eval`.

    Returns:
        Whether the string represents a single tuple or a space-separated list of
            arguments.
    """
    if not evals_to_tuple.startswith("(") or not evals_to_tuple.endswith(")"):
        return False

    without_outer_parens = evals_to_tuple[1:-1]
    # Short-circuit the case `evals_to_tuple == "()"` because `ast.literal_eval` will
    # raise a SyntaxError (EOF) when evaluating `""`.
    if not without_outer_parens:
        return True

    try:
        ast.literal_eval(evals_to_tuple[1:-1])
    except SyntaxError:
        return False
    else:
        return True


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
                tentative_action_args: tuple[Any, ...] | Any = ast.literal_eval(
                    action_args_str
                )
            except Exception:
                raise ActionError(
                    f"unable to parse {action_args_str!r} in action {action!r}"
                )
            else:
                # At this point, if tentative_action_args is not a tuple, it was a
                # single argument. If tentative_action_args IS a tuple, it may have
                # been because the tentative_action_args was a comma-separated list
                # of arguments, like `"1, False, (1, 2, 3)"`, or because it was a single
                # argument tuple, like `"(1, 2, 3)"`. In the latter case,
                # we need to convert to `((1, 2, 3),)`.
                if isinstance(
                    tentative_action_args, tuple
                ) and not _is_single_tuple_argument(action_args_str):
                    action_args = tentative_action_args
                else:
                    action_args = (tentative_action_args,)
        else:
            action_args = ()
    else:
        action_name = action
        action_args = ()

    return action_name, action_args
