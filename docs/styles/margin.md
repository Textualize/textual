# Margin

The `margin` rule adds space around the entire widget.

- `margin: 1;` Sets a margin of 1 around all 4 edges
- `margin: 1 2;` Sets a margin of 1 on the top and bottom edges, and a margin of 2 on the left and right edges
- `margin: 1 2 3 4;` Sets a margin of one on the top edge, 2 on the right, 3 on the bottom, and 4 on the left.

Margin may also be set individually, following the same pattern as above, by setting `margin-top`, `margin-right`, `margin-bottom`, or `margin-left`.

## Example

=== "margin.py"

    ```python
    --8<-- "docs/examples/styles/margin.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/margin.py"}
    ```

## CSS

```sass
/* Set margin of 2 on the top and bottom edges, and 4 on the left and right */
margin: 2 4;
```

## Python

```python
# In Python you can set the margin as a tuple of integers
widget.styles.margin = (2, 3)
```
