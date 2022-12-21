# Margin

The `margin` rule adds space around the entire widget. Margin may be specified with 1, 2 or 4 values.

| Example            | Description                                                          |
|--------------------|----------------------------------------------------------------------|
| `margin: 1;`       | A single value sets the margin around all 4 edges.                   |
| `margin: 1 2;`     | Two values sets the margin for the top/bottom and left/right edges.  |
| `margin: 1 2 3 4;` | Four values sets top, right, bottom, and left margins independently. |

Margin may also be set individually by setting `margin-top`, `margin-right`, `margin-bottom`, or `margin-left` to a single value.

## Syntax

```
margin: <INTEGER>;  /* Same value for the 4 edges. */
margin: <INTEGER> <INTEGER>;
/*       top/bot, left/right */
margin: <INTEGER> <INTEGER> <INTEGER> <INTEGER>;
/*           top,    right,   bottom,     left */

margin-top: <INTEGER>;
margin-right: <INTEGER>;
margin-bottom: <INTEGER>;
margin-left: <INTEGER>;
```

## Examples

In the example below we add a large margin to a label, which makes it move away from the top-left corner of the screen.

=== "Output"

    ```{.textual path="docs/examples/styles/margin.py"}
    ```

=== "margin.py"

    ```python
    --8<-- "docs/examples/styles/margin.py"
    ```

=== "margin.css"

    ```css
    --8<-- "docs/examples/styles/margin.css"
    ```

The next example shows a grid.
In each cell, we have a placeholder that has its margins set in different ways.

=== "Output"

    ```{.textual path="docs/examples/styles/margin_all.py"}
    ```

=== "margin_all.py"

    ```py
    --8<-- "docs/examples/styles/margin_all.py"
    ```

=== "margin_all.css"

    ```py
    --8<-- "docs/examples/styles/margin_all.css"
    ```

## CSS

```sass
/* Set margin of 1 around all edges */
margin: 1
/* Set margin of 2 on the top and bottom edges, and 4 on the left and right */
margin: 2 4;
/* Set margin of 1 on the top, 2 on the right,
                 3 on the bottom, and 4 on the left */
margin: 1 2 3 4;

margin-top: 1;
margin-right: 2;
margin-bottom: 3;
margin-left: 4;
```

## Python

In Python, you cannot set any of the individual `margin` rules `margin-top`, `margin-right`, `margin-bottom`, and `margin-left`.

However, you _can_ set margin to a single integer, a tuple of 2 integers, or a tuple of 4 integers:

```python
# Set margin of 1 around all edges
widget.styles.margin = 1
# Set margin of 2 on the top and bottom edges, and 4 on the left and right
widget.styles.margin = (2, 4)
# Set margin of 1 on top, 2 on the right, 3 on the bottom, and 4 on the left
widget.styles.margin = (1, 2, 3, 4)
```
