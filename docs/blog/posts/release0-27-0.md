---
draft: false
date: 2023-06-01
categories:
  - Release
title: "Textual adds Sparklines, Selection list, Input validation, and tool tips"
authors:
  - willmcgugan
---

# Textual adds Sparklines, Selection list, Input validation, and tool tips

It's been 12 days since the last Textual release, which is longer than our usual release cycle of a week.

We've been a little distracted with our "dogfood" projects: [Frogmouth](https://github.com/Textualize/frogmouth) and [Trogon](https://github.com/Textualize/trogon). Both of which hit 1000 Github stars in 24 hours. We will be maintaining / updating those, but it is business as usual for this Textual release (and it's a big one). We have such sights to show you.

<!-- more -->

## Sparkline widget

A [Sparkline](../../widget_gallery.md#sparkline) is essentially a mini-plot. Just detailed enough to keep an eye on time-series data.

<div>
--8<-- "docs/blog/images/sparkline.svg"
</div>

Colors are configurable, and all it takes is a call to [`set_interval`](https://textual.textualize.io/api/message_pump/#textual.message_pump.MessagePump.set_interval) to make it animate.

## Selection list

Next up is the [SelectionList](../../widget_gallery.md#selectionlist) widget. Essentially a scrolling list of checkboxes. Lots of use cases for this one.

<div>
--8<-- "docs/blog/images/selection-list.svg"
</div>

## Tooltips

We've added [tooltips](../../guide/widgets.md#tooltips) to Textual widgets.

The API couldn't be simpler: simply assign a string to the `tooltip` property on any widget.
This string will be displayed after 300ms when you hover over the widget.


<div>
--8<-- "docs/blog/images/tooltips.svg"
</div>

As always, you can configure how the tooltips will be displayed with CSS.

## Input updates

We have some quality of life improvements for the [Input](../../widget_gallery.md#input) widget.

You can now use a simple declarative API to [validating input](/widgets/input/#validating-input).

<div>
--8<-- "docs/blog/images/validation.svg"
</div>

Also in this release is a suggestion API, which will *suggest* auto completions as you type.
Hit <kbd>right</kbd> to accept the suggestion.

Here's a screenshot:

<div>
--8<-- "docs/blog/images/suggest.svg"
</div>

You could use this API to offer suggestions from a fixed list, or even pull the data from a network request.

## Join us

Development on Textual is *fast*.
We're very responsive to issues and feature requests.

If you have any suggestions, jump on our [Discord server](https://discord.gg/Enf6Z3qhVr) and you may see your feature in the next release!
