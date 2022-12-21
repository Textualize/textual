# &lt;integer&gt;

The `<integer>` CSS type represents an integer number.

## Syntax

--8<-- "docs/snippets/type_syntax/integer.md"

!!! note

    Some CSS rules may expect an `<integer>` within certain bounds. If that is the case, it will be noted in that rule.

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
