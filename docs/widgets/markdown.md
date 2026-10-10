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

## Styling Markdown Content

`Markdown` doesn't render its content as plain text — it builds a tree of internal
widgets, one per Markdown element (headers, paragraphs, lists, tables, etc). Each
block element is rendered by a dedicated widget, allowing it to be targeted directly
using Textual CSS.

### Rendered widgets

The table below lists the widget created for each Markdown element. Use these names
as CSS type selectors in your stylesheet.

| Markdown element | Widget |
| :- | :- |
| `# H1` | `MarkdownH1` |
| `## H2` | `MarkdownH2` |
| `### H3` | `MarkdownH3` |
| `#### H4` | `MarkdownH4` |
| `##### H5` | `MarkdownH5` |
| `###### H6` | `MarkdownH6` |
| Horizontal rule (`---`) | `MarkdownHorizontalRule` |
| Paragraph | `MarkdownParagraph` |
| Block quote (`> ...`) | `MarkdownBlockQuote` |
| Bullet list | `MarkdownBulletList` |
| Ordered list | `MarkdownOrderedList` |
| Bullet list item | `MarkdownUnorderedListItem` |
| Ordered list item | `MarkdownOrderedListItem` |
| List bullet/number marker | `MarkdownBullet` |
| Table | `MarkdownTable` |
| Table body | `MarkdownTBody` |
| Table head | `MarkdownTHead` |
| Table row | `MarkdownTR` |
| Table header cell | `MarkdownTH` |
| Table data cell | `MarkdownTD` |
| Code fence / code block | `MarkdownFence` |



For example, to give all block quotes a red left border and make H1s left-aligned
instead of centered:

```css
MarkdownBlockQuote {
    border-left: outer red;
}

MarkdownH1 {
    content-align: left middle;
}
```

### Inline component classes

Inline text styles (as opposed to block-level elements) are exposed as component
classes on `MarkdownBlock`, and can be styled the same way as any other component
class:

| Class | Targets |
| :- | :- |
| `MarkdownBlock > .em` | Emphasized (italic) inline text |
| `MarkdownBlock > .strong` | Strong (bold) inline text |
| `MarkdownBlock > .s` | Strikethrough inline text |
| `MarkdownBlock > .code_inline` | Inline code spans |

```css
MarkdownBlock > .code_inline {
    background: $accent 20%;
    color: $text;
}
```

!!! warning

    These four component classes back the standard Markdown formatting rules.
    Changing them substantially may make inline emphasis, code, etc. harder to
    distinguish from normal text.

### Table component classes

Tables are rendered by `MarkdownTableContent`, which exposes its own component
classes for the header row and grid lines:

| Class | Targets |
| :- | :- |
| `MarkdownTableContent.markdown-table--header` | The header row |
| `MarkdownTableContent.markdown-table--lines` | The keyline/grid separators |

```css
MarkdownTableContent > .markdown-table--header {
    color: $success;
}
```


## See Also


* [MarkdownViewer][textual.widgets.MarkdownViewer] code reference


---


::: textual.widgets.Markdown
    options:
      heading_level: 2