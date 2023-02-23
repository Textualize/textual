# RadioButton

A simple radio button which stores a boolean value.

- [x] Focusable
- [ ] Container

## Example

The example below shows radio buttons, used within [RadioSet][textual.widgets.RadioSet]s.

=== "Output"

    ```{.textual path="docs/examples/widgets/radio_set.py"}
    ```

=== "radio_set.py"

    ```python
    --8<-- "docs/examples/widgets/radio_set.py"
    ```

=== "radio_set.css"

    ```sass
    --8<-- "docs/examples/widgets/radio_set.css"
    ```

## Reactive Attributes

| Name    | Type   | Default | Description                    |
|---------|--------|---------|--------------------------------|
| `value` | `bool` | `False` | The value of the radio button. |

## Bindings

The radio button widget defines directly the following bindings:

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

### ::: textual.widgets.RadioButton.Changed

## See Also

- [RadioButton](../api/radiobutton.md) code reference
