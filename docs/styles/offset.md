# Offset

The `offset` rule adds an offset to the widget's position.

## Example

In this example, we have 3 widgets with differing offsets.

=== "offset.py"

    ```python
    --8<-- "docs/examples/styles/offset.py"
    ```

=== "offset.css"

    ```css
    --8<-- "docs/examples/styles/offset.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/offset.py"}
    ```

## CSS

```sass
/* Move the widget 2 cells in the x direction, and 4 in the y direction. */
offset: 2 4;
```

## Python

```python
# Move the widget 2 cells in the x direction, and 4 in the y direction.
widget.styles.offset = (2, 4)
```
