---
draft: false
date: 2023-03-22
categories:
  - Release
title: "Textual 0.16.0 adds TabbedContent and border titles"
authors:
  - willmcgugan
---

# Textual 0.16.0 adds TabbedContent and border titles

Textual 0.16.0 lands 9 days after the previous release. We have some new features to show you.

<!-- more -->

There are two highlights in this release. In no particular order, the first is [TabbedContent](../../widgets/tabbed_content.md) which uses a row of *tabs* to navigate content. You will have likely encountered this UI in the desktop and web. I think in Windows they are known as "Tabbed Dialogs".

This widget combines existing [Tabs](../../widgets/tabs.md) and [ContentSwitcher](../../api/content_switcher.md) widgets and adds an expressive interface for composing. Here's a trivial example to use content tabs to navigate a set of three markdown documents:

```python
def compose(self) -> ComposeResult:
    with TabbedContent("Leto", "Jessica", "Paul"):
        yield Markdown(LETO)
        yield Markdown(JESSICA)
        yield Markdown(PAUL)
```

Here's an example of the UI you can create with this widget (note the nesting)!

```{.textual path="docs/examples/widgets/tabbed_content.py" press="j"}
```


## Border titles

The second highlight is a frequently requested feature (FRF?). Widgets now have the two new string properties, `border_title` and `border_subtitle`, which will be displayed within the widget's border.

You can set the alignment of these titles via [`border-title-align`](../../styles/border_title_align.md) and [`border-subtitle-align`](../../styles/border_subtitle_align.md). Titles may contain [Console Markup](https://rich.readthedocs.io/en/latest/markup.html), so you can add additional color and style to the labels.

Here's an example of a widget with a title:

<div>
--8<-- "docs/blog/images/border-title.svg"
</div>

BTW the above is a command you can run to see the various border styles you can apply to widgets.

```
textual borders
```

## Container changes

!!! warning "Breaking change"

    If you have an app that uses any container classes, you should read this section.

We've made a change to containers in this release. Previously all containers had *auto* scrollbars, which means that any container would scroll if its children didn't fit. With nested layouts, it could be tricky to understand exactly which containers were scrolling. In 0.16.0 we split containers in to scrolling and non-scrolling versions. So `Horizontal` will now *not* scroll by default, but `HorizontalScroll` will have automatic scrollbars.


## What else?

As always, see the [release notes](https://github.com/Textualize/textual/releases/tag/v0.16.0) for the full details on this update.

If you want to talk about this update or anything else Textual related, join us on our [Discord server](https://discord.gg/Enf6Z3qhVr).
