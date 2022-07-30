# Background

The `background` rule sets the background color of the widget.

=== "background.py"

    ```python
    --8<-- "docs/examples/styles/background.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/background.py"}
    ```

## CSS

```sass
/* Blue background */
background: blue;

/* 20% red backround */
background: red 20%;

/* RGB color */
background: rgb(100,120,200);
```

## Python

You can use the same syntax as CSS, or explicitly set a Color object.

```python
# Set blue background
widget.styles.background = "blue"

from textual.color import Color
# Set with a color object
widget.styles.background = Color.parse("pink")

```
