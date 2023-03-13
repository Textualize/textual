---
draft: false
date: 2023-03-13
categories:
  - Release
title: "Textual 0.15.0 adds a tabs widget"
authors:
  - willmcgugan
---

# Textual 0.15.0 adds a tabs widget

We've just pushed Textual 0.15.0, only 4 days after the previous version. That's a little faster than our typical release cadence of 1 to 2 weeks.

What's new in this release?

<!-- more -->

The highlight of this release is a new [Tabs](./widgets/../../../widgets/tabs.md) widget to display tabs which can be navigated much like tabs in a browser. Here's a screenshot:

<div>
--8<-- "docs/blog/images/tabs_widget.svg"
</div>

In a future release, this will be combined with the [ContentSwitcher](../../widgets/content_switcher.md) widget to create a traditional tabbed dialog. Although Tabs is still useful as a standalone widgets.

!!! tip

    I like to tweet progress with widgets on Twitter. See the [#textualtabs](https://twitter.com/search?q=%23textualtabs&src=typeahead_click) hashtag which documents progress on this widget.

Also in this release is a new [LoadingIndicator](./../../widgets/loading_indicator.md) widget to display a simple animation while waiting for data. Here's a screenshot:

<div>
--8<-- "docs/blog/images/loading_indicator.svg"
</div>

As always, see the [release notes](https://github.com/Textualize/textual/releases/tag/v0.15.0) for the full details on this update.

If you want to talk about these widgets, or anything else Textual related, join us on our [Discord server](https://discord.gg/Enf6Z3qhVr).
