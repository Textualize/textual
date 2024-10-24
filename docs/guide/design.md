# Themes

Textual comes with several built-in themes, and it's easy to create your own.

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
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#88C0D0",
        "input-selection-background": "#81a1c1 35%",
    },
)
```

## Theme variables

Themes consist of up to 11 *base colors*, (`primary`, `secondary`, `accent`, etc.), which Textual uses to generate a broad range of CSS variables.
For example, the `textual-dark` theme defines the *primary* base color as `#004578`.

Here's an example of CSS which uses these variables:

```css
MyWidget {
    background: $primary;
    color: $foreground;
}
```

## Base colors

When defining a theme, only the `primary` color is required.
Textual can generate the other base colors if they're not supplied.

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
| `$accent`               | Used sparingly to draw attention. Typically contrasts with $primary and $secondary.                                                                 |

## Shades

For every color, Textual generates 3 dark shades and 3 light shades.

- Add `-lighten-1`, `-lighten-2`, or `-lighten-3` to the color's variable name to get lighter shades (3 is the lightest).
- Add `-darken-1`, `-darken-2`, and `-darken-3` to a color to get the darker shades (3 is the darkest).

For example, `$secondary-darken-1` is a slightly darkened `$secondary`, and `$error-lighten-3` is a very light version of the `$error` color.

## Light and dark themes

Themes can be either "light" or "dark".
This setting is specified in the `Theme` constructor via the `dark` argument, and is used by Textual to determine how to generate shades from base colors.

## Text color

The default color of text in a theme is `$foreground`.
This color should be legible on `$background`, `$surface`, and `$panel` backgrounds.

There is also `$foreground-muted` for text which has lower importance.
`$foreground-disabled` can be used for text which is disabled, for example a menu item which can't be selected.

You can set the text color via the [color](../styles/color.md) CSS property.

### Ensuring text legibility

In some cases, the background color of a widget is unpredictable, meaning we cannot know in advance which text colors will be legible against it.

The theme system defines three CSS variables which you can use to ensure that text is legible on any background.

- `$text` is set to a slightly transparent black or white, depending on which has better contrast against the background the text is on.
- `$text-muted` sets a slightly faded text color. Use this for text which has lower importance. For instance a sub-title or supplementary information.
- `$text-disabled` sets faded out text which indicates it has been disabled. For instance, menu items which are not applicable and can't be clicked.

## Additional variables

Textual uses the base colors as default values for additional variables used throughout the framework.
These variables can be overridden by passing a `variables` argument to the `Theme` constructor.

Here's a comprehensive list of these variables, their purposes, and default values:

### Border

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `$border` | The border color for focused widgets with a border | `$primary` |
| `$border-blurred` | The border color for unfocused widgets | Slightly darkened `$surface` |

### Cursor

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `$block-cursor-foreground` | Text color for block cursor (e.g., in OptionList) | `$text` |
| `$block-cursor-background` | Background color for block cursor | `$primary` |
| `$block-cursor-text-style` | Text style for block cursor | `"bold"` |
| `$block-cursor-blurred-foreground` | Text color for unfocused block cursor | `$text` |
| `$block-cursor-blurred-background` | Background color for unfocused block cursor | `$primary` with 30% opacity |
| `$block-cursor-blurred-text-style` | Text style for unfocused block cursor | `"none"` |
| `$block-hover-background` | Background color when hovering over a block | `$boost` with 5% opacity |

### Input

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `$input-cursor-background` | Background color of the input cursor | `$foreground` |
| `$input-cursor-foreground` | Text color of the input cursor | `$background` |
| `$input-cursor-text-style` | Text style of the input cursor | `"none"` |
| `$input-selection-background` | Background color of selected text | `$primary-lighten-1` with 40% opacity |
| `$input-selection-foreground` | Text color of selected text | `$background` |

### Scrollbar

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `$scrollbar` | Color of the scrollbar | `$panel` |
| `$scrollbar-hover` | Color of the scrollbar when hovered | `$panel-lighten-1` |
| `$scrollbar-active` | Color of the scrollbar when active (being dragged) | `$panel-lighten-2` |
| `$scrollbar-background` | Color of the scrollbar track | `$background-darken-1` |
| `$scrollbar-corner-color` | Color of the scrollbar corner | Same as `$scrollbar-background` |
| `$scrollbar-background-hover` | Color of the scrollbar track when hovering over the scrollbar area | Same as `$scrollbar-background` |
| `$scrollbar-background-active` | Color of the scrollbar track when the scrollbar is active | Same as `$scrollbar-background` |

### Links

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `$link-background` | Background color of links | `"initial"` |
| `$link-background-hover` | Background color of links when hovered | `$primary` |
| `$link-color` | Text color of links | `$text` |
| `$link-style` | Text style of links | `"underline"` |
| `$link-color-hover` | Text color of links when hovered | `$text` |
| `$link-style-hover` | Text style of links when hovered | `"bold not underline"` |

### Footer

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `$footer-foreground` | Text color in the footer | `$foreground` |
| `$footer-background` | Background color of the footer | `$panel` |
| `$footer-key-foreground` | Text color for key bindings in the footer | `$accent` |
| `$footer-key-background` | Background color for key bindings in the footer | `"transparent"` |
| `$footer-description-foreground` | Text color for descriptions in the footer | `$foreground` |
| `$footer-description-background` | Background color for descriptions in the footer | `"transparent"` |
| `$footer-item-background` | Background color for items in the footer | `"transparent"` |


## Previewing colors

Run the following from the command line to preview the colors defined in the color system:

```bash
textual colors
```

Inside the preview you can change the theme via the Command Palette (++ctrl+p++), and view the base variables and shades generated from the theme.

## Theme reference

Here's a list of the CSS variables generated from themes.
The colors below are from the `textual-light` and `textual-dark` themes.

!!! note

    `$boost` will look different on different backgrounds because of its alpha channel.

```{.rich title="Textual Theme Colors"}
from rich import print
from textual.app import DEFAULT_COLORS
from textual.design import show_design
output = show_design(DEFAULT_COLORS["light"], DEFAULT_COLORS["dark"])
```
