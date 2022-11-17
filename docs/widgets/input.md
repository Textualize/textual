# Input

A single-line text input widget.

- [x] Focusable
- [ ] Container

## Example

The example below shows how you might create a simple form using two `Input` widgets.

=== "Output"

    ```{.textual path="docs/examples/widgets/input.py" press="tab,D,a,r,r,e,n"}
    ```

=== "input.py"

    ```python
    --8<-- "docs/examples/widgets/input.py"
    ```

## Reactive Attributes

| Name              | Type   | Default | Description                                                     |
| ----------------- | ------ | ------- | --------------------------------------------------------------- |
| `cursor_blink`    | `bool` | `True`  | True if cursor blinking is enabled.                             |
| `value`           | `str`  | `""`    | The value currently in the text input.                          |
| `cursor_position` | `int`  | `0`     | The index of the cursor in the value string.                    |
| `placeholder`     | `str`  | `str`   | The dimmed placeholder text to display when the input is empty. |
| `password`        | `bool` | `False` | True if the input should be masked.                             |

## Messages

### Changed

The `Input.Changed` message is sent when the value in the text input changes.

- [x] Bubbles

#### Attributes

| attribute | type  | purpose                          |
| --------- | ----- | -------------------------------- |
| `value`   | `str` | The new value in the text input. |


### Submitted

The `Input.Submitted` message is sent when you press ++enter++ with the text field submitted.

- [x] Bubbles

#### Attributes

| attribute | type  | purpose                          |
| --------- | ----- | -------------------------------- |
| `value`   | `str` | The new value in the text input. |


## Additional Notes

* The spacing around the text content is due to border. To remove it, set `border: none;` in your CSS.

## See Also

* [Input](../api/input.md) code reference
