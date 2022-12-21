# Grid

There are a number of properties relating to the Textual `grid` layout.

For an in-depth look at the grid layout, visit the grid [guide](../guide/layout.md#grid).

| Property       | Description                                    |
|----------------|------------------------------------------------|
| [`column-span`](./column_span.md)  | Number of columns a cell spans.                |
| [`grid-columns`](./grid_columns.md) | Width of grid columns.                         |
| [`grid-gutter`](./grid_gutter.md)  | Spacing between grid cells.                    |
| [`grid-rows`](./grid_rows.md)    | Height of grid rows.                           |
| [`grid-size`](./grid_size.md)    | Number of columns and rows in the grid layout. |
| [`row-span`](./row_span.md)     | Number of rows a cell spans.                   |

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
column-span: <a href="../css_types/integer.md">&lt;integer&gt;</a>;

grid-columns: <a href="../css_types/scalar.md">&lt;scalar&gt;</a>+;

grid-gutter: <a href="../css_types/scalar.md">&lt;scalar&gt;</a> [<a href="../css_types/scalar.md">&lt;scalar&gt;</a>];

grid-rows: <a href="../css_types/scalar.md">&lt;scalar&gt;</a>+;

grid-size: <a href="../css_types/integer.md">&lt;integer&gt;</a> [<a href="../css_types/integer.md">&lt;integer&gt;</a>];

row-span: <a href="../css_types/integer.md">&lt;integer&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The styles `column-span` and `row-span` accept a single non-negative [`<integer>`](../../css_types/integer.md) while the style `grid-size` accepts one or two non-negative [`<integer>`](../../css_types/integer.md).

The style `grid-gutter` accepts one or two [`<scalar>`](../../css_types/scalar.md) while the styles `grid-columns` and `grid-rows` accept one or more.


### Values

#### &lt;integer&gt;

--8<-- "docs/snippets/type_syntax/integer.md"

#### &lt;scalar&gt;

--8<-- "docs/snippets/type_syntax/scalar.md"

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
