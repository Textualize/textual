# &lt;integer&gt;

The `<integer>` CSS type represents an integer number.

## Syntax

An [`<integer>`](./integer.md) is any valid integer number like `-10` or `42`.

!!! note

    Some CSS rules may expect an `<integer>` within certain bounds. If that is the case, it will be noted in that rule.

## Examples

### CSS

```css
.classname {
    offset: 10 -20
}
```

### Python

In Python, a rule that expects a CSS type `<integer>` will expect a value of the type `int`:

```py
widget.styles.offset = (10, -20)
```
