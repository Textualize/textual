# Button


A simple button widget which can be pressed using a mouse click or by pressing ++return++
when it has focus.

- [x] Focusable
- [ ] Container

## Example

The example below shows each button variant, and its disabled equivalent.
Clicking any of the non-disabled buttons in the example app below will result the app exiting and the details of the selected button being printed to the console.

=== "Output"

    ```{.textual path="docs/examples/widgets/button.py"}
    ```

=== "button.py"

    ```python
    --8<-- "docs/examples/widgets/button.py"
    ```

=== "button.css"

    ```css
    --8<-- "docs/examples/widgets/button.css"
    ```

## Reactive Attributes

| Name       | Type   | Default     | Description                                                                                                                       |
| ---------- | ------ | ----------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `label`    | `str`  | `""`        | The text that appears inside the button.                                                                                          |
| `variant`  | `str`  | `"default"` | Semantic styling variant. One of `default`, `primary`, `success`, `warning`, `error`.                                             |
| `disabled` | `bool` | `False`     | Whether the button is disabled or not. Disabled buttons cannot be focused or clicked, and are styled in a way that suggests this. |

## Messages

### Pressed

The `Button.Pressed` message is sent when the button is pressed.

- [x] Bubbles

#### Attributes

_No other attributes_

## Additional Notes

* The spacing between the text and the edges of a button are due to border, _not_ padding. To create a button with zero visible padding, use the `border: none;` declaration.

## See Also

* [Button](../api/button.md) code reference
