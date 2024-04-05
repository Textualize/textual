# Grid-rows

The `grid-rows` style allows to define the height of the rows of the grid.

!!! note

    This style only affects widgets with `layout: grid`.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
grid-rows: <a href="../../../css_types/scalar">&lt;scalar&gt;</a>+;
--8<-- "docs/snippets/syntax_block_end.md"

The `grid-rows` style takes one or more [`<scalar>`](../../css_types/scalar.md) that specify the length of the rows of the grid.

If there are more rows in the grid than scalars specified in `grid-rows`, they are reused cyclically.
If the number of [`<scalar>`](../../css_types/scalar.md) is in excess, the excess is ignored.

## Example

The example below shows a grid with 10 labels laid out in a grid with 5 rows and 2 columns.

We set `grid-rows: 1fr 6 25%`.
Because there are more rows than scalars in the style definition, the scalars will be reused:

 - rows 1 and 4 have height `1fr`;
 - rows 2 and 5 have height `6`; and
 - row 3 has height `25%`.


=== "Output"

    ```{.textual path="docs/examples/styles/grid_rows.py"}
    ```

=== "grid_rows.py"

    ```py
    --8<-- "docs/examples/styles/grid_rows.py"
    ```

=== "grid_rows.tcss"

    ```css hl_lines="3"
    --8<-- "docs/examples/styles/grid_rows.tcss"
    ```

## CSS

```css
/* Set all rows to have 50% height */
grid-rows: 50%;

/* Every other row is twice as tall as the first one */
grid-rows: 1fr 2fr;
```

## Python

```py
grid.styles.grid_rows = "50%"
grid.styles.grid_rows = "1fr 2fr"
```

## See also

 - [`grid-columns`](./grid_columns.md) to specify the width of the grid columns.
