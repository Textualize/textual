# Row-span

The `row-span` style specifies how many rows a widget will span in a grid layout.

!!! note

    This style only affects widgets that are direct children of a widget with `layout: grid`.

## Syntax

```sass
row-span: <INTEGER>
```

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

    ```css
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
