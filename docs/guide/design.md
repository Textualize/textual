# Themes

Textual comes with several built-in *themes*, and it's easy to create your own.
A theme provides variables which can be used in the CSS of your app.
Click on the tabs below to see how themes can change the appearance of an app.

=== "nord"

    ```{.textual path="docs/examples/themes/todo_app.py"}
    ```

=== "gruvbox"

    ```{.textual path="docs/examples/themes/todo_app.py" press="ctrl+t"}
    ```

=== "tokyo-night"

    ```{.textual path="docs/examples/themes/todo_app.py" press="ctrl+t,ctrl+t"}
    ```

=== "textual-dark"

    ```{.textual path="docs/examples/themes/todo_app.py" press="ctrl+t,ctrl+t,ctrl+t"}
    ```

=== "solarized-light"

    ```{.textual path="docs/examples/themes/todo_app.py" press="ctrl+t,ctrl+t,ctrl+t,ctrl+t"}
    ```

## Changing the theme

The theme can be changed at runtime via the [Command Palette](./command_palette.md) (++ctrl+p++).

You can also programmatically change the theme by setting the value of `App.theme` to the name of a theme:

```python
class MyApp(App):
    def on_mount(self) -> None:
        self.theme = "nord"
```

A theme must be *registered* before it can be used.
Textual comes with a selection of built-in themes which are registered by default.

## Registering a theme

A theme is a simple Python object which maps variable names to colors.
Here's an example:

```python
from textual.theme import Theme

arctic_theme = Theme(
    name="arctic",
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

You can register this theme by calling `App.register_theme` in the `on_mount` method of your `App`.

```python
from textual.app import App

class MyApp(App):
    def on_mount(self) -> None:
        # Register the theme
        self.register_theme(arctic_theme)  # (1)!

        # Set the app's theme
        self.theme = "arctic"  # (2)!
```

1. Register the theme, making it available to the app (and command palette)
2. Set the app's theme. When this line runs, the app immediately refreshes to use the new theme.

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

On changing the theme, the values stored in these variables are updated to match the new theme, and the colors of `MyWidget` are updated accordingly.

## Base colors

When defining a theme, only the `primary` color is required.
Textual will attempt to generate the other base colors if they're not supplied.

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
| `$warning`              | Indicates a warning. Typically used as a background color. `$text-warning` can be used for foreground.                                                                                                            |
| `$error`                | Indicates an error. Typically used as a background color. `$text-error` can be used for foreground.                                                                                                             |
| `$success`              | Used to indicate success. Typically used as a background color. `$text-success` can be used for foreground.                                                                                                      |
| `$accent`               | Used sparingly to draw attention. Typically contrasts with `$primary` and `$secondary`.                                                                 |

## Shades

For every color, Textual generates 3 dark shades and 3 light shades.

- Add `-lighten-1`, `-lighten-2`, or `-lighten-3` to the color's variable name to get lighter shades (3 is the lightest).
- Add `-darken-1`, `-darken-2`, and `-darken-3` to a color to get the darker shades (3 is the darkest).

For example, `$secondary-darken-1` is a slightly darkened `$secondary`, and `$error-lighten-3` is a very light version of the `$error` color.

## Light and dark themes

Themes can be either *light* or *dark*.
This setting is specified in the `Theme` constructor via the `dark` argument, and influences how Textual
generates variables.
Built-in widgets may also use the value of `dark` to influence their appearance.

## Text color

The default color of text in a theme is `$foreground`.
This color should be legible on `$background`, `$surface`, and `$panel` backgrounds.

There is also `$foreground-muted` for text which has lower importance.
`$foreground-disabled` can be used for text which is disabled, for example a menu item which can't be selected.

You can set the text color via the [color](../styles/color.md) CSS property.

The available text colors are:

- `$text-primary`
- `$text-secondary`
- `$text-accent`
- `$text-warning`
- `$text-error`
- `$text-success`

### Ensuring text legibility

In some cases, the background color of a widget is unpredictable, so we cannot be certain our text will be readable against it.

The theme system defines three CSS variables which you can use to ensure that text is legible on any background.

- `$text` is set to a slightly transparent black or white, depending on which has better contrast against the background the text is on.
- `$text-muted` sets a slightly faded text color. Use this for text which has lower importance. For instance a sub-title or supplementary information.
- `$text-disabled` sets faded out text which indicates it has been disabled. For instance, menu items which are not applicable and can't be clicked.

### Colored text

Colored text is also generated from the base colors, which is guaranteed to be legible against a background of `$background`, `$surface`, and `$panel`.
For example, `$text-primary` is a version of the `$primary` color tinted to ensure legibility.

=== "Output (Theme: textual-dark)"

    ```{.textual path="docs/examples/themes/colored_text.py" lines="9" columns="30"}
    ```

=== "colored_text.py"

    ```python title="colored_text.py"
    --8<-- "docs/examples/themes/colored_text.py"
    ```

These colors are also be guaranteed to be legible when used as the foreground color of a widget with a *muted color* background.

## Muted colors

Muted colors are generated from the base colors by blending them with `$background` at 70% opacity.
For example, `$primary-muted` is a muted version of the `$primary` color.

Textual aims to ensure that the colored text it generates is legible against the corresponding muted color.
In other words, `$text-primary` text should be legible against a background of `$primary-muted`:

=== "Output (Theme: textual-dark)"

    ```{.textual path="docs/examples/themes/muted_backgrounds.py" lines="9" columns="40"}
    ```

=== "muted_backgrounds.py"

    ```python title="muted_backgrounds.py"
    --8<-- "docs/examples/themes/muted_backgrounds.py"
    ```

The available muted colors are:

- `$primary-muted`
- `$secondary-muted`
- `$accent-muted`
- `$warning-muted`
- `$error-muted`
- `$success-muted`

## Additional variables

Textual uses the base colors as default values for additional variables used throughout the framework.
These variables can be overridden by passing a `variables` argument to the `Theme` constructor.
This also allows you to override variables such as `$primary-muted`, described above.

In the Gruvbox theme, for example, we override the foreground color of the block cursor (the cursor used in widgets like `OptionList`) to be `$foreground`.

```python hl_lines="14-17"
Theme(
    name="gruvbox",
    primary="#85A598",
    secondary="#A89A85",
    warning="#fabd2f",
    error="#fb4934",
    success="#b8bb26",
    accent="#fabd2f",
    foreground="#fbf1c7",
    background="#282828",
    surface="#3c3836",
    panel="#504945",
    dark=True,
    variables={
        "block-cursor-foreground": "#fbf1c7",
        "input-selection-background": "#689d6a40",
    },
)
```

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

### Button

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `$button-foreground` | Foreground color for standard buttons | `$foreground` |
| `$button-color-foreground` | Foreground color for colored buttons | `$text` |
| `$button-focus-text-style` | Text style for focused buttons | `"bold reverse"` |

## App-specific variables

The variables above are defined and used by Textual itself.
However, you may also wish to expose other variables which are specific to your application.

You can do this by overriding `App.get_theme_variable_defaults` in your `App` subclass.

This method should return a dictionary of variable names and their default values.
If a variable defined in this dictionary is also defined in a theme's `variables` dictionary, the theme's value will be used.

## Previewing colors

Run the following from the command line to preview the colors defined in the color system:

```bash
textual colors
```

Inside the preview you can change the theme via the Command Palette (++ctrl+p++), and view the base variables and shades generated from the theme.
