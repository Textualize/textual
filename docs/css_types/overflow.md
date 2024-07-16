# &lt;overflow&gt;

The `<overflow>` CSS type represents overflow modes.

## Syntax

The [`<overflow>`](./overflow.md) type can take any of the following values:

| Value    | Description                            |
|----------|----------------------------------------|
| `auto`   | Determine overflow mode automatically. |
| `hidden` | Don't overflow.                        |
| `scroll` | Allow overflowing.                     |

## Examples

### CSS

```css
#container {
    overflow-y: hidden;  /* Don't overflow */
}
```

### Python

```py
widget.styles.overflow_y = "hidden"  # Don't overflow
```
