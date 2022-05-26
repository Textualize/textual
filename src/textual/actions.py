from __future__ import annotations

import ast
from typing import TYPE_CHECKING
import re

if TYPE_CHECKING:
    from typing import Any, Mapping, Optional


class ActionError(Exception):
    pass


class NotAllowedActionExpression(ActionError):
    pass


class NotAllowedAttributeAccessInActionExpression(NotAllowedActionExpression):
    def __init__(self, expression: str, data_source: object, attribute: str):
        self.expression = expression
        self.data_source = data_source
        self.attribute = attribute


class TooManyLevelsInActionExpression(NotAllowedActionExpression):
    pass


re_action_params = re.compile(r"([\w\.]+)(\(.*?\))")


def parse(
    action: str, dynamic_data_sources: Mapping[str, Any] = None
) -> tuple[str, tuple[Any, ...]]:
    """
    Parse an action string into a tuple of the action name and the action parameters.
    Any parameter that is a string starting with a dollar sign is considered a dynamic placeholder,
    and will be replaced with the data source value for that key.

    For example, the parameter string `"$event.key"` will be parsed into `"c"` if the dynamic data sources
    dict has an "event" key, for which the value is a class that explicitly allows the usage of its "key"
    attribute by actions parameters - and the value of its "key" attribute is the string "c".
    Such explicit attribute access is needed for security reasons, to avoid exposing sensitive data in the
    action.

    To enable such explicit attribute access, you can add a `__allowed_attributes_for_actions__` attribute
    on the object.
    For example, an Event class with the following line in its class definition:
    ```__allowed_attributes_for_actions__ = ("key", "sender)```
    ...explicitly allows the use of its "key" and "sender" attributes by actions parameters.

    Only one level of dynamic attribute access is allowed, so `"$event.sender.is_system"` is never allowed
    even if the "sender" explicitly allow the usage of its "is_system" attribute.

    In order to allow direct access to a direct value of dynamic data sources dict, we can add the
    string "Self" to the list of allowed attributes.
    For example, an Event class with the following line in its class definition:
    ```__allowed_attributes_for_actions__ = ("Self", "key", "sender)```
    ...explicitly allows the use of the expression `$event` actions parameters if an instance of this class
    is passed as the "event" key of the dynamic data sources dict.

    Args:
        action (str): an action expression - e.g. `on_mount("login", "$event.key")`
        dynamic_data_sources (dict | None): a mapping of dynamic data sources to use in the action expression.

    Returns:
        tuple[str, tuple[Any, ...]]: the action name and the action parameters, processed according to the
            dynamic data sources and dynamic parameters pattern.

    Raises:
        ActionError: if the action expression is invalid
        NotAllowedActionExpression:, if dynamic attributes resolution rules prevent access to an attribute
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
        action_params = _process_dynamic_data_source_params(
            action_params if isinstance(action_params, tuple) else (action_params,),
            dynamic_data_sources,
        )
    else:
        action_name = action
        action_params = ()

    return (
        action_name,
        action_params,
    )


def _process_dynamic_data_source_params(
    action_params: tuple[Any, ...], dynamic_data_sources: Optional[Mapping[str, Any]]
) -> tuple[Any, ...]:
    processed_params = []

    for param in action_params:
        is_dynamic_param = isinstance(param, str) and param.startswith("$")

        if not is_dynamic_param:
            # We just don't post-process this param at all:
            processed_params.append(param)
            continue

        param_components = param[1:].split(".")

        data_source_key = param_components[0]
        if data_source_key not in dynamic_data_sources:
            # We're requesting something like `"$event"`, but the dynamic data sources dict doesn't have
            # an "event" key: that's an error!
            raise NotAllowedActionExpression(param)
        data_source = dynamic_data_sources[data_source_key]

        allowed_attributes = getattr(
            data_source, "__allowed_attributes_for_actions__", None
        )

        if len(param_components) == 1:
            # Simple case: no attributes access, we just replace the placeholder with the value
            # for this key in our dynamic data sources - e.g. `"$event"` is replaced with sources["event"].
            # This can be done only if we have the string "Self" amongst the allowed attributes,
            if not allowed_attributes or "Self" not in allowed_attributes:
                raise NotAllowedAttributeAccessInActionExpression(
                    param, data_source, "Self"
                )
            processed_params.append(data_source)
            continue

        if len(param_components) == 2:
            # There is an attribute access: for security reasons we're going to check that the
            # data source does allow this attribute to be read by actions
            attribute = param_components[1]
            if not allowed_attributes or attribute not in allowed_attributes:
                raise NotAllowedAttributeAccessInActionExpression(
                    param, data_source, attribute
                )
            processed_params.append(getattr(data_source, attribute))
            continue

        # For security reasons we only allow one level of attribute access in dynamic action expressions.
        # Doing otherwise would open a risk of exposing sensitive data in the "sub-objects" of the expression.
        # (i.e. "$event.sender" can be safe but that may not be the case of "$event.sender.__class__")
        raise TooManyLevelsInActionExpression(param)

    return tuple(processed_params)


if __name__ == "__main__":

    print(parse("foo"))

    print(parse("view.toggle('side')"))

    print(parse("view.toggle"))

    class Event:
        __allowed_attributes_for_actions__ = ["Self", "key"]
        key = "k"

    print(
        parse(
            "view.toggle('a', 1, {1: 'a', 2: 'b'}, '$event', '$event.key')",
            {"event": Event()},
        )
    )
