# Width

The `width` style sets a widget's width. By default, it sets the width of the content area, but if `box-sizing` is set to `border-box` it sets the width of the border area.

## Example

=== "width.py"

    ```python
    --8<-- "docs/examples/styles/width.py"
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
