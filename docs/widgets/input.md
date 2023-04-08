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

- [Input.Changed][textual.widgets.Input.Changed]
- [Input.Submitted][textual.widgets.Input.Submitted]

## Bindings

The Input widget defines the following bindings:

::: textual.widgets.Input.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The input widget provides the following component classes:

::: textual.widgets.Input.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Additional Notes

* The spacing around the text content is due to border. To remove it, set `border: none;` in your CSS.

---


::: textual.widgets.Input
    options:
      heading_level: 2
