# &lt;name&gt;

The `<name>` type represents a sequence of characters that identifies something.

## Syntax

A [`<name>`](./name.md) is any non-empty sequence of characters:

 - starting with a letter `a-z`, `A-Z`, or underscore `_`; and
 - followed by zero or more letters `a-zA-Z`, digits `0-9`, underscores `_`, and hiphens `-`.

## Examples

### CSS

```css
Screen {
    layers: onlyLetters Letters-and-hiphens _lead-under letters-1-digit;
}
```

### Python

```py
widget.styles.layers = "onlyLetters Letters-and-hiphens _lead-under letters-1-digit"
```
