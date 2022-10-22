# Text-style

The `text-style` rule enables a number of different ways of displaying text.

Text styles may be set in combination.
For example `bold underline` or `reverse underline strike`.

## Syntax

```
text-style: <TEXT STYLE> ...;
```

### Values

| Value       | Description                                                    |
|-------------|----------------------------------------------------------------|
| `bold`      | **bold text**                                                  |
| `italic`    | _italic text_                                                  |
| `reverse`   | reverse video text (foreground and background colors reversed) |
| `underline` | <u>underline text</u>                                          |
| `strike`    | <s>strikethrough text</s>                                      |

## Example

Each of the three text panels has a different text style.

=== "text_style.py"

    ```python
    --8<-- "docs/examples/styles/text_style.py"
    ```

=== "text_style.css"

    ```css
    --8<-- "docs/examples/styles/text_style.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/text_style.py"}
    ```

## CSS

```sass
text-style: italic;
```

## Python

```python
widget.styles.text_style = "italic"
```
