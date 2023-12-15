# Design System

Textual's design system consists of a number of predefined colors and guidelines for how to use them in your app.

You don't have to follow these guidelines, but if you do, you will be able to mix builtin widgets with third party widgets and your own creations, without worrying about clashing colors.


!!! information

    Textual's color system is based on Google's Material design system, modified to suit the terminal.


## Designing with Colors

Textual pre-defines a number of colors as [CSS variables](../guide/CSS.md#css-variables). For instance, the CSS variable `$primary` is set to `#004578` (the blue used in headers). You can use `$primary` in place of the color in the [background](../styles/background.md) and [color](../styles/color.md) rules, or other any other rule that accepts a color.

Here's an example of CSS that uses color variables:

```sass
MyWidget {
    background: $primary;
    color: $text;
}
```

Using variables rather than explicit colors allows Textual to apply color themes. Textual supplies a default light and dark theme, but in the future many more themes will be available.


### Base Colors

There are 12 *base* colors defined in the color scheme. The following table lists each of the color names (as used in CSS) and a description of where to use them.

| Color                   | Description                                                                                                                                         |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `$primary`              | The primary color, can be considered the *branding* color. Typically used for titles, and backgrounds for strong emphasis.                          |
| `$secondary`            | An alternative branding color, used for similar purposes as `$primary`, where an app needs to differentiate something from the primary color.       |
| `$primary-background`   | The primary color applied to a background. On light mode this is the same as `$primary`. In dark mode this is a dimmed version of `$primary`.       |
| `$secondary-background` | The secondary color applied to a background. On light mode this is the same as `$secondary`. In dark mode this is a dimmed version of `$secondary`. |
| `$background`           | A color used for the background, where there is no content.                                                                                         |
| `$surface`              | The color underneath text.                                                                                                                          |
| `$panel`                | A color used to differentiate a part of the UI form the main content. Typically used for dialogs or sidebars.                                       |
| `$boost`                | A color with alpha that can be used to create *layers* on a background.                                                                             |
| `$warning`              | Indicates a warning. Text or background.                                                                                                            |
| `$error`                | Indicates an error.  Text or background.                                                                                                            |
| `$success`              | Used to indicate success.  Text or background.                                                                                                      |
| `$accent`               | Used sparingly to draw attention to a part of the UI (typically borders around focused widgets).                                                    |


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
