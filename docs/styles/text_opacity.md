# Text-opacity

The `text-opacity` blends the color of the content of a widget with the color of the background.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
text-opacity: <a href="../../css_types/number">&lt;number&gt;</a> | <a href="../../css_types/percentage">&lt;percentage&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The text opacity can be set as a [`<number>`](../css_types/number.md) or a [`<percentage>`](../css_types/percentage.md).
`0`/`0%` means no opacity, which is equivalent to full transparency.
Conversely, `1`/`100%` means full opacity, which is equivalent to no transparency.
Values outside of these ranges will be clamped.

## Example

This example shows, from top to bottom, increasing `text-opacity` values.

=== "Output"

    ```{.textual path="docs/examples/styles/text_opacity.py"}
    ```

=== "text_opacity.py"

    ```python
    --8<-- "docs/examples/styles/text_opacity.py"
    ```

=== "text_opacity.css"

    ```sass hl_lines="2 6 10 14 18"
    --8<-- "docs/examples/styles/text_opacity.css"
    ```

## CSS

```sass
/* Set the text to be "half-faded" against the background of the widget */
text-opacity: 50%;
```

## Python

```python
# Set the text to be "half-faded" against the background of the widget
widget.styles.text_opacity = "50%"
```

## See also

 - [`opacity`](./opacity.md) to specify the transparency of a whole widget.
