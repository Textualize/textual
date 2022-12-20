# Layout

The `layout` property defines how a widget arranges its children.

See the [layout](../guide/layout.md) guide for more information.

## Syntax

```
layout: grid | horizontal | vertical;
```

### Values

| Value                | Description                                                                   |
| -------------------- | ----------------------------------------------------------------------------- |
| `grid`               | Child widgets will be arranged in a grid.                                     |
| `horizontal`         | Child widgets will be arranged along the horizontal axis, from left to right. |
| `vertical` (default) | Child widgets will be arranged along the vertical axis, from top to bottom.   |

## Example

Note how the `layout` property affects the arrangement of widgets in the example below.
To learn more about the grid layout, you can see the [layout guide](../guide/layout.md) or the [grid reference](../grid).

=== "layout.py"

    ```python
    --8<-- "docs/examples/styles/layout.py"
    ```

=== "layout.css"

    ```sass
    --8<-- "docs/examples/styles/layout.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/layout.py"}
    ```

## CSS

```sass
layout: horizontal;
```

## Python

```python
widget.styles.layout = "horizontal"
```
