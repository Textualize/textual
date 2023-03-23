# Max-height

The `max-height` style sets a maximum height for a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
max-height: <a href="../../css_types/scalar">&lt;scalar&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `max-height` style accepts a [`<scalar>`](../../css_types/scalar) that defines an upper bound for the [`height`](./height) of a widget.
That is, the height of a widget is never allowed to exceed `max-height`.

## Example

The example below shows some placeholders that were defined to span vertically from the top edge of the terminal to the bottom edge.
Then, we set `max-height` individually on each placeholder.

=== "Output"

    ```{.textual path="docs/examples/styles/max_height.py"}
    ```

=== "max_height.py"

    ```py
    --8<-- "docs/examples/styles/max_height.py"
    ```

=== "max_height.css"

    ```sass hl_lines="12 16 20 24"
    --8<-- "docs/examples/styles/max_height.css"
    ```

    1. This won't affect the placeholder because its height is less than the maximum height.

## CSS

```sass
/* Set the maximum height to 10 rows */
max-height: 10;

/* Set the maximum height to 25% of the viewport height */
max-height: 25vh;
```

## Python

```python
# Set the maximum height to 10 rows
widget.styles.max_height = 10

# Set the maximum height to 25% of the viewport height
widget.styles.max_height = "25vh"
```

## See also

 - [`min-height`](./min_height.md) to set a lower bound on the height of a widget.
 - [`height`](./height.md) to set the height of a widget.
