# Background

The `background` rule sets the background color of the widget.

## Syntax

```
background: <COLOR> [<PERCENTAGE>];
```

## Example

This example creates three widgets and applies a different background to each.

=== "background.py"

    ```python
    --8<-- "docs/examples/styles/background.py"
    ```

=== "background.css"

    ```sass
    --8<-- "docs/examples/styles/background.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/background.py"}
    ```

## CSS

```sass
/* Blue background */
background: blue;

/* 20% red background */
background: red 20%;

/* RGB color */
background: rgb(100,120,200);
```

## Python

You can use the same syntax as CSS, or explicitly set a `Color` object for finer-grained control.

```python
# Set blue background
widget.styles.background = "blue"

from textual.color import Color
# Set with a color object
widget.styles.background = Color.parse("pink")
widget.styles.background = Color(120, 60, 100)
```
