# Padding

The `padding` style specifies spacing around the content of a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
padding: <a href="../../css_types/integer">&lt;integer&gt;</a> # one value for all edges
       | <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a>
       # top/bot   left/right
       | <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a>;
       # top       right     bot       left

padding-top: <a href="../../css_types/integer">&lt;integer&gt;</a>;
padding-right: <a href="../../css_types/integer">&lt;integer&gt;</a>;
padding-bottom: <a href="../../css_types/integer">&lt;integer&gt;</a>;
padding-left: <a href="../../css_types/integer">&lt;integer&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `padding` specifies spacing around the _content_ of a widget, thus this spacing is added _inside_ the widget.
The values of the [`<integer>`](../../css_types/integer) determine how much spacing is added and the number of values define what edges get what padding:

 - 1 [`<integer>`](../../css_types/integer) sets the same padding for the four edges of the widget;
 - 2 [`<integer>`](../../css_types/integer) set padding for top/bottom and left/right edges, respectively.
 - 4 [`<integer>`](../../css_types/integer) set padding for the top, right, bottom, and left edges, respectively.

!!! tip

    To remember the order of the edges affected by the rule `padding` when it has 4 values, think of a clock.
    Its hand starts at the top and then goes clockwise: top, right, bottom, left.

Alternatively, padding can be set for each edge individually through the rules `padding-top`, `padding-right`, `padding-bottom`, and `padding-left`, respectively.

## Example

### Basic usage

This example adds padding around some text.

=== "Output"

    ```{.textual path="docs/examples/styles/padding.py"}
    ```

=== "padding.py"

    ```python
    --8<-- "docs/examples/styles/padding.py"
    ```

=== "padding.css"

    ```sass hl_lines="7"
    --8<-- "docs/examples/styles/padding.css"
    ```

### All padding settings

The next example shows a grid.
In each cell, we have a placeholder that has its padding set in different ways.
The effect of each padding setting is noticeable in the colored background around the text of each placeholder.

=== "Output"

    ```{.textual path="docs/examples/styles/padding_all.py"}
    ```

=== "padding_all.py"

    ```py
    --8<-- "docs/examples/styles/padding_all.py"
    ```

=== "padding_all.css"

    ```sass hl_lines="16 20 24 28 32 36 40 44"
    --8<-- "docs/examples/styles/padding_all.css"
    ```

## CSS

```sass
/* Set padding of 1 around all edges */
padding: 1;
/* Set padding of 2 on the top and bottom edges, and 4 on the left and right */
padding: 2 4;
/* Set padding of 1 on the top, 2 on the right,
                 3 on the bottom, and 4 on the left */
padding: 1 2 3 4;

padding-top: 1;
padding-right: 2;
padding-bottom: 3;
padding-left: 4;
```

## Python

In Python, you cannot set any of the individual `padding` styles `padding-top`, `padding-right`, `padding-bottom`, and `padding-left`.

However, you _can_ set padding to a single integer, a tuple of 2 integers, or a tuple of 4 integers:

```python
# Set padding of 1 around all edges
widget.styles.padding = 1
# Set padding of 2 on the top and bottom edges, and 4 on the left and right
widget.styles.padding = (2, 4)
# Set padding of 1 on top, 2 on the right, 3 on the bottom, and 4 on the left
widget.styles.padding = (1, 2, 3, 4)
```

## See also

 - [`box-sizing`](./box_sizing.md) to specify how to account for padding in a widget's dimensions.
 - [`padding`](./margin.md) to add spacing around a widget.
