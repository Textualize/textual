# Footer

!!! tip "Added in version 0.63.0"

A simple footer widget which is docked to the bottom of its parent container. Displays
available keybindings for the currently focused widget.

- [ ] Focusable
- [ ] Container


## Example

The example below shows an app with a single keybinding that contains only a `Footer`
widget. Notice how the `Footer` automatically displays the keybinding.

=== "Output"

    ```{.textual path="docs/examples/widgets/footer.py"}
    ```

=== "footer.py"

    ```python
    --8<-- "docs/examples/widgets/footer.py"
    ```

## Reactive Attributes

| Name                   | Type   | Default | Description                                                                                |
| ---------------------- | ------ | ------- | ------------------------------------------------------------------------------------------ |
| `compact`              | `bool` | `False` | Display a more compact footer.                                                             |
| `show_command_palette` | `bool` | `True`  | Display the key to invoke the command palette (show on the right hand side of the footer). |

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.


## Additional Notes

* You can prevent keybindings from appearing in the footer by setting the `show` argument of the `Binding` to `False`.
* You can customize the text that appears for the key itself in the footer using the `key_display` argument of `Binding`.


---


::: textual.widgets.Footer
    options:
      heading_level: 2
