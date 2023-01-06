# &lt;name&gt;

The `<name>` type represents a sequence of characters that identifies something.

## Syntax

A [`<name>`](/css_types/name) is any non-empty sequence of characters:

 - starting with a letter `a-z`, `A-Z`, or underscore `_`; and
 - followed by zero or more letters `a-zA-Z`, digits `0-9`, underscores `_`, and hiphens `-`.

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
