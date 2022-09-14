# Styles

In this chapter will explore how you can apply styles to your application to create beautiful user interfaces.


## Styles object

Every Textual widget class provides a `styles` object which contains a number of attributes. These attributes tell Textual how the widget should be displayed, and how it should be positioned on the screen relative to other widgets. You can set any of these styles in your code and Textual will update the screen accordingly.

!!! note

    These docs use the term *screen* to describe the contents of the terminal, which will typically be a window on your desktop.

Let's look at a simple example which sets the styles on `screen` (a special widget that represents the screen).

```python title="screen.py" hl_lines="6-7"
--8<-- "docs/examples/guide/styles/screen.py"
```

The first line sets the [background](../styles/background.md) style to `"darkblue"` which will change the background color to dark blue. There are a few other ways of setting color which we will explore later.

The second line sets [border](../styles/border.md) to a tuple of `("heavy", "white")` which tells Textual to draw a white border with a style of `"heavy"`. Running this code will show the following:

```{.textual path="docs/examples/guide/styles/screen.py"}
```

## Styling widgets

Setting styles on screen is useful, but to create most user interfaces we will also need to apply styles to other widgets.

The following example adds a static widget which we will apply some styles to:

```python title="widget.py" hl_lines="7 11-12"
--8<-- "docs/examples/guide/styles/widget.py"
```

The compose method stores a reference to the widget before yielding it. In our mount handler we can use that reference to set some styles. We set the same styles as the screen example, but this time on the widget. Here is the result:

```{.textual path="docs/examples/guide/styles/widget.py"}
```

Widgets will occupy the full width of the screen and as many lines as required to fit in the vertical direction, which is why we see a wide box on the top of the screen.

Note how the combined height of the widget is three rows (lines) in the terminal. This is because a border adds two rows (and two columns). If you were to remove the line that sets the border style, the widget would occupy only a single row.

Widgets will also wrap text by default. If you were to replace `"Textual"` with a long paragraph of text, the widget will expand downwards to fit.

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
- HSL colors start with `hsl` followed by a angle between 0 adn 360 and two percentage values, representing Hue, Saturation and Lightness. For example `hsl(0,100%,50%)` is intense red and `hsl(280,60%,49%)` is *dark orchid*


The background and color styles will also accept a [color][textual.color.Color] object which is convenient if you want to create colors dynamically.

The following example adds three widgets and sets color styles.

```python title="colors01.py" hl_lines="16-19"
--8<-- "docs/examples/guide/styles/colors01.py"
```

Here is the output:

```{.textual path="docs/examples/guide/styles/colors01.py"}
```

### Alpha

Textual (and computers in general) represents color internally as a tuple of three values for the red, green, and blue components, which when combined create all of the 16.7 million colors a typical computer screen can display.

Textual support a common fourth value called *alpha* which is how transparent a color is. If you set this value on a background color Textual will blend the background color with the background underneath it. If you set alpha on the text, then it will blend the text with its background.

There are a few ways you can set alpha on a color in Textual.

- You can set the alpha value of a color by adding a fourth pair (or digit) to a hex color. The extra digits set an opacity of 0 for completely transparent to 255 (completely opaque). Any values between 0 and 255 will be translucent. For example `"#9932CC7f"` is a dark orchid which is roughly 50% translucent.
- You can set alpha with the `rgba` format, which is identical to `rgb` with the additional of a fourth value that should be between 0 and 1, where 0 is invisible and 1 is opaque. For example `"rgba(192,78,96,0.5)"`.
- You can add the `a` parameter on a [Color][textual.color.Color] object. For example `Color(192, 78, 96, a=0.5)` creates a translucent dark orchid. 

The following examples shows what happens when you set alpha on background colors:

```python title="colors01.py" hl_lines="12-15"
--8<-- "docs/examples/guide/styles/colors02.py"
```

We set the `background` style to a color with an alpha that ranges from 0.1 to 1. Notice how with an alpha of 0.1 the background almost matches the screen, but at 1.0 it is a solid color.

```{.textual path="docs/examples/guide/styles/colors02.py"}
```

## Dimensions

Widgets occupy a rectangular region of the screen, which may be as small as a single character or as large as the screen. Potentially *larger* if scrolling is enabled.

### Box Model

The size of a widget on screen is the total of a number of settings.

- [width](../styles/width.md) and [height](../styles/width.md) define the size of the content area which contains text or other content set in your code.
- [padding](../styles/padding.md) adds optional space around the content area. 
- [border](../styles/border.md) draws an optional rectangular border around the padding and the content area.

Additionally, the [margin](../styles/margin.md) style adds space around a widgets border, which isn't technically part of the widget, but provide visual separation between widgets.

Together these styles compose the widget's *box model*. The following diagram shows how these settings are combined:

<div class="excalidraw">
--8<-- "docs/images/styles/box.excalidraw.svg"
</div>

### Width and height

Setting the width restricts the number of columns used by a widget, and setting the height restricts the number of rows. Let's look at an example which sets both dimensions.

```python title="dimensions01.py" hl_lines="21-22"
--8<-- "docs/examples/guide/styles/dimensions01.py"
```

This code produces the following result.

```{.textual path="docs/examples/guide/styles/dimensions01.py"}
```

Note how the text wraps in the widget, and is cropped because it doesn't fit in the space provided.

#### Auto

In practice, we generally want the size of a widget to adapt to it's content. We can use a special value to achieve this. If you set width or height to "auto", then that dimension will grow to fit the content.

Let's set the height to auto and see what happens.


```python title="dimensions02.py" hl_lines="22"
--8<-- "docs/examples/guide/styles/dimensions02.py"
```

If you run this you will see the following:

```{.textual path="docs/examples/guide/styles/dimensions02.py"}
```

The height has grown to accommodate the full text.

#### Units

TODO: Styles docs

- What are styles
- Styles object on widgets / app
- Setting styles via CSS
- Box model
- Color / Background
- Borders / Outline


