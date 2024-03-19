# LoadingIndicator

!!! tip "Added in version 0.15.0"

Displays pulsating dots to indicate when data is being loaded.

- [ ] Focusable
- [ ] Container


!!! tip

    Widgets have a [`loading`][textual.widget.Widget.loading] reactive which
    you can use to temporarily replace your widget with a `LoadingIndicator`.
    See the [Loading Indicator](../guide/widgets.md#loading-indicator) section
    in the Widgets guide for details.


## Example

Simple usage example:

=== "Output"

    ```{.textual path="docs/examples/widgets/loading_indicator.py"}
    ```

=== "loading_indicator.py"

    ```python
    --8<-- "docs/examples/widgets/loading_indicator.py"
    ```

## Changing Indicator Color

You can set the color of the loading indicator by setting its `color` style.

Here's how you would do that with CSS:

```css
LoadingIndicator {
    color: red;
}
```

## Reactive Attributes

This widget has no reactive attributes.

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

---


::: textual.widgets.LoadingIndicator
    options:
      heading_level: 2
