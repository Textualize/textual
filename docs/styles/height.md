# Height

The `height` style sets a widget's height.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
height: <a href="../../css_types/scalar">&lt;scalar&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `height` style needs a [`<scalar>`](../../css_types/scalar) to determine the vertical length of the widget.
By default, it sets the height of the content area, but if [`box-sizing`](./box_sizing) is set to `border-box` it sets the height of the border area.

## Examples

### Basic usage

This examples creates a widget with a height of 50% of the screen.

=== "Output"

    ```{.textual path="docs/examples/styles/height.py"}
    ```

=== "height.py"

    ```python
    --8<-- "docs/examples/styles/height.py"
    ```

=== "height.css"

    ```sass hl_lines="3"
    --8<-- "docs/examples/styles/height.css"
    ```

### All height formats

The next example creates a series of wide widgets with heights set with different units.
Open the CSS file tab to see the comments that explain how each height is computed.
(The output includes a vertical ruler on the right to make it easier to check the height of each widget.)

=== "Output"

    ```{.textual path="docs/examples/styles/height_comparison.py" lines=24 columns=80}
    ```

=== "height_comparison.py"

    ```py hl_lines="15-23"
    --8<-- "docs/examples/styles/height_comparison.py"
    ```

    1. The id of the placeholder identifies which unit will be used to set the height of the widget.

=== "height_comparison.css"

    ```sass hl_lines="2 5 8 11 14 17 20 23 26"
    --8<-- "docs/examples/styles/height_comparison.css"
    ```

    1. This sets the height to 2 lines.
    2. This sets the height to 12.5% of the space made available by the container. The container is 24 lines tall, so 12.5% of 24 is 3.
    3. This sets the height to 5% of the width of the direct container, which is the `VerticalScroll` container. Because it expands to fit all of the terminal, the width of the `VerticalScroll` is 80 and 5% of 80 is 4.
    4. This sets the height to 12.5% of the height of the direct container, which is the `VerticalScroll` container. Because it expands to fit all of the terminal, the height of the `VerticalScroll` is 24 and 12.5% of 24 is 3.
    5. This sets the height to 6.25% of the viewport width, which is 80. 6.25% of 80 is 5.
    6. This sets the height to 12.5% of the viewport height, which is 24. 12.5% of 24 is 3.
    7. This sets the height of the placeholder to be the optimal size that fits the content without scrolling.
    Because the content only spans one line, the placeholder has its height set to 1.
    8. This sets the height to `1fr`, which means this placeholder will have half the height of a placeholder with `2fr`.
    9. This sets the height to `2fr`, which means this placeholder will have twice the height of a placeholder with `1fr`.


## CSS

```sass
/* Explicit cell height */
height: 10;

/* Percentage height */
height: 50%;

/* Automatic height */
height: auto
```

## Python

```python
self.styles.height = 10  # Explicit cell height can be an int
self.styles.height = "50%"
self.styles.height = "auto"
```

## See also

 - [`max-height`](./max_height.md) and [`min-height`](./min_height.md) to limit the height of a widget.
 - [`width`](./width.md) to set the width of a widget.
