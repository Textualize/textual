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

In the following example we show the output of each of the values of `text_overflow`.

The widgets all have [text wrapping][`text-wrap`](./text_wrap.md) disabled.
Since the string is longer than the width, it will overflow.

In the first (top) widget, "text-overflow" is set to "clip" which clips any text that is overflowing, resulting in a single line.

In the second widget, "text-overflow" is set to "fold", which causes the overflowing text to *fold* on to the next line.
When text folds like this, it won't respect word boundaries--so you may get words broken across lines.

In the third widget, "text-overflow" is set to "ellipsis", which is similar to "clip", but with the last character set to an ellipsis.
This option is useful to indicate to the user that there may be more text.

=== "Output"

    ```{.textual path="docs/examples/styles/text_overflow.py"}
    ```

=== "text_overflow.py"

    ```py
    --8<-- "docs/examples/styles/text_overflow.py"
    ```

=== "text_overflow.tcss"

    ```css
    --8<-- "docs/examples/styles/text_overflow.tcss"
    ```


### CSS

```css
#widget {
    text-overflow: ellipsis; 
}
```

### Python

```py
widget.styles.text_overflow = "ellipsis" 
```


## See also

 - [`text-wrap`](./text_wrap.md) is used to control wrapping.
