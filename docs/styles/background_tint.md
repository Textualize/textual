# Background-tint

The `background-tint` style modifies the background color by tinting (blending) it with a new color.

This style is typically used to subtly change the background of a widget for emphasis.
For instance the following would make a focused widget have a slightly lighter background.

```css
MyWidget:focus {
    background-tint: white 10%
}
```

The background tint color should typically have less than 100% alpha, in order to modify the background color.
If the alpha component is 100% then the tint color will replace the background color entirely.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
background-tint: <a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

The `background-tint` style requires a [`<color>`](../css_types/color.md) optionally followed by [`<percentage>`](../css_types/percentage.md) to specify the color's opacity (clamped between `0%` and `100%`).

## Examples

### Basic usage

This example shows background tint applied with alpha from 0 to 100%.

=== "Output"

    ```{.textual path="docs/examples/styles/background_tint.py"}
    ```

=== "background_tint.py"

    ```python
    --8<-- "docs/examples/styles/background_tint.py"
    ```

=== "background.tcss"

    ```css hl_lines="5-9"
    --8<-- "docs/examples/styles/background_tint.tcss"
    ```


## CSS

```css
/* 10% backgrouhnd tint */
background-tint: blue 10%;


/* 20% RGB color */
background-tint: rgb(100, 120, 200, 0.2);

```

## Python

You can use the same syntax as CSS, or explicitly set a `Color` object for finer-grained control.

```python
# Set 20% blue background tint
widget.styles.background_tint = "blue 20%"

from textual.color import Color
# Set with a color object
widget.styles.background_tint = Color(120, 60, 100, 0.5)
```

## See also

 - [`background`](./background.md) to set the background color of a widget.
 - [`color`](./color.md) to set the color of text in a widget.
