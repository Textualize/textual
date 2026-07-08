# Constrain

The `constrain` style prevents a widget from being scrolled off the edges of the screen.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
constrain: <a href="#values">&lt;constrain&gt;</a> <a href="#values">&lt;constrain&gt;</a>;

constrain-x: <a href="#values">&lt;constrain&gt;</a>;
constrain-y: <a href="#values">&lt;constrain&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The two values for `constrain` set the constrain behavior for the horizontal and vertical axes, respectively.

To constrain a single axis, use `constrain-x` or `constrain-y`.

### Values

| Value               | Description                                                                 |
|----------------------|-------------------------------------------------------------------------------|
| `none` (default)     | No constrain applied.                                                        |
| `inflect`            | If the widget would be cut off, flip it around to the opposite side.         |
| `inside`             | Keep the widget within the visible area of the screen, moving it if required.|

## Example

TODO: add a runnable example (see `docs/examples/styles/offset.py` and `offset.tcss` for the pattern to follow).

## CSS

```css
/* Keep the widget fully on screen along both axes */
constrain: inside;

/* Flip the widget to the opposite side if it would be cut off, on the x axis only */
constrain-x: inflect;

/* Keep the widget on screen along the y axis only */
constrain-y: inside;
```

## Python

```python
# Keep the widget fully on screen along both axes
widget.styles.constrain = ("inside", "inside")

# Flip the widget to the opposite side if it would be cut off, on the x axis only
widget.styles.constrain_x = "inflect"

# Keep the widget on screen along the y axis only
widget.styles.constrain_y = "inside"
```

## See also

 - [`offset`](./offset.md) to move a widget from its default position.
