# &lt;name&gt;

The `<name>` type represents a sequence of characters that identifies something.

## Syntax

--8<-- "docs/snippets/type_syntax/name.md"

## Examples

### CSS

```sass
* {
    rule: onlyLetters;
    rule: Letters-and-hiphens;
    rule: _leading-underscore;
    rule: letters-and-1-digit;
    rule: name1234567890;
}
```

### Python

<!-- Same examples as above. -->

```py
name = "onlyLetters"
name = "Letters-and-hiphens"
name = "_leading-underscore"
name = "letters-and-1-digit"
name = "name1234567890"
```
