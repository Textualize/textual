# Max-width

The `max-width` style sets a maximum width for a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
max-width: <a href="../../css_types/scalar">&lt;scalar&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `max-width` style accepts a [`<scalar>`](../css_types/scalar.md) that defines an upper bound for the [`width`](./width.md) of a widget.
That is, the width of a widget is never allowed to exceed `max-width`.

## Example

The example below shows some placeholders that were defined to span horizontally from the left edge of the terminal to the right edge.
Then, we set `max-width` individually on each placeholder.

=== "Output"

    ```{.textual path="docs/examples/styles/max_width.py"}
    ```

=== "max_width.py"

    ```py
    --8<-- "docs/examples/styles/max_width.py"
    ```

=== "max_width.tcss"

    ```css hl_lines="12 16 20 24"
    --8<-- "docs/examples/styles/max_width.tcss"
    ```

    1. This won't affect the placeholder because its width is less than the maximum width.

## CSS

```css
/* Set the maximum width to 10 rows */
max-width: 10;

/* Set the maximum width to 25% of the viewport width */
max-width: 25vw;
```

## Python

```python
# Set the maximum width to 10 rows
widget.styles.max_width = 10

# Set the maximum width to 25% of the viewport width
widget.styles.max_width = "25vw"
```

## See also

 - [`min-width`](./min_width.md) to set a lower bound on the width of a widget.
 - [`width`](./width.md) to set the width of a widget.
