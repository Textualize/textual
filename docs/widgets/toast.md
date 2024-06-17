# Toast

!!! tip "Added in version 0.30.0"

A widget which displays a notification message.

- [ ] Focusable
- [ ] Container

!!! warning "Note that `Toast` isn't designed to be used directly in your applications, but it is instead used by [`notify`][textual.app.App.notify] to display a message when using Textual's built-in notification system."

## Styling

You can customize the style of Toasts by targeting the `Toast` [CSS type](../guide/CSS.md#type-selector).
For example:

```scss
Toast {
    padding: 3;
}
```

If you wish to change the location of Toasts, it is possible by targeting the `ToastRack` CSS type.
For example:

```scss
ToastRack {
        align: right top;
}
```

The three severity levels also have corresponding
[classes](../guide/CSS.md#class-name-selector), allowing you to target the
different styles of notification. They are:

- `-information`
- `-warning`
- `-error`

If you wish to tailor the notifications for your application you can add
rules to your CSS like this:

```scss
Toast.-information {
    /* Styling here. */
}

Toast.-warning {
    /* Styling here. */
}

Toast.-error {
    /* Styling here. */
}
```

You can customize just the title wih the `toast--title` class.
The following would make the title italic for an information toast:

```scss
Toast.-information .toast--title {
    text-style: italic;
}

```

## Example

=== "Output"

    ```{.textual path="docs/examples/widgets/toast.py"}
    ```

=== "toast.py"

    ```python
    --8<-- "docs/examples/widgets/toast.py"
    ```

## Reactive Attributes

This widget has no reactive attributes.

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

The toast widget provides the following component classes:

::: textual.widgets._toast.Toast.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

---

::: textual.widgets._toast.Toast
    options:
      show_root_heading: true
      show_root_toc_entry: true
