# &lt;keyline&gt;

The `<keyline>` CSS type represents a line style used in the [keyline](../styles/keyline.md) rule.


## Syntax

| Value    | Description                |
| -------- | -------------------------- |
| `none`   | No line (disable keyline). |
| `thin`   | A thin line.               |
| `heavy`  | A heavy (thicker) line.    |
| `double` | A double line.             |

## Examples

### CSS

```css
Vertical {
    keyline: thin green;
}
```

### Python

```py
# A tuple of <keyline> and color
widget.styles.keyline = ("thin", "green")
```
