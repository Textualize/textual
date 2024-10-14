# Background

The `background` style sets the background color of a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
background: <a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

The `background` style requires a [`<color>`](../css_types/color.md) optionally followed by [`<percentage>`](../css_types/percentage.md) to specify the color's opacity (clamped between `0%` and `100%`).

## Examples

### Basic usage

This example creates three widgets and applies a different background to each.

=== "Output"

    ```{.textual path="docs/examples/styles/background.py"}
    ```

=== "background.py"

    ```python
    --8<-- "docs/examples/styles/background.py"
    ```

=== "background.tcss"

    ```css hl_lines="9 13 17"
    --8<-- "docs/examples/styles/background.tcss"
    ```

### Different opacity settings

The next example creates ten widgets laid out side by side to show the effect of setting different percentages for the background color's opacity.

=== "Output"

    ```{.textual path="docs/examples/styles/background_transparency.py"}
    ```

=== "background_transparency.py"

    ```python
    --8<-- "docs/examples/styles/background_transparency.py"
    ```

=== "background_transparency.tcss"

    ```css hl_lines="2 6 10 14 18 22 26 30 34 38"
    --8<-- "docs/examples/styles/background_transparency.tcss"
    ```

## CSS

```css
/* Blue background */
background: blue;

/* 20% red background */
background: red 20%;

/* RGB color */
background: rgb(100, 120, 200);

/* HSL color */
background: hsl(290, 70%, 80%);
```

## Python

You can use the same syntax as CSS, or explicitly set a `Color` object for finer-grained control.

```python
# Set blue background
widget.styles.background = "blue"
# Set through HSL model
widget.styles.background = "hsl(351,32%,89%)"

from textual.color import Color
# Set with a color object by parsing a string
widget.styles.background = Color.parse("pink")
widget.styles.background = Color.parse("#FF00FF")
# Set with a color object instantiated directly
widget.styles.background = Color(120, 60, 100)
```

## See also

 - [`background-tint`](./background_tint.md) to blend a color with the background.
 - [`color`](./color.md) to set the color of text in a widget.
