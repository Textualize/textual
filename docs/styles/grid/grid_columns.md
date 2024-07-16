# Grid-columns

The `grid-columns` style allows to define the width of the columns of the grid.

!!! note

    This style only affects widgets with `layout: grid`.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
grid-columns: <a href="../../../css_types/scalar">&lt;scalar&gt;</a>+;
--8<-- "docs/snippets/syntax_block_end.md"

The `grid-columns` style takes one or more [`<scalar>`](../../css_types/scalar.md) that specify the length of the columns of the grid.

If there are more columns in the grid than scalars specified in `grid-columns`, they are reused cyclically.
If the number of [`<scalar>`](../../css_types/scalar.md) is in excess, the excess is ignored.

## Example

The example below shows a grid with 10 labels laid out in a grid with 2 rows and 5 columns.

We set `grid-columns: 1fr 16 2fr`.
Because there are more rows than scalars in the style definition, the scalars will be reused:

 - columns 1 and 4 have width `1fr`;
 - columns 2 and 5 have width `16`; and
 - column 3 has width `2fr`.


=== "Output"

    ```{.textual path="docs/examples/styles/grid_columns.py"}
    ```

=== "grid_columns.py"

    ```py
    --8<-- "docs/examples/styles/grid_columns.py"
    ```

=== "grid_columns.tcss"

    ```css hl_lines="3"
    --8<-- "docs/examples/styles/grid_columns.tcss"
    ```

## CSS

```css
/* Set all columns to have 50% width */
grid-columns: 50%;

/* Every other column is twice as wide as the first one */
grid-columns: 1fr 2fr;
```

## Python

```py
grid.styles.grid_columns = "50%"
grid.styles.grid_columns = "1fr 2fr"
```

## See also

 - [`grid-rows`](./grid_rows.md) to specify the height of the grid rows.
