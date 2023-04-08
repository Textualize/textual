# Footer

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

| Name            | Type  | Default | Description                                                                                               |
| --------------- | ----- | ------- | --------------------------------------------------------------------------------------------------------- |
| `highlight_key` | `str` | `None`  | Stores the currently highlighted key. This is typically the key the cursor is hovered over in the footer. |

## Messages

This widget sends no messages.

## Component Classes

The footer widget provides the following component classes:

::: textual.widgets.Footer.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Additional Notes

* You can prevent keybindings from appearing in the footer by setting the `show` argument of the `Binding` to `False`.
* You can customize the text that appears for the key itself in the footer using the `key_display` argument of `Binding`.


---


::: textual.widgets.Footer
    options:
      heading_level: 2
