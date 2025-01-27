# &lt;text-wrap&gt;

The `<text-wrap>` CSS type sets how Textual wraps text.

## Syntax

The [`<text-wrap>`](./text_wrap.md) type can take any of the following values:

| Value    | Description               |
| -------- | ------------------------- |
| `wrap`   | Word wrap text (default). |
| `nowrap` | Disable text wrapping.    |

## Examples

### CSS

```css
#widget {
    text-wrap: nowrap;  /* Disable wrapping */
}
```

### Python

```py
widget.styles.text_wrap = "nowrap"  # Disable wrapping
```


## See also

 - [`text-overflow`](./overflow.md) is used to change what happens to overflowing text.
