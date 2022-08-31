# Opacity

The `opacity` property can be used to make a widget partially or fully transparent.


## Syntax

```
opacity: <FRACTIONAL>;
```

### Values

As a fractional property, `opacity` can be set to either a float (between 0 and 1),
or a percentage, e.g. `45%`.
Float values will be clamped between 0 and 1.
Percentage values will be clamped between 0% and 100%.

## Example

This example shows, from top to bottom, increasing opacity values.

=== "opacity.py"

    ```python
    --8<-- "docs/examples/styles/opacity.py"
    ```

=== "opacity.css"

    ```scss
    --8<-- "docs/examples/styles/opacity.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/opacity.py"}
    ```

## CSS

```sass
/* Fade the widget to 50% against its parent's background */
Widget {
    opacity: 50%;
}
```

## Python

```python
# Fade the widget to 50% against its parent's background
widget.styles.opacity = "50%"
```
