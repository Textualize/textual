# Checkbox

A simple checkbox widget which stores a boolean value.

- [x] Focusable
- [ ] Container

## Example

The example below shows checkboxes in various states.

=== "Output"

    ```{.textual path="docs/examples/widgets/checkbox.py"}
    ```

=== "checkbox.py"

    ```python
    --8<-- "docs/examples/widgets/checkbox.py"
    ```

=== "checkbox.css"

    ```sass
    --8<-- "docs/examples/widgets/checkbox.css"
    ```

## Reactive Attributes

| Name    | Type   | Default | Description                        |
| ------- | ------ | ------- | ---------------------------------- |
| `value` | `bool` | `False` | The default value of the checkbox. |

## Bindings

The checkbox widget defines directly the following bindings:

::: textual.widgets.Checkbox.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The checkbox widget provides the following component classes:

::: textual.widgets.Checkbox.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Messages

### ::: textual.widgets.Checkbox.Changed

## Additional Notes

- To remove the spacing around a checkbox, set `border: none;` and `padding: 0;`.

## See Also

- [Checkbox](../api/checkbox.md) code reference
