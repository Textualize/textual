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

The is the second big feature release after last week's [command palette](./release0.37.0.md).
We are really excited about this one!

The [TextArea](/docs/widgets/textarea.md) has finally landed.
I know a lot of folk have been waiting for this one.
Textual's TextArea is a fully-featured widget for editing code, with syntax highlighting and line numbers.
It is highlight configurable, and looks great.

I am personally excited to see what people will build with it!

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
This does work for the widget in question, but (prior to 0.38.0) the `Label` rule would style *all* Labels &mdash; which was probably not intended.

With version 0.38.0, the CSS is scoped so that only the widget's labels will be styled.
This is almost always what you want, which is why it is enabled by default.
If you do want to style something outside of the widget you can set `SCOPED_CSS=False` (as a classvar)

See the [release](https://github.com/Textualize/textual/releases/tag/v0.38.0) page for the full details on this release.

## Join us

Join our [Discord server](https://discord.gg/Enf6Z3qhVr) if you want to discuss Textual with the Textualize devs, or the community.
