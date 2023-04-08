# Markdown

!!! tip "Added in version 0.11.0"

A widget to display a Markdown document.

- [x] Focusable
- [ ] Container


!!! tip

    See [MarkdownViewer](./markdown_viewer.md) for a widget that adds additional features such as a Table of Contents.

## Example

The following example displays Markdown from a string.

=== "Output"

    ```{.textual path="docs/examples/widgets/markdown.py"}
    ```

=== "markdown.py"

    ~~~python
    --8<-- "docs/examples/widgets/markdown.py"
    ~~~

## Messages

- [Markdown.TableOfContentsUpdated][textual.widgets.Markdown.TableOfContentsUpdated]
- [Markdown.TableOfContentsSelected][textual.widgets.Markdown.TableOfContentsSelected]
- [Markdown.LinkClicked][textual.widgets.Markdown.LinkClicked]


## See Also


* [MarkdownViewer][textual.widgets.MarkdownViewer] code reference


---


::: textual.widgets.Markdown
    options:
      heading_level: 2
