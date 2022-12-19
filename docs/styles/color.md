# Color

The `color` rule sets the text color of a widget with an optional.

## Syntax

```
color: (<COLOR> | auto) [<PERCENTAGE>];
```

Use `auto` to automatically choose a color with suitable contrast for readability.

--8<-- "docs/styles/snippets/color_css_syntax.md"

The optional [percentage](./css_units/percentage.md) sets the transparency level and will override any transparency specified directly in the color.

## Examples

This example sets a different text color for each of three different widgets.

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

The next example shows how `auto` chooses between a lighter or a darker text color to increase the contrast and improve readability.

=== "color_auto.py"

    ```py
    --8<-- "docs/examples/styles/color_auto.py"
    ```

=== "color_auto.css"

    ```css hl_lines="2"
    --8<-- "docs/examples/styles/color_auto.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/color_auto.py"}
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
