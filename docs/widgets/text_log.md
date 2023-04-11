# TextLog

A TextLog is a widget which displays scrollable content that may be appended to in realtime.

Call [TextLog.write][textual.widgets.TextLog.write] with a string or [Rich Renderable](https://rich.readthedocs.io/en/latest/protocol.html) to write content to the end of the TextLog. Call [TextLog.clear][textual.widgets.TextLog.clear] to clear the content.

- [X] Focusable
- [ ] Container

## Example

The example below shows an application showing a `TextLog` with different kinds of data logged.

=== "Output"

    ```{.textual path="docs/examples/widgets/text_log.py" press="H,i"}
    ```

=== "text_log.py"

    ```python
    --8<-- "docs/examples/widgets/text_log.py"
    ```



## Reactive Attributes

| Name        | Type   | Default | Description                                                  |
| ----------- | ------ | ------- | ------------------------------------------------------------ |
| `highlight` | `bool` | `False` | Automatically highlight content.                             |
| `markup`    | `bool` | `False` | Apply Rich console markup.                                   |
| `max_lines` | `int`  | `None`  | Maximum number of lines in the log or `None` for no maximum. |
| `min_width` | `int`  | 78      | Minimum width of renderables.                                |
| `wrap`      | `bool` | `False` | Enable word wrapping.                                        |

## Messages

This widget sends no messages.


---


::: textual.widgets.TextLog
    options:
      heading_level: 2
