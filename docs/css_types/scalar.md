# Scalar

A scalar unit is a numeric value with a unit, e.g., `50vh`.
Scalars are used with styles that specify lengths, like `width` and `height`.

Scalars also accept the special value `auto`.

## Syntax

--8<-- "docs/snippets/scalar_syntax.md"

A complete reference table and detailed explanations follow.
You can [skip to the examples](#Examples).

| Unit symbol | Unit            | Example | Description                                                 |
|-------------|-----------------|---------|-------------------------------------------------------------|
| `""`        | Cell            | `10`    | Number of cells (rows or columns).                          |
| `"fr"`      | Fraction        | `1fr`   | Specifies the proportion of space the widget should occupy. |
| `"%"`       | Percent         | `75%`   | Length relative to the container widget.                    |
| `"w"`       | Width           | `25w`   | Percentage relative to the width of the container widget.   |
| `"h"`       | Height          | `75h`   | Percentage relative to the height of the container widget.  |
| `"vw"`      | Viewport width  | `25vw`  | Percentage relative to the viewport width.                  |
| `"vh"`      | Viewport height | `75vh`  | Percentage relative to the viewport height.                 |
| -           | Auto            | `auto`  | Tries to compute the optimal size to fit without scrolling. |

### Cell

The number of cells is the only unit for a scalar that is _absolute_.
This can be an integer or a float but floats are truncated to integers.

If used to specify a horizontal length, it corresponds to the number of columns.
For example, in `width: 15`, this sets the width of a widget to be equal to 15 cells, which translates to 15 columns.

If used to specify a vertical length, it corresponds to the number of lines.
For example, in `height: 10`, this sets the height of a widget to be equal to 10 cells, which translates to 10 lines.

### Fraction

The fraction scalar is used to represent proportional sizes.

For example, if two widgets are side by side and one has `width: 1fr` and the other has `width: 3fr`, the second one will be three times as wide as the first one.

### Percent

The percent scalar is used to specify a total length relative to the space made available by the container widget.

If used to specify a horizontal length, it will be relative to the width of the container.
For example, `width: 50%` sets the width of a widget to 50% of the width of its container.

If used to specify a vertical length, it will be relative to the height of the container.
For example, `height: 50%` sets the height of a widget to 50% of the height of its container.

### Width

The width scalar is similar to the percent scalar, except it sets the percentage to be relative to the width of the container.

For example, `width: 25w` sets the width of a widget to 25% of the width of its container and `height: 25w` sets the height of a widget to 25% of the width of its container.
So, if the container has a width of 100 cells, the width and the height of the child widget will be of 25 cells.

### Height

The height scalar is similar to the percent scalar, except it sets the percentage to be relative to the height of the container.

For example, `height: 75h` sets the height of a widget to 75% of the height of its container and `width: 75h` sets the width of a widget to 75% of the height of its container.
So, if the container has a height of 100 cells, the width and the height of the child widget will be of 75 cells.

### Viewport width

This is the same as the [width scalar](#Width), except that it is relative to the width of the viewport instead of the width of the immediate container.

For example, `width: 25vw` will try to set the width of a widget to be 25% of the viewport width, regardless of the widths of its containers.

### Viewport height

This is the same as the [height scalar](#Height), except that it is relative to the height of the viewport instead of the height of the immediate container.

For example, `height: 75vh` will try to set the height of a widget to be 75% of the viewport height, regardless of the height of its containers.

### Auto

This special value will try to calculate the optimal size to fit the contents of the widget without scrolling.

For example, if its container is big enough, a label with `width: auto` will be just as wide as its text.

## Examples

```css
Widget {
    width: 16;
    width: 1fr;
    width: 50%;
    width: 25w;
    width: 75h;
    width: 25vw;
    width: 75vh;
    width: auto;
}
```

```py
widget.styles.width = 16  # Cell scalar can be an int or a float
widget.styles.width = "1fr"
widget.styles.width = "50%"
widget.styles.width = "25w"
widget.styles.width = "75h"
widget.styles.width = "25vw"
widget.styles.width = "75vh"
widget.styles.width = "auto"
```
