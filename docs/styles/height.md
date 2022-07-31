# Height

The `height` style sets a widget's height. By default, it sets the height of the content area, but if `box-sizing` is set to `border-box` it sets the height of the border area.

## Example

=== "width.py"

    ```python
    --8<-- "docs/examples/styles/height.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/height.py"}
    ```

## CSS

```sass
/* Explicit cell height */
height: 10;

/* Percentage height */
height: 50%;

/* Automatic height */
width: auto
```

## Python

```python
self.styles.height = 10
self.styles.height = "50%
self.styles.height = "auto"
```
