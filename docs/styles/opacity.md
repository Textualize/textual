# Opacity

The `opacity` style sets the opacity of a widget.

While terminals are not capable of true opacity, Textual can create an approximation by blending widgets with their background color.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
opacity: <a href="../../css_types/number">&lt;number&gt;</a> | <a href="../../css_types/percentage">&lt;percentage&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The opacity of a widget can be set as a [`<number>`](../css_types/number.md) or a [`<percentage>`](../css_types/percentage.md).
If given as a number, then `opacity` should be a value between 0 and 1, where 0 is the background color and 1 is fully opaque.
If given as a percentage, 0% is the background color and 100% is fully opaque.

Typically, if you set this value it would be somewhere between the two extremes.
For instance, setting the opacity of a widget to `70%` will make it appear dimmer than surrounding widgets, which could be used to display a *disabled* state.


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
