---
draft: false
date: 2023-02-24
categories:
  - Release
title: "Textual 0.12.0 adds syntactical sugar and batch updates"
authors:
  - willmcgugan
---

# Textual 0.12.0 adds syntactical sugar and batch updates

It's been just 9 days since the previous release, but we have a few interesting enhancements to the Textual API to talk about.

<!-- more -->

## Better compose

We've added a little *syntactical sugar* to Textual's `compose` methods, which aids both
readability and *editability* (that might not be a word).

First, let's look at the old way of building compose methods. This snippet is taken from the `textual colors` command.


```python
for color_name in ColorSystem.COLOR_NAMES:

    items: list[Widget] = [ColorLabel(f'"{color_name}"')]
    for level in LEVELS:
        color = f"{color_name}-{level}" if level else color_name
        item = ColorItem(
            ColorBar(f"${color}", classes="text label"),
            ColorBar("$text-muted", classes="muted"),
            ColorBar("$text-disabled", classes="disabled"),
            classes=color,
        )
        items.append(item)

    yield ColorGroup(*items, id=f"group-{color_name}")
```

This code *composes* the following color swatches:

<div>
--8<-- "docs/blog/images/colors.svg"
</div>

!!! tip

    You can see this by running `textual colors` from the command line.


The old way was not all that bad, but it did make it hard to see the structure of your app at-a-glance, and editing compose methods always felt a little laborious.

Here's the new syntax, which uses context managers to add children to containers:

```python
for color_name in ColorSystem.COLOR_NAMES:
    with ColorGroup(id=f"group-{color_name}"):
        yield Label(f'"{color_name}"')
        for level in LEVELS:
            color = f"{color_name}-{level}" if level else color_name
            with ColorItem(classes=color):
                yield ColorBar(f"${color}", classes="text label")
                yield ColorBar("$text-muted", classes="muted")
                yield ColorBar("$text-disabled", classes="disabled")
```

The context manager approach generally results in fewer lines of code, and presents attributes on the same line as containers themselves. Additionally, adding widgets to a container can be as simple is indenting them.

You can still construct widgets and containers with positional arguments, but this new syntax is preferred. It's not documented yet, but you can start using it now. We will be updating our examples in the next few weeks.

## Batch updates

Textual is smart about performing updates to the screen. When you make a change that might *repaint* the screen, those changes don't happen immediately. Textual makes a note of them, and repaints the screen a short time later (around a 1/60th of a second). Multiple updates are combined so that Textual does less work overall, and there is none of the flicker you might get with multiple repaints.

Although this works very well, it is possible to introduce a little flicker if you make changes across multiple widgets. And especially if you add or remove many widgets at once. To combat this we have added a [batch_update][textual.app.App.batch_update] context manager which tells Textual to disable screen updates until the end of the with block.

The new [Markdown](./release0-11-0.md) widget uses this context manager when it updates its content. Here's the code:

```python
with self.app.batch_update():
    await self.query("MarkdownBlock").remove()
    await self.mount_all(output)
```

Without the batch update there are a few frames where the old markdown blocks are removed and the new blocks are added (which would be perceived as a brief flicker). With the update, the update appears instant.

## Disabled widgets

A few widgets (such as [Button](./../../widgets/button.md)) had a `disabled` attribute which would fade the widget a little and make it unselectable. We've extended this to all widgets. Although it is particularly applicable to input controls, anything may be disabled. Disabling a container makes its children disabled, so you could use this for disabling a form, for example.

!!! tip

    Disabled widgets may be styled with the `:disabled` CSS pseudo-selector.

## Preventing messages

Also in this release is another context manager, which will disable specified Message types. This doesn't come up as a requirement very often, but it can be very useful when it does. This one is documented, see [Preventing events](./../../guide/events.md#preventing-messages) for details.

## Full changelog

As always see the [release page](https://github.com/Textualize/textual/releases/tag/v0.12.0) for additional changes and bug fixes.

## Join us!

We're having fun on our [Discord server](https://discord.gg/Enf6Z3qhVr). Join us there to talk to Textualize developers and share ideas.
