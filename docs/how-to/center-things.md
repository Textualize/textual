# Center things

If you have ever needed to center something in a web page, you will be glad to know it is **much** easier in Textual.

This article discusses a few different ways in which things can be centered, and the differences between them.

## Aligning widgets

The [align](../styles/align.md) rule will center a widget relative to one or both edges.
This rule is applied to a *container*, and will impact how the container's children are arranged.
Let's see this in practice with a trivial app containing a [Static](../widgets/static.md) widget:

```python
--8<-- "docs/examples/how-to/center01.py"
```

Here's the output:

```{.textual path="docs/examples/how-to/center01.py"}
```

The container of the widget is the screen, which has the `align: center middle;` rule applied. The
`center` part tells Textual to align in the horizontal direction, and `middle` tells Textual to align in the vertical direction.

The output *may* surprise you.
The text appears to be aligned in the middle (i.e. vertical edge), but *left* aligned on the horizontal.
This isn't a bug &mdash; I promise.
Let's make a small change to reveal what is happening here.
In the next example, we will add a background and a border to our text:

!!! tip

    Adding a border is a very good way of visualizing layout issues, if something isn't behaving as you would expect.

```python hl_lines="13-16 20"
--8<-- "docs/examples/how-to/center02.py"
```

The static widget will now have a blue background and white border:

```{.textual path="docs/examples/how-to/center02.py"}
```

Note the static widget is as wide as the screen.
Since the widget is as wide as its container, there is no room for it to move in the horizontal direction.

!!! info

    The `align` rule applies to *widgets*, not the text.

In order to see the `center` alignment, we will have to make the widget smaller than the width of the screen.
Let's set the width of the Static widget to `auto`, which will make the widget just wide enough to fit the content:

```python hl_lines="16"
--8<-- "docs/examples/how-to/center03.py"
```

If you run this now, you should see the widget is aligned on both axis:

```{.textual path="docs/examples/how-to/center03.py"}
```

## Aligning text

In addition to aligning widgets, you may also want to align *text*.
In order to demonstrate the difference, lets update the example with some longer text.
We will also set the width of the widget to something smaller, to force the text to wrap.

```python hl_lines="4 18 23"
--8<-- "docs/examples/how-to/center04.py"
```

Here's what it looks like with longer text:

```{.textual path="docs/examples/how-to/center04.py"}
```

Note how the widget is centered, but the text within it is flushed to the left edge.
Left aligned text is the default, but you can also center the text with the [text-align](../styles/text_align.md) rule.
Let's center align the longer text by setting this rule:

```python hl_lines="19"
--8<-- "docs/examples/how-to/center05.py"
```

If you run this, you will see that each line of text is individually centered:

```{.textual path="docs/examples/how-to/center05.py"}
```

You can also use `text-align` to right align text or justify the text (align to both edges).

## Aligning content

There is one last rule that can help us center things.
The [content-align](../styles/content_align.md) rule aligns content *within* a widget.
It treats the text as a rectangular region and positions it relative to the space inside a widget's border.

In order to see why we might need this rule, we need to make the Static widget larger than required to fit the text.
Let's set the height of the Static widget to 9 to give the content room to move:

```python hl_lines="19"
--8<-- "docs/examples/how-to/center06.py"
```

Here's what it looks like with the larger widget:

```{.textual path="docs/examples/how-to/center06.py"}
```

Textual aligns a widget's content to the top border by default, which is why the space is below the text.
We can tell Textual to align the content to the center by setting `content-align: center middle`;

!!! note

    Strictly speaking, we only need to align the content vertically here (there is no room to move the content left or right)
    So we could have done `content-align-vertical: middle;`

```python hl_lines="21"
--8<-- "docs/examples/how-to/center07.py"
```

If you run this now, the content will be centered within the widget:

```{.textual path="docs/examples/how-to/center07.py"}
```

## Aligning multiple widgets

It's just as easy to align multiple widgets as it is a single widget.
Applying `align: center middle;` to the parent widget (screen or other container) will align all its children.

Let's create an example with two widgets.
The following code adds two widgets with auto dimensions:

```python
--8<-- "docs/examples/how-to/center08.py"
```

This produces the following output:

```{.textual path="docs/examples/how-to/center08.py"}
```

We can center both those widgets by applying the `align` rule as before:

```python hl_lines="9-11"
--8<-- "docs/examples/how-to/center09.py"
```

Here's the output:

```{.textual path="docs/examples/how-to/center09.py"}
```

Note how the widgets are aligned as if they are a single group.
In other words, their position relative to each other didn't change, just their position relative to the screen.

If you do want to center each widget independently, you can place each widget inside its own container, and set `align` for those containers.
Textual has a builtin [`Center`][textual.containers.Center] container for just this purpose.

Let's wrap our two widgets in a `Center` container:

```python hl_lines="2 22 24"
--8<-- "docs/examples/how-to/center10.py"
```

If you run this, you will see that the widgets are centered relative to each other, not just the screen:

```{.textual path="docs/examples/how-to/center10.py"}
```

## Summary

Keep the following in mind when you want to center content in Textual:

- In order to center a widget, it needs to be smaller than its container.
- The `align` rule is applied to the *parent* of the widget you want to center (i.e. the widget's container).
- The `text-align` rule aligns text on a line by line basis.
- The `content-align` rule aligns content *within* a widget.
- Use the [`Center`][textual.containers.Center] container if you want to align multiple widgets relative to each other.
- Add a border if the alignment isn't working as you would expect.

---

If you need further help, we are here to [help](../help.md).
