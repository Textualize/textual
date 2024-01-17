# Dialog

!!! tip "Added in version x.y.z"

A container widget designed to help build classic dialog layouts.

- [ ] Focusable
- [X] Container

## Guide

The `Dialog` widget helps with laying out a classic dialog, one with
"content" widgets in the main body, and with a horizontal area of "action
items" (which will normally be buttons) at the bottom. This is ideally done
while [composing with a context
manager](../guide/layout/#composing-with-context-managers). For example:

=== "dialog_simple.py"

    ~~~python
    --8<-- "docs/examples/widgets/dialog_simple.py"
    ~~~

    1. All widgets composed within here will be part of the dialog.
    2. The label is part of the body of the dialog.
    3. This introduces the area of horizontal-layout widgets at the bottom of the dialog.
    4. This button goes into the action area.
    5. This button goes into the action area.

=== "dialog_simple.tcss"

    ```css
    --8<-- "docs/examples/widgets/dialog_simple.tcss"
    ```

This is how the resulting dialog looks:

```{.textual path="docs/examples/widgets/dialog_simple.py"}
```

The items in the `ActionArea` of a dialog are aligned to the right; but it
is a common approach to include one or more widgets in the action area that
are aligned to the left. This can be done too:

The dialog can contain any Textual widget, and the "action area" (where
buttons ordinarily live) can contain other widgets too. For example:

=== "dialog_complex.py"

    ~~~python
    --8<-- "docs/examples/widgets/dialog_complex.py"
    ~~~

    1. This widget goes into the main body of the dialog.
    2. This widget goes into the main body of the dialog.
    3. This widget goes into the main body of the dialog.
    4. This widget goes into the main body of the dialog.
    5. This introduces the area of horizontal-layout widgets at the bottom of the dialog.
    6. Widgets within this group will be aligned to the left.
    7. The `Checkbox` will be on the left of the action area.
    8. The `Button` will be to the right of the action area.
    9. The `Button` will be to the right of the action area.
    10. The `Button` will be to the right of the action area.

=== "dialog_complex.tcss"

    ```css
    --8<-- "docs/examples/widgets/dialog_complex.tcss"
    ```

The resulting dialog looks like this:

```{.textual path="docs/examples/widgets/dialog_complex.py"}
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
