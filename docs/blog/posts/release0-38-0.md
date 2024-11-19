---
draft: false
date: 2023-09-21
categories:
  - Release
title: "Textual 0.38.0 adds a syntax aware TextArea"
authors:
  - willmcgugan
---

# Textual 0.38.0 adds a syntax aware TextArea

This is the second big feature release this month after last week's [command palette](./release0.37.0.md).

<!-- more -->

The [TextArea](../../widgets/text_area.md) has finally landed.
I know a lot of folk have been waiting for this one.
Textual's TextArea is a fully-featured widget for editing code, with syntax highlighting and line numbers.
It is highly configurable, and looks great.

Darren Burns (the author of this widget) has penned a terrific write-up on the TextArea.
See [Things I learned while building Textual's TextArea](./text-area-learnings.md) for some of the challenges he faced.


## Scoped CSS

Another notable feature added in 0.38.0 is *scoped* CSS.
A common gotcha in building Textual widgets is that you could write CSS that impacted styles outside of that widget.

Consider the following widget:

```python
class MyWidget(Widget):
    DEFAULT_CSS = """
    MyWidget {
        height: auto;
        border: magenta;
    }
    Label {
        border: solid green;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("foo")
        yield Label("bar")
```

The author has intended to style the labels in that widget by adding a green border.
This does work for the widget in question, but (prior to 0.38.0) the `Label` rule would style *all* Labels (including any outside of the widget) &mdash; which was probably not intended.

With version 0.38.0, the CSS is scoped so that only the widget's labels will be styled.
This is almost always what you want, which is why it is enabled by default.
If you do want to style something outside of the widget you can set `SCOPED_CSS=False` (as a classvar).


## Light and Dark pseudo selectors

We've also made a slight quality of life improvement to the CSS, by adding `:light` and `:dark` pseudo selectors.
This allows you to change styles depending on whether the app is currently using a light or dark theme.

This was possible before, just a little verbose.
Here's how you would do it in 0.37.0:

```css
App.-dark-mode MyWidget Label {
    ...
}
```

In 0.38.0 it's a little more concise and readable:

```css
MyWidget:dark Label {
    ...
}
```

## Testing guide

Not strictly part of the release, but we've added a [guide on testing](/guide/testing) Textual apps.

As you may know, we are on a mission to make TUIs a serious proposition for critical apps, which makes testing essential.
We've extracted and documented our internal testing tools, including our snapshot tests pytest plugin [pytest-textual-snapshot](https://pypi.org/project/pytest-textual-snapshot/).

This gives devs powerful tools to ensure the quality of their apps.
Let us know your thoughts on that!

## Release notes

See the [release](https://github.com/Textualize/textual/releases/tag/v0.38.0) page for the full details on this release.


## What's next?

There's lots of features planned over the next few months.
One feature I am particularly excited by is a widget to generate plots by wrapping the awesome [Plotext](https://pypi.org/project/plotext/) library.
Check out some early work on this feature:

<div class="video-wrapper">
<iframe width="1163" height="1005" src="https://www.youtube.com/embed/A3uKzWErC8o" title="Preview of Textual Plot widget" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>

## Join us

Join our [Discord server](https://discord.gg/Enf6Z3qhVr) if you want to discuss Textual with the Textualize devs, or the community.
