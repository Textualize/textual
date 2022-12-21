# &lt;percentage&gt;

The `<percentage>` CSS type represents a percentage value.
It is often used to represent values that are relative to the parent's values.

!!! warning

    Not to be confused with the [`<scalar>`](./scalar.md) type.

## Syntax

--8<-- "docs/snippets/type_syntax/percentage.md"
Some rules may clamp the values between `0%` and `100%`.

## Examples

### CSS

```sass
* {
    rule: 70%;    /* Integer followed by % */
    rule: -3.5%;  /* The number can be negative/decimal */
}
```

### Python

```py
percentage = "70%"
```
