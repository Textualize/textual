# MarkdownViewer

!!! tip "Added in version 0.11.0"

A Widget to display Markdown content with an optional Table of Contents.

- [x] Focusable
- [ ] Container

!!! note

    This Widget adds browser-like functionality on top of the [Markdown](./markdown.md) widget.


## Example

The following example displays Markdown from a string and a Table of Contents.

=== "Output"

    ```{.textual path="docs/examples/widgets/markdown_viewer.py" columns="100" lines="42"}
    ```

=== "markdown.py"

    ~~~python
    --8<-- "docs/examples/widgets/markdown_viewer.py"
    ~~~

## Reactive Attributes

| Name                     | Type | Default | Description                                                       |
| ------------------------ | ---- | ------- | ----------------------------------------------------------------- |
| `show_table_of_contents` | bool | True    | Wether a Table of Contents should be displayed with the Markdown. |

## See Also

* [Markdown][textual.widgets.Markdown] code reference



---


::: textual.widgets.MarkdownViewer
    options:
      heading_level: 2
