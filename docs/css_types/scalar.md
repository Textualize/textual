# &lt;scalar&gt;

The `<scalar>` CSS type represents a length.
It can be a [`<number>`](./number.md) and a unit, or the special value `auto`.
It is used to represent lengths, for example in the [`width`](../styles/width.md) and [`height`](../styles/height.md) rules.

!!! warning

    Not to be confused with the [`<number>`](./number.md) or [`<percentage>`](./percentage.md) types.

## Syntax

A [`<scalar>`](./scalar.md) can be any of the following:

 - a fixed number of cells (e.g., `10`);
 - a fractional proportion relative to the sizes of the other widgets (e.g., `1fr`);
 - a percentage relative to the container widget (e.g., `50%`);
 - a percentage relative to the container width/height (e.g., `25w`/`75h`);
 - a percentage relative to the viewport width/height (e.g., `25vw`/`75vh`); or
 - the special value `auto` to compute the optimal size to fit without scrolling.

A complete reference table and detailed explanations follow.
You can [skip to the examples](#examples).

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

The unit fraction is used to represent proportional sizes.

For example, if two widgets are side by side and one has `width: 1fr` and the other has `width: 3fr`, the second one will be three times as wide as the first one.

### Percent

The percent unit matches a [`<percentage>`](./percentage.md) and is used to specify a total length relative to the space made available by the container widget.

If used to specify a horizontal length, it will be relative to the width of the container.
For example, `width: 50%` sets the width of a widget to 50% of the width of its container.

If used to specify a vertical length, it will be relative to the height of the container.
For example, `height: 50%` sets the height of a widget to 50% of the height of its container.

### Width

The width unit is similar to the percent unit, except it sets the percentage to be relative to the width of the container.

For example, `width: 25w` sets the width of a widget to 25% of the width of its container and `height: 25w` sets the height of a widget to 25% of the width of its container.
So, if the container has a width of 100 cells, the width and the height of the child widget will be of 25 cells.

### Height

The height unit is similar to the percent unit, except it sets the percentage to be relative to the height of the container.

For example, `height: 75h` sets the height of a widget to 75% of the height of its container and `width: 75h` sets the width of a widget to 75% of the height of its container.
So, if the container has a height of 100 cells, the width and the height of the child widget will be of 75 cells.

### Viewport width

This is the same as the [width unit](#width), except that it is relative to the width of the viewport instead of the width of the immediate container.
The width of the viewport is the width of the terminal minus the widths of widgets that are docked left or right.

For example, `width: 25vw` will try to set the width of a widget to be 25% of the viewport width, regardless of the widths of its containers.

### Viewport height

This is the same as the [height unit](#height), except that it is relative to the height of the viewport instead of the height of the immediate container.
The height of the viewport is the height of the terminal minus the heights of widgets that are docked top or bottom.

For example, `height: 75vh` will try to set the height of a widget to be 75% of the viewport height, regardless of the height of its containers.

### Auto

This special value will try to calculate the optimal size to fit the contents of the widget without scrolling.

For example, if its container is big enough, a label with `width: auto` will be just as wide as its text.

## Examples

### CSS

```css
Horizontal {
    width: 60;     /* 60 cells */
    height: 1fr;   /* proportional size of 1 */
}
```

### Python

```py
widget.styles.width = 16       # Cell unit can be specified with an int/float
widget.styles.height = "1fr"   # proportional size of 1
```
