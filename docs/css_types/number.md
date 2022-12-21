# &lt;number&gt;

The `<number>` CSS type represents a real number, which can be an integer or a number with a decimal part (akin to a `float` in Python).

## Syntax

--8<-- "docs/snippets/type_syntax/number.md"

## Examples

### CSS

```sass
* {
    css-rule: 6       /* Integers are numbers */
    css-rule: -13     /* Numbers can be negative */
    css-rule: 4.75    /* Numbers can have a decimal part */
    css-rule: -73.73
}
```

### Python

In Python, a rule that expects a CSS type `<number>` will accept an `int` or a `float`:

```py
number = 6       # ints are numbers
number = -13     # ints can be negative
number = 4.75    # floats are numbers
number = -73.73  # negative floats too
```
