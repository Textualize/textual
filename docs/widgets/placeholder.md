# Placeholder


A widget that is meant to have no complex functionality.
Use the placeholder widget when studying the layout of your app before having to develop your custom widgets.

The placeholder widget has variants that display different bits of useful information.
Clicking a placeholder will cycle through its variants.

- [ ] Focusable
- [ ] Container

## Example

The example below shows each placeholder variant.

=== "Output"

    ```{.textual path="docs/examples/widgets/placeholder.py"}
    ```

=== "placeholder.py"

    ```python
    --8<-- "docs/examples/widgets/placeholder.py"
    ```

=== "placeholder.css"

    ```css
    --8<-- "docs/examples/widgets/placeholder.css"
    ```

## Reactive Attributes

| Name       | Type   | Default     | Description                                        |
| ---------- | ------ | ----------- | -------------------------------------------------- |
| `variant`  | `str`  | `"default"` | Styling variant. One of `default`, `size`, `text`. |


## Messages

This widget sends no messages.

## See Also

* [Placeholder](../api/placeholder.md) code reference
