# Row-span

The `row-span` style specifies how many rows a widget will span in a grid layout.

!!! note

    This style only affects widgets that are direct children of a widget with `layout: grid`.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
row-span: <a href="../../css_types/integer">&lt;integer&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `row-span` style accepts a single non-negative [`<integer>`](../../../css_types/integer) that quantifies how many rows the given widget spans.

## Example

The example below shows a 4 by 4 grid where many placeholders span over several rows.

Notice that grid cells are filled from left to right, top to bottom.
After placing the placeholders `#p1`, `#p2`, `#p3`, and `#p4`, the next available cell is in the second row, fourth column, which is where the top of `#p5` is.

=== "Output"

    ```{.textual path="docs/examples/styles/row_span.py"}
    ```

=== "row_span.py"

    ```py
    --8<-- "docs/examples/styles/row_span.py"
    ```

=== "row_span.css"

    ```sass hl_lines="2 5 8 11 14 17 20"
    --8<-- "docs/examples/styles/row_span.css"
    ```

## CSS

```sass
row-span: 3
```

## Python

```py
widget.styles.row_span = 3
```

## See also

 - [`column-span`](./column_span.md) to specify how many columns a widget spans.
