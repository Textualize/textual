# Log

A Log widget displays lines of text which may be appended to in realtime.

Call [Log.write_line][textual.widgets.Log.write_line] to write a line at a time, or [Log.write_lines][textual.widgets.Log.write_lines] to write multiple lines at once.

!!! tip

    See also [RichLog][textual.widgets.RichLog] which can write more than just text, and supports a number of advanced features.



- [X] Focusable
- [ ] Container

## Example

The example below shows an application showing a `RichLog` with different kinds of data logged.

=== "Output"

    ```{.textual path="docs/examples/widgets/log.py" press="H,i"}
    ```

=== "rich_log.py"

    ```python
    --8<-- "docs/examples/widgets/log.py"
    ```



## Reactive Attributes

| Name          | Type   | Default | Description                                                  |
| ------------- | ------ | ------- | ------------------------------------------------------------ |
| `max_lines`   | `int`  | `None`  | Maximum number of lines in the log or `None` for no maximum. |
| `auto_scroll` | `bool` | `False` | Scroll to end of log when new lines are added.               |


## Messages

This widget sends no messages.


---


::: textual.widgets.Log
    options:
      heading_level: 2
