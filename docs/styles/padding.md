# Padding

The padding rule adds space around the content of a widget. You can specify padding with 1, 2 or 4 numbers.

| example             |                                                                     |
| ------------------- | ------------------------------------------------------------------- |
| `padding: 1;`       | A single value sets a padding of 1 around all 4 edges               |
| `padding: 1 2;`     | Two values sets the padding for the top/bottom and left/right edges |
| `padding: 1 2 3 4;` | Four values sets top, right, bottom, and left padding independently |

Padding may also be set individually by setting `padding-top`, `padding-right`, `padding-bottom`, or `padding-left` to a single value.

## Syntax

```
padding: <INTEGER>;
padding: <INTEGER> <INTEGER>;
padding: <INTEGER> <INTEGER> <INTEGER> <INTEGER>;
```

## Example

This example adds padding around static text.

=== "padding.py"

    ```python
    --8<-- "docs/examples/styles/padding.py"
    ```

=== "padding.css"

    ```css
    --8<-- "docs/examples/styles/padding.css"
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
