# Grid

There are a number of properties relating to the Textual `grid` layout.

For an in-depth look at the grid layout, visit the grid [guide](../guide/layout.md#grid).

| Property       | Description                                    |
|----------------|------------------------------------------------|
| [`grid-size`](./grid_size.md)    | Number of columns and rows in the grid layout. |
| [`grid-rows`](./grid_rows.md)    | Height of grid rows.                           |
| [`grid-columns`](./grid_columns.md) | Width of grid columns.                         |
| [`grid-gutter`](./grid_gutter.md)  | Spacing between grid cells.                    |
| [`row-span`](./row_span.md)     | Number of rows a cell spans.                   |
| [`column-span`](./column_span.md)  | Number of columns a cell spans.                |

## Syntax

```sass
grid-size: <INTEGER> [<INTEGER>];
/* columns first, then rows */
grid-rows: <SCALAR> . . .;
grid-columns: <SCALAR> . . .;
grid-gutter: <SCALAR>;
row-span: <INTEGER>;
column-span: <INTEGER>;
```

## Example

The example below shows all the properties above in action.
The `grid-size: 3 4;` declaration sets the grid to 3 columns and 4 rows.
The first cell of the grid, tinted magenta, shows a cell spanning multiple rows and columns.
The spacing between grid cells is because of the `grid-gutter` declaration.

=== "Output"

    ```{.textual path="docs/examples/styles/grid.py"}
    ```

=== "grid.py"

    ```python
    --8<-- "docs/examples/styles/grid.py"
    ```

=== "grid.css"

    ```sass
    --8<-- "docs/examples/styles/grid.css"
    ```

!!! warning

    The properties listed on this page will only work when the layout is `grid`.
