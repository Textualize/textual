# Dialog

!!! tip "Added in version x.y.z"

A container widget designed to help build classic dialog layouts.

- [ ] Focusable
- [X] Container

## Guide

### Composing a `Dialog`

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

### Dialog variants

Much like with [`Button`](./button.md) the `Dialog` widget has variants;
these provide ready-made semantic styles for your dialogs. As well as
`default`, there are also:

#### "success"

A `success` variant `Dialog` can be created by either passing `"success"` as
the `variant` parameter when [creating the
`Dialog`](#textual.widgets.Dialog), by setting the [`variant`
reactive](#textual.widgets._dialog.Dialog.variant) to `"success"`, or by
calling the [`Dialog.success`
constructor](#textual.widgets._dialog.Dialog.success).

=== "Success variant dialog"

    ```{.textual path="docs/examples/widgets/dialog_success.py"}
    ```

=== "dialog_success.py"

    ~~~python
    --8<-- "docs/examples/widgets/dialog_success.py"
    ~~~

#### "warning"

A `warning` variant `Dialog` can be created by either passing `"warning"` as
the `variant` parameter when [creating the
`Dialog`](#textual.widgets.Dialog), by setting the [`variant`
reactive](#textual.widgets._dialog.Dialog.variant) to `"warning"`, or by
calling the [`Dialog.warning`
constructor](#textual.widgets._dialog.Dialog.warning).

=== "Warning variant dialog"

    ```{.textual path="docs/examples/widgets/dialog_warning.py"}
    ```

=== "dialog_warning.py"

    ~~~python
    --8<-- "docs/examples/widgets/dialog_warning.py"
    ~~~

#### "error"

An `error` variant `Dialog` can be created by either passing `"error"` as
the `variant` parameter when [creating the
`Dialog`](#textual.widgets.Dialog), by setting the [`variant`
reactive](#textual.widgets._dialog.Dialog.variant) to `"error"`, or by
calling the [`Dialog.error`
constructor](#textual.widgets._dialog.Dialog.error).

=== "Error variant dialog"

    ```{.textual path="docs/examples/widgets/dialog_error.py"}
    ```

=== "dialog_error.py"

    ~~~python
    --8<-- "docs/examples/widgets/dialog_error.py"
    ~~~

## Styling the Dialog

The `Dialog` will always contain one sub-widget, called `Body`; this is
where the widgets that are not in the
[`ActionArea`](#textual.widgets._dialog.Dialog.ActionArea) are held. If you
wish to style the main body you can target `Dialog Body` in your CSS:

=== "dialog_styling.tcss"

    ~~~css hl_lines="7-12"
    --8<-- "docs/examples/widgets/dialog_styling.tcss"
    ~~~

=== "Styled dialog body"

    ```{.textual path="docs/examples/widgets/dialog_styling.py"}
    ```

=== "dialog_styling.py"

    ~~~python
    --8<-- "docs/examples/widgets/dialog_styling.py"
    ~~~


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
