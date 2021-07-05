from __future__ import annotations

import ast
from typing import Any, Tuple
import re


class ActionError(Exception):
    pass


re_action_params = re.compile(r"([\w\.]+)(\(.*?\))")


def parse(action: str) -> tuple[str, tuple[Any, ...]]:
    params_match = re_action_params.match(action)
    if params_match is not None:
        action_name, action_params_str = params_match.groups()
        try:
            action_params = ast.literal_eval(action_params_str)
        except Exception as error:
            raise ActionError(str(error))
    else:
        action_name = action
        action_params = ()

    return (
        action_name,
        action_params if isinstance(action_params, tuple) else (action_params,),
    )


if __name__ == "__main__":

    print(parse("view.toggle('side')"))

    print(parse("view.toggle"))
