# Min-width

The `min-width` style sets a minimum width for a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
min-width: <a href="../../css_types/scalar">&lt;scalar&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `min-width` style accepts a [`<scalar>`](../../css_types/scalar) that defines a lower bound for the [`width`](./width) of a widget.
That is, the width of a widget is never allowed to be under `min-width`.

## Example

The example below shows some placeholders with their width set to `50%`.
Then, we set `min-width` individually on each placeholder.

=== "Output"

    ```{.textual path="docs/examples/styles/min_width.py"}
    ```

=== "min_width.py"

    ```py
    --8<-- "docs/examples/styles/min_width.py"
    ```

=== "min_width.css"

    ```sass hl_lines="13 17 21 25"
    --8<-- "docs/examples/styles/min_width.css"
    ```

    1. This won't affect the placeholder because its width is larger than the minimum width.

## CSS

```sass
/* Set the minimum width to 10 rows */
min-width: 10;

/* Set the minimum width to 25% of the viewport width */
min-width: 25vw;
```

## Python

```python
# Set the minimum width to 10 rows
widget.styles.min_width = 10

# Set the minimum width to 25% of the viewport width
widget.styles.min_width = "25vw"
```

## See also

 - [`max-width`](./max_width.md) to set an upper bound on the width of a widget.
 - [`width`](./width.md) to set the width of a widget.
