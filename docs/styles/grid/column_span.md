# Column-span

The `column-span` style specifies how many columns a widget will span in a grid layout.

!!! note

    This style only affects widgets that are direct children of a widget with `layout: grid`.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
column-span: <a href="../../../css_types/integer">&lt;integer&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `column-span` style accepts a single non-negative [`<integer>`](../../css_types/integer.md) that quantifies how many columns the given widget spans.

## Example

The example below shows a 4 by 4 grid where many placeholders span over several columns.

=== "Output"

    ```{.textual path="docs/examples/styles/column_span.py"}
    ```

=== "column_span.py"

    ```py
    --8<-- "docs/examples/styles/column_span.py"
    ```

=== "column_span.tcss"

    ```css hl_lines="2 5 8 11 14 20"
    --8<-- "docs/examples/styles/column_span.tcss"
    ```

## CSS

```css
column-span: 3;
```

## Python

```py
widget.styles.column_span = 3
```

## See also

 - [`row-span`](./row_span.md) to specify how many rows a widget spans.
