# Text-justify

The `text-justify` rule justifies text within a widget.

This property is not the same as the `text-justify` property in browser CSS.

## Syntax

```
text-justify: [left|center|right|full];
```

### Values

| Value    | Description                         |
|----------|-------------------------------------|
| `left`   | Left justifies text in the widget   |
| `center` | Center justifies text in the widget |
| `right`  | Right justifies text in the widget  |
| `full`   | Fully justifies text in the widget  |

## Example

This example shows, from top to bottom: `left`, `center`, `right`, and `full` justified text.

=== "text_justify.py"

    ```python
    --8<-- "docs/examples/styles/text_justify.py"
    ```

=== "text_justify.css"

    ```css
    --8<-- "docs/examples/styles/text_justify.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/text_justify.py"}
    ```

## CSS

```sass
/* Set text in all Widgets to be right justified */
Widget {
    text-justify: right;
}
```

## Python

```python
# Set text in the widget to be right justified
widget.styles.text_justify = "right"
```
