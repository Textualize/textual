---
draft: false
date: 2023-09-15
categories:
  - Release
title: "Textual 0.37.0 adds a command palette"
authors:
  - willmcgugan
---


# Textual 0.37.0 adds a command palette

Textual version 0.37.0 has landed!
The highlight of this release is the new command palette.

<!-- more -->

A command palette gives users quick access to features in your app.
If you hit ctrl+backslash in a Textual app, it will bring up the command palette where you can start typing commands.
The commands are matched with a *fuzzy* search, so you only need to type two or three characters to get to any command.

Here's a video of it in action:

<div class="video-wrapper">
<iframe width="1280" height="auto" src="https://www.youtube.com/embed/sOMIkjmM4MY" title="" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>

Adding your own commands to the command palette is a piece of cake.
Here's the (command) Provider class used in the example above:

```python
class ColorCommands(Provider):
    """A command provider to select colors."""

    async def search(self, query: str) -> Hits:
        """Called for each key."""
        matcher = self.matcher(query)
        for color in COLOR_NAME_TO_RGB.keys():
            score = matcher.match(color)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(color),
                    partial(self.app.post_message, SwitchColor(color)),
                )
```

And here is how you add a provider to your app:

```python
class ColorApp(App):
    """Experiment with the command palette."""

    COMMANDS = App.COMMANDS | {ColorCommands}
```

We're excited about this feature because it is a step towards bringing a common user interface to Textual apps.

!!! quote

    It's a Textual app. I know this.

    &mdash; You, maybe.

The goal is to be able to build apps that may look quite different, but take no time to learn, because once you learn how to use one Textual app, you can use them all.

See the Guide for details on how to work with the [command palette](../../guide/command_palette.md).

## What else?

Also in 0.37.0 we have a new [Collapsible](/widget_gallery/#collapsible) widget, which is a great way of adding content while avoiding a cluttered screen.

And of course, bug fixes and other updates. See the [release](https://github.com/Textualize/textual/releases/tag/v0.37.0) page for the full details.

## What's next?

Coming very soon, is a new TextEditor widget.
This is a super powerful widget to enter arbitrary text, with beautiful syntax highlighting for a number of languages.
We're expecting that to land next week.
Watch this space, or join the [Discord server](https://discord.gg/Enf6Z3qhVr) if you want to be the first to try it out.

## Join us

Join our [Discord server](https://discord.gg/Enf6Z3qhVr) if you want to discuss Textual with the Textualize devs, or the community.
