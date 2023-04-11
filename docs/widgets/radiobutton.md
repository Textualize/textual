# RadioButton

!!! tip "Added in version 0.13.0"

A simple radio button which stores a boolean value.

- [x] Focusable
- [ ] Container

A radio button is best used with others inside a [`RadioSet`](./radioset.md).

## Example

The example below shows radio buttons, used within a [`RadioSet`](./radioset.md).

=== "Output"

    ```{.textual path="docs/examples/widgets/radio_button.py"}
    ```

=== "radio_button.py"

    ```python
    --8<-- "docs/examples/widgets/radio_button.py"
    ```

=== "radio_button.css"

    ```sass
    --8<-- "docs/examples/widgets/radio_button.css"
    ```

## Reactive Attributes

| Name    | Type   | Default | Description                    |
| ------- | ------ | ------- | ------------------------------ |
| `value` | `bool` | `False` | The value of the radio button. |

## Bindings

The radio button widget defines the following bindings:

::: textual.widgets._toggle_button.ToggleButton.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The radio button widget provides the following component classes:

::: textual.widgets._toggle_button.ToggleButton.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Messages

- [RadioButton.Changed][textual.widgets.RadioButton.Changed]

## See Also

- [RadioSet](./radioset.md)

---


::: textual.widgets.RadioButton
    options:
      heading_level: 2
