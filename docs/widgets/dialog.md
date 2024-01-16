# Dialog

!!! tip "Added in version x.y.z"

Widget description.

- [ ] Focusable
- [X] Container


## Example

Example app showing the widget:

=== "Output"

    ```{.textual path="docs/examples/widgets/dialog.py"}
    ```

=== "checkbox.py"

    ```python
    --8<-- "docs/examples/widgets/dialog.py"
    ```

=== "checkbox.tcss"

    ```css
    --8<-- "docs/examples/widgets/dialog.tcss"
    ```


## Reactive Attributes

| Name      | Type            | Default     | Description                                                                |
|-----------|-----------------|-------------|----------------------------------------------------------------------------|
| `title`   | `str`           | `""`        | The title of the dialog.                                                   |
| `variant` | `DialogVariant` | `"default"` | Semantic styling variant. One of `default`, `success`, `warning`, `error`. |

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component classes

This widget has no component classes.

## Additional notes

- Did you know this?
- Another pro tip.


## See also

- [ModalScreen](../guide/screens.md#modal-screens)


---


::: textual.widgets.Dialog
    options:
      heading_level: 2

::: textual.widgets.dialog
    options:
      show_root_heading: true
      show_root_toc_entry: true
