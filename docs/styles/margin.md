# Margin

The `margin` rule adds space around the entire widget. Margin may be specified with 1, 2 or 4 values.

| example            |                                                                     |
| ------------------ | ------------------------------------------------------------------- |
| `margin: 1;`       | A single value sets a margin of 1 around all 4 edges                |
| `margin: 1 2;`     | Two values sets the margin for the top/bottom and left/right edges  |
| `margin: 1 2 3 4;` | Four values sets top, right, bottom, and left margins independently |

Margin may also be set individually by setting `margin-top`, `margin-right`, `margin-bottom`, or `margin-left` to an single value.

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
