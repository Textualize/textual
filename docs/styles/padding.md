# Padding

The padding rule adds space around the content of a widget. You can specify padding with 1, 2 or 4 numbers.

- `1` Sets a padding of 1 around all 4 edges
- `1 2` Sets a padding of 1 on the top and bottom edges, and a padding of two on the left and right edges
- `1 2 3 4` Sets a padding of one on the top edge, 2 on the right, 3 on the bottom, and 4 on the left.

## Example

=== "padding.py"

    ```python
    --8<-- "docs/examples/styles/padding.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/padding.py"}
    ```

## CSS

```sass
/* Set padding of 2 on the top and bottom edges, and 4 on the left and right */
padding: 2 4;
```

## Python

```python
# In Python you can set the padding as a tuple of integers
widget.styles.padding = (2, 3)
```
