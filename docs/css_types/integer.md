# &lt;integer&gt;

The `<integer>` CSS type represents an integer number and can be positive or negative.

!!! note

    Some CSS rules may expect an `<integer>` within certain bounds. If that is the case, it will be noted in that rule.

## Syntax

Any legal integer, like `-10` or `42`.

## Examples

### CSS

```sass
* {
    rule: -5;
    rule: 10;
}
```

### Python

In Python, a rule that expects a CSS type `<integer>` will expect a value of the type `int`:

```py
integer = -5
integer = 10
```
