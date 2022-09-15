# Color

The `color` rule sets the text color of a Widget.

## Syntax

```
color: <COLOR> | auto [<PERCENTAGE>];
```

## Example

This example sets a different text color to three different widgets.

=== "color.py"

    ```python
    --8<-- "docs/examples/styles/color.py"
    ```

=== "color.css"

    ```css
    --8<-- "docs/examples/styles/color.css"
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

/* Automatically choose color with suitable contrast for readability */
color: auto;
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
