# Text-style

The `text-style` rule enables a number of different ways of displaying text. The value may be set to any of the following:

| Style         | Effect                                                         |
| ------------- | -------------------------------------------------------------- |
| `"bold"`      | **bold text**                                                  |
| `"italic"`    | _italic text_                                                  |
| `"reverse"`   | reverse video text (foreground and background colors reversed) |
| `"underline"` | <u>underline text</u>                                          |
| `"strike"`    | <s>strikethrough text</s>                                      |

Text styles may be set in combination. For example "bold underline" or "reverse underline strike".

## Example

=== "text_style.py"

    ```python
    --8<-- "docs/examples/styles/text_style.py"
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
