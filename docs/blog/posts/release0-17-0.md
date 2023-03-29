---
draft: false
date: 2023-03-29
categories:
  - Release
title: "Textual 0.17.0 adds translucent screens and Options List"
authors:
  - willmcgugan
---

# Textual 0.17.0 adds translucent screens and Options List

This is a surprisingly large release, given it has been just 7 days since the last version, and we were down a developer for most of that time.

What's new in this release?

<!-- more -->

There are two new notable features I want to cover. The first is a compositor effect.

## Translucent screens

Textual has a concept of "screens" which you can think of as different modes, with independent own logic and widgets.
The App class keeps a stack of these screens so you can switch to a new screen, but easily return to the previous screen.

!!! info inline end "Screens"

    See the [screens](../../guide/screens.md) docs for more information.

    <a href="/guide/screens">
    <div class="excalidraw">
    --8<-- "docs/images/screens/pop_screen.excalidraw.svg"
    </div>
    </a>

You can use screens to build modal dialogs by *pushing* a screen with controls / buttons, and *popping* the screen when the user has finished with it.
The problem with this approach is that there was nothing to indicate to the user that the original screen was still there, and could be returned to.

In this release we have added alpha support to a Screen's background color which allows the screen underneath to show through, often blended with a little color.

Adding this to your app couldn't be much easier.
Here's a simple example:

```sass hl_lines="3"
DialogScreen {
    align: center middle;
    background: $primary 30%;
}
```

Setting the background to `$primary` will make the background blue (with the default theme).
The addition of `30%` sets the alpha so that it will be blended with the background.
Here's the kind of effect this creates:

<div class="excalidraw">
--8<-- "docs/blog/images/transparent_background.svg"
</div>

There are 4 screens here, one for the base screen and each of the three dialogs.

## Options list

Textual has had a [ListView](../../widgets/list_view.md) widget for a while, which is an excellent way of navigating a list of items (actually other widgets). In this release we've added an [OptionList](../../widgets/options_list.md) which is similar in appearance, but uses the [line api](../../guide/widgets.md#line-api) under the hood which makes it way more efficient when it comes to very large lists.

## What else?

There are a number of fixes regarding freshing in this release. If you had issues with parts of the screen not updating, the new version should resolve it.

There's also a new logging handler, and a "thick" border type. [release notes](https://github.com/Textualize/textual/releases/tag/v0.17.0) for the full details.

If you want to talk about this update or anything else Textual related, join us on our [Discord server](https://discord.gg/Enf6Z3qhVr).


## Next week

Next week we plan to take a break from building Textual to building apps with Textual.
We do this now and again to give us an opportunity to step back and understand things from the perspective of a developer using Textual.
It will also give us the chance to build some really interesting apps.
Hope it goes without saying, but these will all be under an Open Source license.
