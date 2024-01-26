# &lt;text-align&gt;

The `<text-align>` CSS type represents alignments that can be applied to text.

!!! warning

    Not to be confused with the [`text-align`](../styles/text_align.md) CSS rule that sets the alignment of text in a widget.

## Syntax

A [`<text-align>`](./text_align.md) can be any of the following values:

| Value     | Alignment type                       |
|-----------|--------------------------------------|
| `center`  | Center alignment.                    |
| `end`     | Alias for `right`.                   |
| `justify` | Text is justified inside the widget. |
| `left`    | Left alignment.                      |
| `right`   | Right alignment.                     |
| `start`   | Alias for `left`.                    |

!!! tip

    The meanings of `start` and `end` will likely change when RTL languages become supported by Textual.

## Examples

### CSS

```css
Label {
    text-align: justify;
}
```

### Python

```py
widget.styles.text_align = "justify"
```
