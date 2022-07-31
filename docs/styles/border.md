# Border

The `border` rule enables the drawing of a box around a widget. A border is set with a border style (see below) followed by a color.

- `"ascii"`
- `"round"`
- `"solid"`
- `"double"`
- `"dashed"`
- `"heavy"`
- `"inner"`
- `"outer"`
- `"hkey"`
- `"vkey"`
- `"tall"`
- `"wide"`

For examples `heavy white` would display a heavy white line around a widget.

Borders may also be set individually with the `border-top`, `border-right`, `border-bottom` and `border-left` rules.

## Example

This examples shows three widgets with different border styles.

=== "border.py"

    ```python
    --8<-- "docs/examples/styles/border.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/border.py"}
    ```

## CSS

```sass
/* Set a heavy white border */
border: heavy white;

/* set a red border on the left */
border-left: outer red;
```

## Python

```python
# Set a heavy white border
widget.border = ("heavy", "white)

# Set a red border on the left
widget.border_left = ("outer", "red)
```
