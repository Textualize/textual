# Tint

The `tint` style blends a color with the whole widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
tint: <a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

The tint style blends a [`<color>`](../css_types/color.md) with the widget. The color should likely have an _alpha_ component (specified directly in the color used or by the optional [`<percentage>`](../css_types/percentage.md)), otherwise the end result will obscure the widget content.

## Example

This examples shows a green tint with gradually increasing alpha.

=== "Output"

    ```{.textual path="docs/examples/styles/tint.py"}
    ```

=== "tint.py"

    ```python hl_lines="13"
    --8<-- "docs/examples/styles/tint.py"
    ```

    1. We set the tint to a `Color` instance with varying levels of opacity, set through the method [with_alpha][textual.color.Color.with_alpha].

=== "tint.tcss"

    ```css
    --8<-- "docs/examples/styles/tint.tcss"
    ```

## CSS

```css
/* A red tint (could indicate an error) */
tint: red 20%;

/* A green tint */
tint: rgba(0, 200, 0, 0.3);
```

## Python

```python
# A red tint
from textual.color import Color
widget.styles.tint = Color.parse("red").with_alpha(0.2);

# A green tint
widget.styles.tint = "rgba(0, 200, 0, 0.3)"
```
