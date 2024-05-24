# Grid

There are a number of styles relating to the Textual `grid` layout.

For an in-depth look at the grid layout, visit the grid [guide](../../guide/layout.md#grid).

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
<a href="./column_span/">column-span</a>: <a href="../../../css_types/integer">&lt;integer&gt;</a>;

<a href="./grid_columns/">grid-columns</a>: <a href="../../../css_types/scalar">&lt;scalar&gt;</a>+;

<a href="./grid_gutter/">grid-gutter</a>: <a href="../../../css_types/scalar">&lt;scalar&gt;</a> [<a href="../../../css_types/scalar">&lt;scalar&gt;</a>];

<a href="./grid_rows/">grid-rows</a>: <a href="../../../css_types/scalar">&lt;scalar&gt;</a>+;

<a href="./grid_size/">grid-size</a>: <a href="../../../css_types/integer">&lt;integer&gt;</a> [<a href="../../../css_types/integer">&lt;integer&gt;</a>];

<a href="./row_span/">row-span</a>: <a href="../../../css_types/integer">&lt;integer&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

Visit each style's reference page to learn more about how the values are used.

## Example

The example below shows all the styles above in action.
The `grid-size: 3 4;` declaration sets the grid to 3 columns and 4 rows.
The first cell of the grid, tinted magenta, shows a cell spanning multiple rows and columns.
The spacing between grid cells is defined by the `grid-gutter` style.

=== "Output"

    ```{.textual path="docs/examples/styles/grid.py"}
    ```

=== "grid.py"

    ```python
    --8<-- "docs/examples/styles/grid.py"
    ```

=== "grid.tcss"

    ```css
    --8<-- "docs/examples/styles/grid.tcss"
    ```

!!! warning

    The styles listed on this page will only work when the layout is `grid`.

## See also

 - The [grid layout](../../guide/layout.md#grid) guide.
