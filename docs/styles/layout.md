# Layout

The `layout` style defines how a widget arranges its children.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
layout: grid | horizontal | vertical;
--8<-- "docs/snippets/syntax_block_end.md"

The `layout` style takes an option that defines how child widgets will be arranged, as per the table shown below.

### Values

| Value                | Description                                                                   |
| -------------------- | ----------------------------------------------------------------------------- |
| `grid`               | Child widgets will be arranged in a grid.                                     |
| `horizontal`         | Child widgets will be arranged along the horizontal axis, from left to right. |
| `vertical` (default) | Child widgets will be arranged along the vertical axis, from top to bottom.   |

See the [layout](../guide/layout.md) guide for more information.

## Example

Note how the `layout` style affects the arrangement of widgets in the example below.
To learn more about the grid layout, you can see the [layout guide](../guide/layout.md) or the [grid reference](./grid/index.md).

=== "Output"

    ```{.textual path="docs/examples/styles/layout.py"}
    ```

=== "layout.py"

    ```python
    --8<-- "docs/examples/styles/layout.py"
    ```

=== "layout.tcss"

    ```css hl_lines="2 8"
    --8<-- "docs/examples/styles/layout.tcss"
    ```

## CSS

```css
layout: horizontal;
```

## Python

```python
widget.styles.layout = "horizontal"
```

## See also

 - [Layout guide](../guide/layout.md).
 - [Grid reference](./grid/index.md).
