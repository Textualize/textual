# &lt;text-overflow&gt;

The `<text-overflow>` CSS type sets how Textual wraps text.

## Syntax

The [`<text-overflow>`](./text_overflow.md) type can take any of the following values:

| Value      | Description                                                                         |
| ---------- | ----------------------------------------------------------------------------------- |
| `clip`     | Overflowing text will be clipped (the overflow portion is removed from the output). |
| `fold`     | Overflowing text will fold on to the next line.                                     |
| `ellipsis` | Overflowing text will be truncate and the last character replaced with an ellipsis. |


## Examples

### CSS

```css
#widget {
    text-overflow: ellipsis;  /* Disable wrapping */
}
```

### Python

```py
widget.styles.text_overflow = "ellipsis"  # Disable wrapping
```


## See also

 - [`text-wrap`](./text_wrap.md) to enable or disable text wrapping.
