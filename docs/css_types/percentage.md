# &lt;percentage&gt;

The `<percentage>` CSS type represents a percentage value.
It is often used to represent values that are relative to the parent's values.

!!! warning

    Not to be confused with the [`<scalar>`](./scalar.md) type.

## Syntax

A [`<percentage>`](/css_types/percentage) is a [`<number>`](/css_types/number) followed by the percent sign `%` (without spaces).
Some rules may clamp the values between `0%` and `100%`.

## Examples

### CSS

```sass
#footer {
    /* Integer followed by % */
    color: red 70%;

    /* The number can be negative/decimal, although that may not make sense */
    offset: -30% 12.5%;
}
```

### Python

```py
# Integer followed by %
widget.styles.color = "red 70%"

# The number can be negative/decimal, although that may not make sense
widget.styles.offset = ("-30%", "12.5%")
```
