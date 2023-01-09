# Opacity

The `opacity` property sets the opacity/transparency of a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
opacity: <a href="../../css_types/number">&lt;number&gt;</a> | <a href="../../css_types/percentage">&lt;percentage&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The opacity of a widget can be set as a [`<number>`](../css_types/number.md)  or a [`<percentage>`](../css_types/percentage.md).
`0`/`0%` means no opacity, which is equivalent to full transparency.
Conversely, `1`/`100%` means full opacity, which is equivalent to no transparency.
Values outside of these ranges will be clamped.

## Example

This example shows, from top to bottom, increasing opacity values for a label with a border and some text.
When the opacity is zero, all we see is the (black) background.

=== "Output"

    ```{.textual path="docs/examples/styles/opacity.py"}
    ```

=== "opacity.py"

    ```python
    --8<-- "docs/examples/styles/opacity.py"
    ```

=== "opacity.css"

    ```sass hl_lines="2 6 10 14 18"
    --8<-- "docs/examples/styles/opacity.css"
    ```

## CSS

```sass
/* Fade the widget to 50% against its parent's background */
opacity: 50%;
```

## Python

```python
# Fade the widget to 50% against its parent's background
widget.styles.opacity = "50%"
```

## See also

 - [`text-opacity`](./text_opacity.md) to blend the color of a widget's content with its background color.
