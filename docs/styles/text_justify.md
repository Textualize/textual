# Text-justify

The `text-justify` rule justifies text within a widget.

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

In this example, we can see, from top to bottom,
 `left`, `center`, `right`, and `full` justified text respectively.

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
