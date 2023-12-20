# Color

The `color` style sets the text color of a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
color: (<a href="../../css_types/color">&lt;color&gt;</a> | auto) [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

The `color` style requires a [`<color>`](../css_types/color.md) followed by an optional [`<percentage>`](../css_types/percentage.md) to specify the color's opacity.

You can also use the special value of `"auto"` in place of a color. This tells Textual to automatically select either white or black text for best contrast against the background.

## Examples

### Basic usage

This example sets a different text color for each of three different widgets.

=== "Output"

    ```{.textual path="docs/examples/styles/color.py"}
    ```

=== "color.py"

    ```python
    --8<-- "docs/examples/styles/color.py"
    ```

=== "color.tcss"

    ```css hl_lines="8 12 16"
    --8<-- "docs/examples/styles/color.tcss"
    ```

### Auto

The next example shows how `auto` chooses between a lighter or a darker text color to increase the contrast and improve readability.

=== "Output"

    ```{.textual path="docs/examples/styles/color_auto.py"}
    ```

=== "color_auto.py"

    ```py
    --8<-- "docs/examples/styles/color_auto.py"
    ```

=== "color_auto.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/styles/color_auto.tcss"
    ```

## CSS

```css
/* Blue text */
color: blue;

/* 20% red text */
color: red 20%;

/* RGB color */
color: rgb(100, 120, 200);

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

## See also

 - [`background`](./background.md) to set the background color in a widget.
