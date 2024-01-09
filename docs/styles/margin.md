# Margin

The `margin` style specifies spacing around a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
margin: <a href="../../css_types/integer">&lt;integer&gt;</a>
      # one value for all edges
      | <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a>
      # top/bot   left/right
      | <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a>;
      # top       right     bot       left

margin-top: <a href="../../css_types/integer">&lt;integer&gt;</a>;
margin-right: <a href="../../css_types/integer">&lt;integer&gt;</a>;
margin-bottom: <a href="../../css_types/integer">&lt;integer&gt;</a>;
margin-left: <a href="../../css_types/integer">&lt;integer&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `margin` specifies spacing around the four edges of the widget equal to the [`<integer>`](../css_types/integer.md) specified.
The number of values given defines what edges get what margin:

 - 1 [`<integer>`](../css_types/integer.md) sets the same margin for the four edges of the widget;
 - 2 [`<integer>`](../css_types/integer.md) set margin for top/bottom and left/right edges, respectively.
 - 4 [`<integer>`](../css_types/integer.md) set margin for the top, right, bottom, and left edges, respectively.

!!! tip

    To remember the order of the edges affected by the rule `margin` when it has 4 values, think of a clock.
    Its hand starts at the top and the goes clockwise: top, right, bottom, left.

Alternatively, margin can be set for each edge individually through the styles `margin-top`, `margin-right`, `margin-bottom`, and `margin-left`, respectively.

## Examples

### Basic usage

In the example below we add a large margin to a label, which makes it move away from the top-left corner of the screen.

=== "Output"

    ```{.textual path="docs/examples/styles/margin.py"}
    ```

=== "margin.py"

    ```python
    --8<-- "docs/examples/styles/margin.py"
    ```

=== "margin.tcss"

    ```css hl_lines="7"
    --8<-- "docs/examples/styles/margin.tcss"
    ```

### All margin settings

The next example shows a grid.
In each cell, we have a placeholder that has its margins set in different ways.

=== "Output"

    ```{.textual path="docs/examples/styles/margin_all.py"}
    ```

=== "margin_all.py"

    ```py
    --8<-- "docs/examples/styles/margin_all.py"
    ```

=== "margin_all.tcss"

    ```css hl_lines="25 29 33 37 41 45 49 53"
    --8<-- "docs/examples/styles/margin_all.tcss"
    ```

## CSS

```css
/* Set margin of 1 around all edges */
margin: 1;
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

Python does not provide the properties `margin-top`, `margin-right`, `margin-bottom`, and `margin-left`.
However, you _can_ set the margin to a single integer, a tuple of 2 integers, or a tuple of 4 integers:

```python
# Set margin of 1 around all edges
widget.styles.margin = 1
# Set margin of 2 on the top and bottom edges, and 4 on the left and right
widget.styles.margin = (2, 4)
# Set margin of 1 on top, 2 on the right, 3 on the bottom, and 4 on the left
widget.styles.margin = (1, 2, 3, 4)
```

## See also

 - [`padding`](./padding.md) to add spacing around the content of a widget.
