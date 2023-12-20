# Min-height

The `min-height` style sets a minimum height for a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
min-height: <a href="../../css_types/scalar">&lt;scalar&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `min-height` style accepts a [`<scalar>`](../css_types/scalar.md) that defines a lower bound for the [`height`](./height.md) of a widget.
That is, the height of a widget is never allowed to be under `min-height`.

## Example

The example below shows some placeholders with their height set to `50%`.
Then, we set `min-height` individually on each placeholder.

=== "Output"

    ```{.textual path="docs/examples/styles/min_height.py"}
    ```

=== "min_height.py"

    ```py
    --8<-- "docs/examples/styles/min_height.py"
    ```

=== "min_height.tcss"

    ```css hl_lines="13 17 21 25"
    --8<-- "docs/examples/styles/min_height.tcss"
    ```

    1. This won't affect the placeholder because its height is larger than the minimum height.

## CSS

```css
/* Set the minimum height to 10 rows */
min-height: 10;

/* Set the minimum height to 25% of the viewport height */
min-height: 25vh;
```

## Python

```python
# Set the minimum height to 10 rows
widget.styles.min_height = 10

# Set the minimum height to 25% of the viewport height
widget.styles.min_height = "25vh"
```

## See also

 - [`max-height`](./max_height.md) to set an upper bound on the height of a widget.
 - [`height`](./height.md) to set the height of a widget.
