# Width

The `width` rule sets a widget's width. By default, it sets the width of the content area, but if `box-sizing` is set to `border-box` it sets the width of the border area.

## Syntax

```
width: <SCALAR>;
```

## Example

This example adds a widget with 50% width of the screen.

=== "width.py"

    ```python
    --8<-- "docs/examples/styles/width.py"
    ```

=== "width.css"

    ```css
    --8<-- "docs/examples/styles/width.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/width.py"}
    ```

## CSS

```sass
/* Explicit cell width */
width: 10;

/* Percentage width */
width: 50%;

/* Automatic width */
width: auto
```

## Python

```python
self.styles.width = 10
self.styles.width = "50%
self.styles.width = "auto"
```
