# Grid properties

There are a number of properties relating to the Textual `grid` layout.

For an in-depth look at the grid layout, visit the grid [guide](../guide/layout.md#grid).

| Property       | Description                                    |
|----------------|------------------------------------------------|
| `grid-size`    | Number of columns and rows in the grid layout. |
| `grid-rows`    | Height of grid rows.                           |
| `grid-columns` | Width of grid columns.                         |
| `grid-gutter`  | Spacing between grid cells.                    |
| `row-span`     | Number of rows a cell spans.                   |
| `column-span`  | Number of columns a cell spans.                |

## Syntax

```sass
grid-size: <INTEGER> [<INTEGER>];  /* columns first, then rows */
grid-rows: <SCALAR> ...;
grid-columns: <SCALAR> ...;
grid-gutter: <SCALAR>;
row-span: <INTEGER>;
column-span: <INTEGER>;
```

## Example
