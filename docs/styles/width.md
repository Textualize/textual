# Width

The `width` style sets a widget's width.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
width: <a href="../../css_types/scalar">&lt;scalar&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The style `width` needs a [`<scalar>`](../../css_types/scalar) to determine the horizontal length of the width.
By default, it sets the width of the content area, but if [`box-sizing`](./box_sizing) is set to `border-box` it sets the width of the border area.

## Examples

### Basic usage

This example adds a widget with 50% width of the screen.

=== "Output"

    ```{.textual path="docs/examples/styles/width.py"}
    ```

=== "width.py"

    ```python
    --8<-- "docs/examples/styles/width.py"
    ```

=== "width.css"

    ```sass hl_lines="3"
    --8<-- "docs/examples/styles/width.css"
    ```

### All width formats

=== "Output"

    ```{.textual path="docs/examples/styles/width_comparison.py" lines=24 columns=80}
    ```

=== "width_comparison.py"

    ```py hl_lines="15-23"
    --8<-- "docs/examples/styles/width_comparison.py"
    ```

    1. The id of the placeholder identifies which unit will be used to set the width of the widget.

=== "width_comparison.css"

    ```sass hl_lines="2 5 8 11 14 17 20 23 26"
    --8<-- "docs/examples/styles/width_comparison.css"
    ```

    1. This sets the width to 9 columns.
    2. This sets the width to 12.5% of the space made available by the container.
    The container is 80 columns wide, so 12.5% of 80 is 10.
    3. This sets the width to 10% of the width of the direct container, which is the `Horizontal` container.
    Because it expands to fit all of the terminal, the width of the `Horizontal` is 80 and 10% of 80 is 8.
    4. This sets the width to 25% of the height of the direct container, which is the `Horizontal` container.
    Because it expands to fit all of the terminal, the height of the `Horizontal` is 24 and 25% of 24 is 6.
    5. This sets the width to 15% of the viewport width, which is 80.
    15% of 80 is 12.
    6. This sets the width to 25% of the viewport height, which is 24.
    25% of 24 is 6.
    7. This sets the width of the placeholder to be the optimal size that fits the content without scrolling.
    Because the content is the string `"#auto"`, the placeholder has its width set to 5.
    8. This sets the width to `1fr`, which means this placeholder will have a third of the width of a placeholder with `3fr`.
    9. This sets the width to `3fr`, which means this placeholder will have triple the width of a placeholder with `1fr`.


## CSS

```sass
/* Explicit cell width */
width: 10;

/* Percentage width */
width: 50%;

/* Automatic width */
width: auto;
```

## Python

```python
widget.styles.width = 10
widget.styles.width = "50%
widget.styles.width = "auto"
```

## See also

 - [`max-width`](./max_width.md) and [`min-width`](./min_width.md) to limit the width of a widget.
 - [`height`](./height.md) to set the height of a widget.
