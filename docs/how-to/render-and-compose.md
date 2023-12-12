# Render and compose

A common question that comes up on the [Textual Discord server](https://discord.gg/Enf6Z3qhVr) is what is the difference between [`render`][textual.widget.Widget.render] and [`compose`][textual.widget.Widget.compose] methods on a widget?
In this article we will clarify the differences, and use both these methods to build something fun.

<div class="video-wrapper">
<iframe width="1280" height="922" src="https://www.youtube.com/embed/dYU7jHyabX8" title="" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>

## Which method to use?

Render and compose are easy to confuse because they both ultimately define what a widget will look like, but they have quite different uses. 

The `render` method on a widget returns a [Rich](https://rich.readthedocs.io/en/latest/) renderable, which is anything you could print with Rich.
The simplest renderable is just text; so `render()` methods often return a string, but could equally return a [`Text`](https://rich.readthedocs.io/en/latest/text.html) instance, a [`Table`](https://rich.readthedocs.io/en/latest/tables.html), or anything else from Rich (or third party library).
Whatever is returned from `render()` will be combined with any styles from CSS and displayed within the widget's borders.

The `compose` method is used to build [*compound* widgets](../guide/widgets.md#compound-widgets) (widgets composed of other widgets).

A general rule of thumb, is that if you implement a `compose` method, there is no need for a `render` method because it is the widgets yielded from `compose` which define how the custom widget will look.
However, you *can* mix these two methods.
If you implement both, the `render` method will set the custom widget's *background* and `compose` will add widgets on top of that background.

## Combining render and compose

Let's look at an example that combines both these methods.
We will create a custom widget with a [linear gradient][textual.renderables.gradient.LinearGradient] as a background.
The background will be animated (I did promise *fun*)!

=== "render_compose.py"

    ```python
    --8<-- "docs/examples/how-to/render_compose.py"
    ```

    1. Refresh the widget 30 times a second.
    2. Compose our compound widget, which contains a single Static.
    3. Render a linear gradient in the background.

=== "Output"

    ```{.textual path="docs/examples/how-to/render_compose.py" columns="100" lines="40"}
    ```

The `Splash` custom widget has a `compose` method which adds a simple `Static` widget to display a message.
Additionally there is a `render` method which returns a renderable to fill the background with a gradient.

!!! tip

    As fun as this is, spinning animated gradients may be too distracting for most apps!

## Summary

Keep the following in mind when building [custom widgets](../guide/widgets.md).

1. Use `render` to return simple text, or a Rich renderable.
2. Use `compose` to create a widget out of other widgets.
3. If you define both, then `render` will be used as a *background*.


---

We are here to [help](../help.md)!
