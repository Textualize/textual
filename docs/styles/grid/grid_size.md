# Grid-size

The `grid-size` style sets the number of columns and rows in a grid layout.

The number of rows can be left unspecified and it will be computed automatically.

!!! note

    This style only affects widgets with `layout: grid`.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
grid-size: <a href="../../../css_types/integer">&lt;integer&gt;</a> [<a href="../../../css_types/integer">&lt;integer&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

The `grid-size` style takes one or two non-negative [`<integer>`](../../css_types/integer.md).
The first defines how many columns there are in the grid.
If present, the second one sets the number of rows – regardless of the number of children of the grid –, otherwise the number of rows is computed automatically.

## Examples

### Columns and rows

In the first example, we create a grid with 2 columns and 5 rows, although we do not have enough labels to fill in the whole grid:

=== "Output"

    ```{.textual path="docs/examples/styles/grid_size_both.py"}
    ```

=== "grid_size_both.py"

    ```py
    --8<-- "docs/examples/styles/grid_size_both.py"
    ```

=== "grid_size_both.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/styles/grid_size_both.tcss"
    ```

    1. Create a grid with 2 columns and 4 rows.

### Columns only

In the second example, we create a grid with 2 columns and however many rows are needed to display all of the grid children:

=== "Output"

    ```{.textual path="docs/examples/styles/grid_size_columns.py"}
    ```

=== "grid_size_columns.py"

    ```py
    --8<-- "docs/examples/styles/grid_size_columns.py"
    ```

=== "grid_size_columns.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/styles/grid_size_columns.tcss"
    ```

    1. Create a grid with 2 columns and however many rows.

## CSS

```css
/* Grid with 3 columns and 5 rows */
grid-size: 3 5;

/* Grid with 4 columns and as many rows as needed */
grid-size: 4;
```

## Python

To programmatically change the grid size, the number of rows and columns must be specified separately:

```py
widget.styles.grid_size_rows = 3
widget.styles.grid_size_columns = 6
```
