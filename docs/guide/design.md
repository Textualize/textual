# Themes

Textual comes with several built-in themes.
You can also easily create your own themes.
A theme is a simple Python object which maps variable names to colors.
Here's an example:

```python
Theme(
    name="nord",
    primary="#88C0D0",
    secondary="#81A1C1",
    accent="#B48EAD",
    foreground="#D8DEE9",
    background="#2E3440",
    success="#A3BE8C",
    warning="#EBCB8B",
    error="#BF616A",
    surface="#3B4252",
    panel="#434C5E",
    dark=True,
    variables={
        "block-cursor-background": "#88C0D0",
        "block-cursor-foreground": "#2E3440",
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#88C0D0",
        "input-selection-background": "#81a1c1 35%",
    },
)
```

## Theme Variables

Themes consist of up to 11 *base colors*, (`primary`, `secondary`, `accent`, etc.), which Textual uses to generate a broad range of CSS variables.

Sampling from a limited base palette makes it easier to create visually consistent themes,
without needing to manually define a large number of variables.

For example, the `textual-dark` theme defines the *primary* base color as `#004578`.
Textual then generates a number of variations from this base color, such as `$primary`, `$primary-lighten-1` and `$primary-darken-1`.

!!! tip

    If `textual-dev` (the Textual devtools) is installed, you can view the variables generated from a theme by running `textual colors`.

Here's an example of CSS which uses these variables:

```css
MyWidget {
    background: $primary;
    color: $foreground;
}
```

The base colors are also used as the default values for other variables, such as `$border`.
`$border` defines the border color of focused widgets and is set to `$primary` by default.
These variables can also be overridden by passing a `variables` argument to the `Theme` constructor.

## Base Colors

The following table lists each of 11 base colors (as used in CSS) and a description of where they are used by default.

| Color                   | Description                                                                                                                                         |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `$primary`              | The primary color, can be considered the *branding* color. Typically used for titles, and backgrounds for strong emphasis.                          |
| `$secondary`            | An alternative branding color, used for similar purposes as `$primary`, where an app needs to differentiate something from the primary color.       |
| `$foreground`           | The default text color, which should be legible on `$background`, `$surface`, and `$panel`.                                                         |
| `$background`           | A color used for the background, where there is no content. Used as the default background color for screens.                                       |
| `$surface`              | The default background color of widgets, typically sitting on top of `$background`.                                                                 |
| `$panel`                | A color used to differentiate a part of the UI form the main content. Used sparingly in Textual itself.                                             |
| `$boost`                | A color with alpha that can be used to create *layers* on a background.                                                                             |
| `$warning`              | Indicates a warning. Text or background.                                                                                                            |
| `$error`                | Indicates an error.  Text or background.                                                                                                            |
| `$success`              | Used to indicate success.  Text or background.                                                                                                      |
| `$accent`               | Used sparingly to draw attention to a part of the UI (typically borders around focused widgets).                                                    |


## Designing with Colors

Textual pre-defines a number of colors as [CSS variables](../guide/CSS.md#css-variables). For instance, the CSS variable `$primary` is set to `#004578` (the blue used in headers). You can use `$primary` in place of the color in the [background](../styles/background.md) and [color](../styles/color.md) rules, or other any other rule that accepts a color.

Here's an example of CSS that uses color variables:

```css
MyWidget {
    background: $primary;
    color: $text;
}
```

Using variables rather than explicit colors allows Textual to apply color themes. Textual supplies a default light and dark theme, but in the future many more themes will be available.




### Shades

For every color, Textual generates 3 dark shades and 3 light shades.

- Add `-lighten-1`, `-lighten-2`, or `-lighten-3` to the color's variable name to get lighter shades (3 is the lightest).
- Add `-darken-1`, `-darken-2`, and `-darken-3` to a color to get the darker shades (3 is the darkest).

For example, `$secondary-darken-1` is a slightly darkened `$secondary`, and `$error-lighten-3` is a very light version of the `$error` color.

### Dark mode

There are two color themes in Textual, a light mode and dark mode. You can switch between them by toggling the `dark` attribute on the App class.

In dark mode `$background` and `$surface` are off-black. Dark mode also set `$primary-background` and `$secondary-background` to dark versions of `$primary` and `$secondary`.


### Text color

The design system defines three CSS variables you should use for text color.

- `$text` sets the color of text in your app. Most text in your app should have this color.
- `$text-muted` sets a slightly faded text color. Use this for text which has lower importance. For instance a sub-title or supplementary information.
- `$text-disabled` sets faded out text which indicates it has been disabled. For instance, menu items which are not applicable and can't be clicked.

You can set these colors via the [color](../styles/color.md) property. The design system uses `auto` colors for text, which means that Textual will pick either white or black (whichever has better contrast).

!!! information

    These text colors all have some alpha applied, so that even `$text` isn't pure white or pure black. This is done because blending in a little of the background color produces text that is not so harsh on the eyes.

### Theming

In a future version of Textual you will be able to modify theme colors directly, and allow users to configure preferred themes.


## Color Preview

Run the following from the command line to preview the colors defined in the color system:

```bash
textual colors
```

## Theme Reference

Here's a list of the colors defined in the default light and dark themes.

!!! note

    `$boost` will look different on different backgrounds because of its alpha channel.

```{.rich title="Textual Theme Colors"}
from rich import print
from textual.app import DEFAULT_COLORS
from textual.design import show_design
output = show_design(DEFAULT_COLORS["light"], DEFAULT_COLORS["dark"])
```
