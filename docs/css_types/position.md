# &lt;position&gt;

The `<position>` CSS type defines how the the `offset` rule is applied..


## Syntax

A [`<position>`](./position.md) may be any of the following values:

| Value      | Alignment type                                               |
| ---------- | ------------------------------------------------------------ |
| `relative` | Offset is applied to widgets default position.               |
| `absolute` | Offset is applied to the origin (top left) of its container. |

## Examples

### CSS

```css
Label {
    position: absolute;
    offset: 10 5;
}
```

### Python

```py
widget.styles.position = "absolute"
widget.styles.offset = (10, 5)
```
