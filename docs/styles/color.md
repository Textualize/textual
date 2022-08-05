# Color

The `color` rule sets the text color of a Widget.

=== "color.py"

    ```python
    --8<-- "docs/examples/styles/color.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/color.py"}
    ```

## CSS

```sass
/* Blue text */
color: blue;

/* 20% red text */
color: red 20%;

/* RGB color */
color: rgb(100,120,200);
```

## Python

You can use the same syntax as CSS, or explicitly set a `Color` object.

```python
# Set blue text
widget.styles.color = "blue"

from textual.color import Color
# Set with a color object
widget.styles.color = Color.parse("pink")

```
