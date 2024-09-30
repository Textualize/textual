---
title: "How do I center a widget in a screen?"
alt_titles:
  - "centre a widget"
  - "centre widgets"
  - "center a control"
  - "centre a control"
  - "center controls"
  - "centre controls"
---

!!! tip

    See [*How To Center Things*](https://textual.textualize.io/how-to/center-things/) in the
    Textual documentation for a more comprehensive answer to this question.

To center a widget within a container use
[`align`](https://textual.textualize.io/styles/align/). But remember that
`align` works on the *children* of a container, it isn't something you use
on the child you want centered.

For example, here's an app that shows a `Button` in the middle of a
`Screen`:

```python
from textual.app import App, ComposeResult
from textual.widgets import Button

class ButtonApp(App):

    CSS = """
    Screen {
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        yield Button("PUSH ME!")

if __name__ == "__main__":
    ButtonApp().run()
```

If you use the above on multiple widgets, you'll find they appear to
"left-align" in the center of the screen, like this:

```
+-----+
|     |
+-----+

+---------+
|         |
+---------+

+---------------+
|               |
+---------------+
```

If you want them more like this:

```
     +-----+
     |     |
     +-----+

   +---------+
   |         |
   +---------+

+---------------+
|               |
+---------------+
```

The best approach is to wrap each widget in a [`Center`
container](https://textual.textualize.io/api/containers/#textual.containers.Center)
that individually centers it. For example:

```python
from textual.app import App, ComposeResult
from textual.containers import Center
from textual.widgets import Button

class ButtonApp(App):

    CSS = """
    Screen {
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        yield Center(Button("PUSH ME!"))
        yield Center(Button("AND ME!"))
        yield Center(Button("ALSO PLEASE PUSH ME!"))
        yield Center(Button("HEY ME ALSO!!"))

if __name__ == "__main__":
    ButtonApp().run()
```
