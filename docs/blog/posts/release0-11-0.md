---
draft: false
date: 2023-02-15
categories:
  - Release
title: "Textual 0.11.0 adds a beautiful Markdown widget"
authors:
  - willmcgugan
---

# Textual 0.11.0 adds a beautiful Markdown widget

We released Textual 0.10.0 25 days ago, which is a little longer than our usual release cycle. What have we been up to?

<!-- more -->

The headline feature of this release is the enhanced Markdown support. Here's a screenshot of an example:

<div>
--8<-- "docs/blog/images/markdown-viewer.svg"
</div>

!!! tip

    You can generate these SVG screenshots for your app with `textual run my_app.py --screenshot 5` which will export a screenshot after 5 seconds.

There are actually 2 new widgets: [Markdown](./../../widgets/markdown.md) for a simple Markdown document, and [MarkdownViewer](./../../widgets/markdown_viewer.md) which adds browser-like navigation and a table of contents.

Textual has had support for Markdown since day one by embedding a Rich [Markdown](https://rich.readthedocs.io/en/latest/markdown.html) object -- which still gives decent results! This new widget adds dynamic controls such as scrollable code fences and tables, in addition to working links.

In future releases we plan on adding more Markdown extensions, and the ability to easily embed custom widgets within the document. I'm sure there are plenty of interesting applications that could be powered by dynamically generated Markdown documents.

## DataTable improvements

There has been a lot of work on the [DataTable](../../widgets/data_table.md) API. We've added the ability to sort the data, which required that we introduce the concept of row and column keys. You can now reference rows / columns / cells by their coordinate or by row / column key.

Additionally there are new [update_cell][textual.widgets.DataTable.update_cell] and [update_cell_at][textual.widgets.DataTable.update_cell_at] methods to update cells after the data has been populated. Future releases will have more methods to manipulate table data, which will make it a very general purpose (and powerful) widget.

## Tree control

The [Tree](../../widgets/tree.md) widget has grown a few methods to programmatically expand, collapse and toggle tree nodes.

## Breaking changes

There are a few breaking changes in this release. These are mostly naming and import related, which should be easy to fix if you are affected. Here's a few notable examples:

- `Checkbox` has been renamed to `Switch`. This is because we plan to introduce complimentary `Checkbox` and `RadioButton` widgets in a future release, but we loved the look of *Switches* too much to drop them.
- We've dropped the `emit` and `emit_no_wait` methods. These methods posted message to the parent widget, but we found that made it problematic to subclass widgets. In almost all situations you want to replace these with `self.post_message` (or `self.post_message_no_wait`).

Be sure to check the [CHANGELOG](https://github.com/Textualize/textual/blob/main/CHANGELOG.md) for the full details on potential breaking changes.

## Join us!

We're having fun on our [Discord server](https://discord.gg/Enf6Z3qhVr). Join us there to talk to Textualize developers and share ideas.
