# Layout

The `layout` property defines how a widget arranges its children.

## Syntax

```
layout: [vertical|horizontal|center];
```

### Values

| Value                | Description                                                                   |
|----------------------|-------------------------------------------------------------------------------|
| `vertical` (default) | Child widgets will be arranged along the vertical axis, from top to bottom.   |
| `horizontal`         | Child widgets will be arranged along the horizontal axis, from left to right. |
| `center`             | A single child widget will be placed in the center.                           |

## Example

Note how the `layout` property affects the arrangement of widgets in the example below.

=== "layout.py"

    ```python
    --8<-- "docs/examples/styles/layout.py"
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
