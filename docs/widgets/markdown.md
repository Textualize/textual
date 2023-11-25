# Markdown

!!! tip "Added in version 0.11.0"

A widget to display a Markdown document.

- [ ] Focusable
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

## Reactive Attributes

This widget has no reactive attributes.

## Messages

- [Markdown.TableOfContentsUpdated][textual.widgets.Markdown.TableOfContentsUpdated]
- [Markdown.TableOfContentsSelected][textual.widgets.Markdown.TableOfContentsSelected]
- [Markdown.LinkClicked][textual.widgets.Markdown.LinkClicked]

## Bindings

This widget has no bindings.

## Component Classes

The markdown widget provides the following component classes:

::: textual.widgets.Markdown.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false


## See Also


* [MarkdownViewer][textual.widgets.MarkdownViewer] code reference


---


::: textual.widgets.Markdown
    options:
      heading_level: 2
