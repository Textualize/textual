# Save time with Textual containers

Textual's [containers][textual.containers] provide a convenient way of arranging your widgets. Let's look at them in a little detail.

!!! info "Are you in the right place?"

    We are talking about Textual container widgets here. Not to be confused with [containerization](https://en.wikipedia.org/wiki/Containerization_(computing))&mdash;which is something else entirely!


## What are containers?

Containers are reusable [compound widgets](../guide/widgets.md#compound-widgets) with preset styles to arrange their children.
For instance, there is a [Horizontal][textual.containers.Horizontal] container which arranges all of its children in a horizontal row.
Let's look at a quick example of that:

```python hl_lines="2 21"
--8<-- "docs/examples/how-to/containers01.py"
```

1. Use the with statement to add the Horizontal container.
2. Any widgets yielded within the Horizontal block will be arranged in a horizontal row.

Here's the output:

```{.textual path="docs/examples/how-to/containers01.py"}
```

Note that inside the `Horizontal` block new widgets will be placed to the right of previous widgets, forming a row.
This will still be the case if you later add or remove widgets.
Without the container, the widgets would be stacked vertically.

### How are containers implemented?

Before I describe some of the other containers, I would like to show how containers are implemented.
The following is the actual source of the `Horizontal` widget:

```python
class Horizontal(Widget):
    """An expanding container with horizontal layout and no scrollbars."""

    DEFAULT_CSS = """
    Horizontal {
        width: 1fr;
        height: 1fr;
        layout: horizontal;
        overflow: hidden hidden;
    }
    """
```

That's it!
A simple widget with a few preset styles.
The other containers are just as simple.

## Horizontal and Vertical

We've seen the `Horizontal` container in action.
The [Vertical][textual.containers.Vertical] container, as you may have guessed, work the same but arranges its children vertically, i.e. from top to bottom.

You can probably imagine what this looks like, but for sake of completeness, here is an example with a Vertical container:

```python hl_lines="2 21"
--8<-- "docs/examples/how-to/containers02.py"
```

1. Stack the widgets vertically.

And here's the output:

```{.textual path="docs/examples/how-to/containers02.py"}
```

Three boxes, vertically stacked.

!!! tip "Styling layout"

    You can set the layout of a compound widget with the [layout](../styles/layout.md) rule.

### Size behavior

Something to keep in mind when using `Horizontal` or `Vertical` is that they will consume the remaining space in the screen. Let's look at an example to illustrate that.

The following code adds a `with-border` style which draws a green border around the container.
This will help us visualize the dimensions of the container.

```python
--8<-- "docs/examples/how-to/containers03.py"
```

1. Add the `with-border` class to draw a border around the container.

Here's the output:

```{.textual path="docs/examples/how-to/containers03.py"}
```

Notice how the container is as large as the screen.
Let's look at what happens if we add another container:

```python hl_lines="31-34"
--8<-- "docs/examples/how-to/containers04.py"
```

And here's the result:

```{.textual path="docs/examples/how-to/containers04.py"}
```

Two horizontal containers divide the remaining screen space in two.
If you were to add another horizontal it would divide the screen space in to thirds&mdash;and so on.

This makes `Horizontal` and `Vertical` excellent for designing the macro layout of your app's interface, but not for making tightly packed rows or columns. For that you need the *group* containers which I'll cover next.

!!! tip "FR Units"

    You can implement this behavior of dividing the screen in your own widgets with [FR units](../guide/styles.md#fr-units)


## Group containers

The [HorizontalGroup][textual.containers.HorizontalGroup] and [VerticalGroup][textual.containers.VerticalGroup] containers are very similar to their non-group counterparts, but don't expand to fill the screen space.

Let's look at an example.
In the following code, we have two HorizontalGroups with a border so we can visualize their size.

```python hl_lines="2 27 31"
--8<-- "docs/examples/how-to/containers05.py"
```

Here's the output:

```{.textual path="docs/examples/how-to/containers05.py"}
```

We can see that the widgets are arranged horizontally as before, but they only use as much vertical space as required to fit.

## Scrolling containers

Something to watch out for regarding the previous containers we have discussed, is that they don't scroll by default.
Let's see what happens if we add more boxes than could fit on the screen.

In the following example, we will add 10 boxes:

```python hl_lines="28 29"
--8<-- "docs/examples/how-to/containers06.py"
```

Here's the output:

```{.textual path="docs/examples/how-to/containers06.py"}
```

We have add 10 `Box` widgets, but there is not enough room for them to fit.
The remaining boxes are off-screen and can't be viewed unless the user resizes their screen.

If we expect more content that fits, we can replacing the containers with [HorizontalScroll][textual.containers.HorizontalScroll] or [VerticalScroll][textual.containers.VerticalScroll], which will automatically add scrollbars if required.

Let's make that change:

```python hl_lines="2 27"
--8<-- "docs/examples/how-to/containers07.py"
```

Here's the output:

```{.textual path="docs/examples/how-to/containers07.py"}
```

We now have a scrollbar we can click and drag to see all the boxes.

!!! tip "Automatic scrollbars"  

    You can also implement automatic scrollbars with the [overflow](../styles/overflow.md) style.


## Center, Right, and Middle

The [Center][textual.containers.Center], [Right][textual.containers.Right], and [Middle][textual.containers.Middle] containers are handy for setting the alignment of select widgets.

First lets look at `Center` and `Right` which align their children on the horizontal axis (there is no `Left` container, as this is the default).

Here's an example:

```python hl_lines="2 28 30"
--8<-- "docs/examples/how-to/containers08.py"
```

1. The default is to align widgets to the left.
2. Align the child to the center.
3. Align the child to the right edge.

Here's the output:

```{.textual path="docs/examples/how-to/containers08.py"}
```

Note how `Center` and `Right` expand to fill the horizontal dimension, but are only as tall as they need to be.

!!! tip "Alignment in TCSS"

    You can set alignment in TCSS with the [align](../styles/align.md) rule.

The [Middle][textual.containers.Middle] container aligns its children to the center of the *vertical* axis.
Let's look at an example.
The following code aligns three boxes on the vertical axis:

```python hl_lines="2 27"
--8<-- "docs/examples/how-to/containers09.py"
```

1. Align children to the center of the vertical axis.

Here's the output:

```{.textual path="docs/examples/how-to/containers09.py"}
```

Note how the container expands on the vertical axis, but fits on the horizontal axis.

## Other containers

This how-to covers the most common widgets, but isn't exhausted.
Be sure to visit the [container reference][textual.containers] for the full list.
There may be new containers added in future versions of Textual.

## Custom containers

The builtin [containers][textual.containers] cover a number of common layout patterns, but are unlikely to cover every possible requirement.
Fortunately, creating your own is easy.
Just like the builtin containers, you can create a container by extending Widget and adding little TCSS.

Here's a template for a custom container:

```python
class MyContainer(Widget):
    """My custom container."""    
    DEFAULT_CSS = """
    MyContainer {
        # Your rules here
    }
    """    
```

## Summary

- Containers are compound widgets with preset styles for arranging their children.
- [`Horizontal`][textual.containers.Horizontal] and [`Vertical`][textual.containers.Vertical] containers stretch to fill available space.
- [`HorizontalGroup`][textual.containers.HorizontalGroup] and [`VerticalGroup`][textual.containers.VerticalGroup] fit to the height of their contents.
- [`HorizontalScroll`][textual.containers.HorizontalScroll] and [`VerticalScroll`][textual.containers.VerticalScroll] add automatic scrollbars.
- [`Center`][textual.containers.Center], [`Right`][textual.containers.Right], and [`Middle`][textual.containers.Middle] set alignment.
- Custom containers are trivial to create.
