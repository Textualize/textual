# Text-opacity

The `text-opacity` blends the color of the content of a widget with the color of the background.

## Syntax

```
text-opacity: <FRACTIONAL>;
```

### Values

As a fractional property, `text-opacity` can be set to either a float (between 0 and 1),
or a percentage, e.g. `45%`.
Float values will be clamped between 0 and 1.
Percentage values will be clamped between 0% and 100%.

## Example

This example shows, from top to bottom, increasing text-opacity values.

=== "text_opacity.py"

    ```python
    --8<-- "docs/examples/styles/text_opacity.py"
    ```

=== "text_opacity.css"

    ```css
    --8<-- "docs/examples/styles/text_opacity.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/text_opacity.py"}
    ```

## CSS

```sass
/* Set the text to be "half-faded" against the background of the widget */
Widget {
    text-opacity: 50%;
}
```

## Python

```python
# Set the text to be "half-faded" against the background of the widget
widget.styles.text_opacity = "50%"
```
