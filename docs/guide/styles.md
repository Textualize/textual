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

The screen is a special-case for a widget, in that it always matches the dimensions of your terminal window. Widgets provide more flexibility for styling.

The following example adds a static widget which we will apply some styles to:

```python title="widget.py" hl_lines="11-12"
--8<-- "docs/examples/guide/styles/widget.py"
```

The compose method stores a reference to the widget before yielding it. In our mount handler we can use that reference to set some styles. We set the same styles as the screen example, but this time on the widget. Here is the result:

```{.textual path="docs/examples/guide/styles/widget.py"}
```

Widgets will occupy the full width of the screen and as many lines as required to fit in the vertical direction, which is why we see a wide box on the top of the screen.

Note how the combined height of the widget is three rows (lines) in the terminal. This is because a border adds two rows (and two column). If you were to remove the line that sets the border style, the widget would occupy only a single row.

Widgets will also wrap text by default. If you were to replace `"Textual"` with a long paragraph of text, it will wrap lines and the widget will extend downwards.

## Colors

There are a number of style attribute which accept colors. The most commonly used are [color](../styles/color.md) which sets the default color of text on a widget, and [background](..styles/background/md) which sets the background color (under the text).

You can set a color value to one of a number of pre-defined color constants, such as "crimson", "lime", and "palegreen". You can find a full list in the [Color reference](../reference/color.md#textual.color--named-colors).

Here's how you would set the screen background to lime:

```python
widget.styles.background = "lime"
```

In addition to color names, you can also use any of the following ways of expressing a color:

- RGB hex colors starts with a `#` followed by three pairs of one or two hex digits; one for the red, green, and blue color components. For example, `#f00` is an intense red color, and `#9932CC` is *dark orchid*.
- RGB decimal color start with `rgb` followed by a tuple of three numbers in the range 0 to 255. For example `rgb(255,0,0)` is intense red, and `rgb(153,50,204)` is *dark orchid*.
- HSL colors start with `hsl` followed by a tuple of three colors in the range 0 to 255, representing the Hue Saturation and Lightness. For example `hsl(0,100%,50%)` is intense red and `hsl(280,60%,49%)` is *dark orchid*


The background and color styles will also accept a [color][textual.color.Color] object which is convenient if you want to create colors dynamically.

The following example adds three widgets and sets color styles.

```python title="colors01.py" hl_lines="16-19"
--8<-- "docs/examples/guide/styles/colors01.py"
```

Here is the output:

```{.textual path="docs/examples/guide/styles/colors01.py"}
```

### Alpha component

Textual (and computers in general) represents color as a tuple of three values for the red, green, and blue components which when combined create all of the 16.7 million colors a typical computer screen can display.

Textual support a common fourth value called *alpha* can be thought of as how transparent a color is. If you set this value on a background color then Textual will blend the background color with the background underneath it. If you set alpha on the text, then it will blend the text with its background.

There are a few ways you can set alpha on a color in Textual.

- You can set the alpha value of a color by adding a fourth pair (or digit) to a hex color. The extra digits set an opacity of 0 for completely transparent to 255 (completely opaque). Any values between 0 and 255 will be translucent. For example `"#9932CC7f"` is a dark orchid which is roughly 50% translucent.
- You can set alpha with the `rgba` format, which is identical to `rgb` with the additional of a fourth value that should be between 0 and 1, where 0 is invisible and 1 is opaque.
- You can add a fourth value to a [Color][textual.color.Color] object. For example `Color(192, 78, 96, 0.5)` creates a translucent dark orchid. 

The following examples shows what happens when you set alpha on background colors:

```python title="colors01.py" hl_lines="12-13"
--8<-- "docs/examples/guide/styles/colors02.py"
```

We set the `background` style to a color with an alpha that ranges from 0.1 to 1. Notice how with an alpha of 0.1 the background almost matches the screen, but at 1.0 it is a solid color.

```{.textual path="docs/examples/guide/styles/colors02.py"}
```

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


