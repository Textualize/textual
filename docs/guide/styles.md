# Styles

In this chapter will explore how you can apply styles to your application to create beautiful user interfaces.


## Styles object

Every Textual widget class provides a `styles` object which contains a number of attributes. These attributes tell Textual how the widget should be displayed, and how it should be positioned on the screen relative to other widgets.

!!! note

    These docs use the term *screen* to describe the contents of the terminal, which will typically be a window on your desktop.

If you write to any styles attribute the screen will update accordingly.

Let's look at a simple example which sets the styles on `screen` (a special widget that represents the screen).

```python title="screen.py" hl_lines="6-7"
--8<-- "docs/examples/guide/styles/screen.py"
```

The first line sets the [background](../styles/background.md) style to `"darkblue"` which will change the background color to dark blue. There are a few other ways of setting color which we will explore later.

The second line sets [border](../styles/border.md) to a tuple of `("heavy", "white")` which tells Textual to draw a white border with a style of `"heavy"`. Running this code will show the following:

```{.textual path="docs/examples/guide/styles/screen.py"}
```

## Styling widgets



## Colors

There are a number of style attribute which accept colors. The most commonly used arel be [color](../styles/color.md) which sets the default color of text on a widget, and [background](..styles/background/md) which sets the background color (under the text).

You can set a color value to one of a number of pre-defined color constants, such as "crimson", "lime", and "palegreen". You can find a full list in the [Color reference](../reference/color.md#textual.color--named-colors).

Here's how you would set the screen background to lime:

```python
self.screen.background = "lime"
```

In addition to color names, there are other ways you can specify a color in Textual (which give you access to all 16.7 million colors a typical monitor can display).

- RGB hex colors starts with a `#` followed by three pairs of one or two hex digits; one for the red, green, and blue color components. For example, `#f00` is an intense red color, and `#9932CC` is *dark orchid*.
- RGB decimal color start with `rgb` followed by a tuple of three numbers in the range 0 to 255. For example `rgb(255,0,0)` is intense red, and `rgb(153,50,204)` is *dark orchid*.
- HSL colors start with `hsl` followed by a tuple of three colors in the range 0 to 255, representing the Hue Saturation and Lightness. For example `hsl(0,100%,50%)` is intense red and `hsl(280,60%,49%)` is *dark orchid*



## Box Model


<div class="excalidraw">
--8<-- "docs/images/styles/box.excalidraw.svg"
</div>



TODO: Styles docs

- What are styles
- Styles object on widgets / app
- Setting styles via CSS
- Box model
- Color / Background
- Borders / Outline


