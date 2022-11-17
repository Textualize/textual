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

    ```css
    --8<-- "docs/examples/widgets/checkbox.css"
    ```

## Reactive Attributes

| Name    | Type   | Default | Description                        |
| ------- | ------ | ------- | ---------------------------------- |
| `value` | `bool` | `False` | The default value of the checkbox. |

## Messages

### Pressed

The `Checkbox.Changed` message is sent when the checkbox is toggled.

- [x] Bubbles

#### Attributes

| attribute | type   | purpose                        |
| --------- | ------ | ------------------------------ |
| `value`   | `bool` | The new value of the checkbox. |

## Additional Notes

- To remove the spacing around a checkbox, set `border: none;` and `padding: 0;`.
- The `.checkbox--switch` component class can be used to change the color and background of the switch.
- When focused, the ++enter++ or ++space++ keys can be used to toggle the checkbox.

## See Also

- [Checkbox](../api/checkbox.md) code reference
