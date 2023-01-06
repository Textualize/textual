# &lt;overflow&gt;

The `<overflow>` CSS type represents overflow modes.

## Syntax

The [`<overflow>`](/css_types/overflow) type can take any of the following values:

| Value    | Description                            |
|----------|----------------------------------------|
| `auto`   | Determine overflow mode automatically. |
| `hidden` | Don't overflow.                        |
| `scroll` | Allow overflowing.                     |

## Examples

### CSS

```sass
* {
    rule: auto;    /* Determine overflow mode automatically. */
    rule: hidden;  /* Don't overflow. */
    rule: scroll;  /* Allow overflowing. */
}
```

### Python

```py
overflow = "auto"    # Determine overflow mode automatically.
overflow = "hidden"  # Don't overflow.
overflow = "scroll"  # Allow overflowing.
```
