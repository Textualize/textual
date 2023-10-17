# RichLog

A RichLog is a widget which displays scrollable content that may be appended to in realtime.

Call [RichLog.write][textual.widgets.RichLog.write] with a string or [Rich Renderable](https://rich.readthedocs.io/en/latest/protocol.html) to write content to the end of the RichLog. Call [RichLog.clear][textual.widgets.RichLog.clear] to clear the content.

!!! tip

    See also [Log](../widgets/log.md) which is an alternative to `RichLog` but specialized for simple text.

- [X] Focusable
- [ ] Container

## Example

The example below shows an application showing a `RichLog` with different kinds of data logged.

=== "Output"

    ```{.textual path="docs/examples/widgets/rich_log.py" press="H,i"}
    ```

=== "rich_log.py"

    ```python
    --8<-- "docs/examples/widgets/rich_log.py"
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

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.


---


::: textual.widgets.RichLog
    options:
      heading_level: 2
