---
draft: false
date: 2023-03-29
categories:
  - Release
title: "Textual 0.17.0 adds translucent screens and Option List"
authors:
  - willmcgugan
---

# Textual 0.17.0 adds translucent screens and Option List

This is a surprisingly large release, given it has been just 7 days since the last version (and we were down a developer for most of that time).

What's new in this release?

<!-- more -->

There are two new notable features I want to cover. The first is a compositor effect.

## Translucent screens

Textual has a concept of "screens" which you can think of as independent UI modes, each with their own user interface and logic.
The App class keeps a stack of these screens so you can switch to a new screen and later return to the previous screen.

!!! tip inline end "Screens"

    See the [guide](../../guide/screens.md) to learn more about the screens API.

    <a href="/guide/screens">
    <div class="excalidraw">
    --8<-- "docs/images/screens/pop_screen.excalidraw.svg"
    </div>
    </a>

Screens can be used to build modal dialogs by *pushing* a screen with controls / buttons, and *popping* the screen when the user has finished with it.
The problem with this approach is that there was nothing to indicate to the user that the original screen was still there, and could be returned to.

In this release we have added alpha support to the Screen's background color which allows the screen underneath to show through, typically blended with a little color.
Applying this to a screen makes it clear than the user can return to the previous screen when they have finished interacting with the modal.

Here's how you can enable this effect with CSS:

```sass hl_lines="3"
DialogScreen {
    align: center middle;
    background: $primary 30%;
}
```

Setting the background to `$primary` will make the background blue (with the default theme).
The addition of `30%` sets the alpha so that it will be blended with the background.
Here's the kind of effect this creates:

<div>
--8<-- "docs/blog/images/transparent_background.svg"
</div>

There are 4 screens in the above screenshot, one for the base screen and one for each of the three dialogs.
Note how each screen modifies the color of the screen below, but leaves everything visible.

See the [docs on screen opacity](../../guide/screens.md#screen-opacity) if you want to add this to your apps.

## Option list

Textual has had a [ListView](../../widgets/list_view.md) widget for a while, which is an excellent way of navigating a list of items (actually other widgets). In this release we've added an [OptionList](../../widgets/option_list.md) which is similar in appearance, but uses the [line api](../../guide/widgets.md#line-api) under the hood. The Line API makes it more efficient when you approach thousands of items.

```{.textual path="docs/examples/widgets/option_list_strings.py"}
```

The Options List accepts [Rich](https://github.com/Textualize/rich/) *renderable*, which means that anything Rich can render may be displayed in a list. Here's an Option List of tables:

```{.textual path="docs/examples/widgets/option_list_tables.py" columns="100" lines="32"}
```

We plan to build on the `OptionList` widget to implement drop-downs, menus, check lists, etc.
But it is still very useful as it is, and you can add it to apps now.

## What else?

There are a number of fixes regarding refreshing in this release. If you had issues with parts of the screen not updating, the new version should resolve it.

There's also a new logging handler, and a "thick" border type.

See [release notes](https://github.com/Textualize/textual/releases/tag/v0.17.0) for the full details.


## Next week

Next week we plan to take a break from building Textual to *building apps* with Textual.
We do this now and again to give us an opportunity to step back and understand things from the perspective of a developer using Textual.
We will hopefully have something interesting to show from the exercise, and new Open Source apps to share.

## Join us

If you want to talk about this update or anything else Textual related, join us on our [Discord server](https://discord.gg/Enf6Z3qhVr).
