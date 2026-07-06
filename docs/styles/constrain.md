# Constrain

The `constrain` style defines how a widget should be constrained to avoid clipping by the edges of the screen (or container).

## Syntax

```
constrain: <constrain> [<constrain>];

constrain-x: <constrain>;
constrain-y: <constrain>;   
```

`constrain` accepts one or two values. If a single value is provided, it is applied to both axes.
If two values are given, the first is applied to the horizontal axis and the second to the vertical axis.

To constrain a single axis, use `constrain-x` or `constrain-y`.

### Values

| Value               | Description                                                                                      |
|---------------------|----------------------------------------------------------------------------------------------------|
| `none` (default)    | The widget is not constrained.                                                                    |
| `inflect`           | If the widget would be clipped, it is flipped to the opposite side of the origin.                 |
| `inside`            | If the widget would be clipped, it is moved to be entirely within the constraining region.         |

## CSS

```css
/* Constrain both axes so the widget is kept fully on screen */
constrain: inside;

/* Flip the widget to the opposite side if it would otherwise be clipped horizontally */
constrain-x: inflect;

/* Different constrain values per axis */
constrain: inflect inside;
```

## Python

```python
# Constrain both axes
widget.styles.constrain = ("inside", "inside")

# Set a single axis
widget.styles.constrain_x = "inflect"
widget.styles.constrain_y = "inside"
```

## See also

 - [`offset`](./offset.md) to set the position of a widget.