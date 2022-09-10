# Styles

Textual provides a large number of *styles* you can use to customize how your app looks and feels. In this chapter will will look at how you can edit styles in your applications.


## Styles object

Every widget class in Textual provides a `styles` object which contains a number of writable attributes. Styles define the position and size of a widget, in addition to color, text style, borders, alignment and much more.

Let's look at a simple example which sets the styles on the `screen` (a special widget that represents the screen).

```python title="screen.py" hl_lines="6-7"
--8<-- "docs/examples/guide/styles/screen.py"
```

The first line sets `screen.styles.background` to `"darkblue"` which will change the background color to dark blue. There are a few other ways of setting color which we will explore later.

The second line sets `screen.styles.border` to a tuple of `("heavy", "white")` which tells Textual to draw a white border with a style of `"heavy"`. Running this code will show the following:

```{.textual path="docs/examples/guide/styles/screen.py"}
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


