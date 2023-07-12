# Toast

!!! tip "Added in version ?.??.?"

A widget which displays a notification message.

- [ ] Focusable
- [ ] Container

Note that `Toast` isn't designed to be used directly in your applications,
but it is instead used by [`notify`][textual.app.App.notify] to
display a message when using Textual's built-in notification system.

## Styling

As just mentioned: while `Toast` isn't designed to be used directly in your
applications, it can be styled using [Textual's CSS](/guide/CSS/). The main
approach to styling would be to target the `Toast`
[type](/guide/CSS/#type-selector). For example:

```scss
Toast {
    padding: 3;
}
```

The three severity levels also have corresponding
[classes](/guide/CSS/#class-name-selector), allowing you to target the
different styles of notification. They are:

- `information`
- `warning`
- `error`

If you wish to tailor the notifications for your application you can add
rules to your CSS like this:

```scss
Toast.information {
    /* Styling here. */
}

Toast.warning {
    /* Styling here. */
}

Toast.error {
    /* Styling here. */
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

---

::: textual.widgets._toast
    options:
      show_root_heading: true
      show_root_toc_entry: true
