# Button


A simple button widget which can be pressed using a mouse click or by pressing ++return++
when it has focus.

- [x] Focusable
- [ ] Container

## Example

The example below shows each button variant, and its disabled equivalent.
Clicking any of the non-disabled buttons in the example app below will result in the app exiting and the details of the selected button being printed to the console.

=== "Output"

    ```{.textual path="docs/examples/widgets/button.py"}
    ```

=== "button.py"

    ```python
    --8<-- "docs/examples/widgets/button.py"
    ```

=== "button.tcss"

    ```css
    --8<-- "docs/examples/widgets/button.tcss"
    ```

## Reactive Attributes

| Name       | Type            | Default     | Description                                                                                                                       |
|------------|-----------------|-------------|-----------------------------------------------------------------------------------------------------------------------------------|
| `label`    | `str`           | `""`        | The text that appears inside the button.                                                                                          |
| `variant`  | `ButtonVariant` | `"default"` | Semantic styling variant. One of `default`, `primary`, `success`, `warning`, `error`.                                             |
| `disabled` | `bool`          | `False`     | Whether the button is disabled or not. Disabled buttons cannot be focused or clicked, and are styled in a way that suggests this. |

## Messages

- [Button.Pressed][textual.widgets.Button.Pressed]

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

## Additional Notes

- The spacing between the text and the edges of a button are _not_ due to padding. The default styling for a `Button` has the `height` set to 3 lines and a `min-width` of 16 columns. To create a button with zero visible padding, you will need to change these values and also remove the border with `border: none;`.

---


::: textual.widgets.Button
    options:
      heading_level: 2

::: textual.widgets.button
    options:
      show_root_heading: true
      show_root_toc_entry: true
