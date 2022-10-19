# Layout

The `layout` property defines how a widget arranges its children.

See [layout](../guide/layout.md) guide for more information.

## Syntax

```
layout: [grid|horizontal|vertical];
```

### Values

| Value                | Description                                                                   |
| -------------------- | ----------------------------------------------------------------------------- |
| `grid`               | Child widgets will be arranged in a grid.                                     |
| `horizontal`         | Child widgets will be arranged along the horizontal axis, from left to right. |
| `vertical` (default) | Child widgets will be arranged along the vertical axis, from top to bottom.   |

## Example

Note how the `layout` property affects the arrangement of widgets in the example below.

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
widget.layout = "horizontal"
```
