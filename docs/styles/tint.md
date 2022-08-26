# Tint

The tint rule blends a color with the widget. The color should likely have an _alpha_ component, or the end result would obscure the widget content.

## Syntax

```
tint: <COLOR> [<PERCENTAGE>];
```

## Example

This examples shows a green tint with gradually increasing alpha.

=== "tint.py"

    ```python
    --8<-- "docs/examples/styles/tint.py"
    ```

=== "tint.css"

    ```css
    --8<-- "docs/examples/styles/tint.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/tint.py"}
    ```

## CSS

```sass
/* A red tint (could indicate an error) */
tint: red 20%

/* A green tint */
tint: rgba(0, 200, 0, 0.3);
```

# Python

```python
# A red tint
from textual.color import Color
widget.styles.tint = Color.parse("red").with_alpha(0.2);

# A green tint
widget.styles.tint = "rgba(0, 200, 0, 0.3):
```
