# Column-span

The `column-span` style specifies how many rows a widget will span in a grid layout.

## Syntax

```sass
column-span: <INTEGER>
```

## Example

The example below shows a 4 by 4 grid where many placeholders span over several columns.

=== "Output"

    ```{.textual path="docs/examples/styles/column_span.py"}
    ```

=== "column_span.py"

    ```py
    --8<-- "docs/examples/styles/column_span.py"
    ```

=== "column_span.css"

    ```css
    --8<-- "docs/examples/styles/column_span.css"
    ```

## CSS

```sass
column-span: 3
```

## Python

```py
widget.styles.column_span = 3
```
