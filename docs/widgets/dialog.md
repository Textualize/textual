# Dialog

!!! tip "Added in version x.y.z"

A container widget designed to help build classic dialog layouts.

- [ ] Focusable
- [X] Container

## Example

### Simple example

The example below shows a classic confirmation dialog, with a title, some
text to prompt the user, and then a pair of buttons to confirm or cancel the
following operation.

=== "Output"

    ```{.textual path="docs/examples/widgets/dialog_simple.py"}
    ```

=== "dialog_simple.py"

    ```python
    --8<-- "docs/examples/widgets/dialog_simple.py"
    ```

=== "dialog_simple.tcss"

    ```css
    --8<-- "docs/examples/widgets/dialog_simple.tcss"
    ```

### Longer example

The dialog can contain any Textual widget, and the "action area" (where
buttons ordinarily live) can contain other widgets too. For example:

=== "Output"

    ```{.textual path="docs/examples/widgets/dialog_complex.py"}
    ```

=== "dialog_complex.py"

    ```python
    --8<-- "docs/examples/widgets/dialog_complex.py"
    ```

=== "dialog_complex.tcss"

    ```css
    --8<-- "docs/examples/widgets/dialog_complex.tcss"
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
