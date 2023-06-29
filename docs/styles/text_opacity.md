# Text-opacity

The `text-opacity` style blends the foreground color (i.e. text) with the background color.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
text-opacity: <a href="../../css_types/number">&lt;number&gt;</a> | <a href="../../css_types/percentage">&lt;percentage&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"


The text opacity of a widget can be set as a [`<number>`](../css_types/number.md) or a [`<percentage>`](../css_types/percentage.md).
If given as a number, then `text-opacity` should be a value between 0 and 1, where 0 makes the foreground color match the background (effectively making text invisible) and 1 will display text as normal.
If given as a percentage, 0% will result in invisible text, and 100% will display fully opaque text.

Typically, if you set this value it would be somewhere between the two extremes.
For instance, setting `text-opacity` to `70%` would result in slightly faded text. Setting it to `0.3` would result in very dim text.

!!! warning

    Be careful not to set text opacity so low as to make it hard to read.


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

 - [`opacity`](./opacity.md) to specify the opacity of a whole widget.
