# TextArea

!!! tip "Added in version 0.38.0"

A widget for editing text which may span multiple lines.
Supports syntax highlighting for a selection of languages.

- [x] Focusable
- [ ] Container


## Guide

### Loading text

In this example we load some initial text into the `TextArea`, and set the language to `"python"` to enable syntax highlighting.

=== "Output"

    ```{.textual path="docs/examples/widgets/text_area.py" columns="42" lines="8"}
    ```

=== "text_area_example.py"

    ```python
    --8<-- "docs/examples/widgets/text_area.py"
    ```

To load content into the `TextArea` after it has already been created,
use the [`load_text`][textual.widgets._text_area.TextArea.load_text] method.

To update the parser used for syntax highlighting, set the [`language`][textual.widgets._text_area.TextArea.language] reactive attribute:

```python
# Set the language to Markdown
text_area.language = "markdown"
```

### Working with the cursor

The cursor location is available via the `cursor_location` attribute.
Writing a new value to `cursor_location` will immediately update the location of the cursor.

```python
>>> text_area = TextArea()
>>> text_area.cursor_location
(0, 0)
>>> text_area.cursor_location = (0, 4)
>>> text_area.cursor_location
(0, 4)
```

`cursor_location` is the easiest way to move the cursor programmatically, but it doesn't
allow us to select text. To select text, we can use the `selection` reactive attribute.

Let's select the first two lines of text in a document by adding `text_area.selection = Selection(start=(0, 0), end=(2, 0))`
to our code:

=== "Output"

    ```{.textual path="docs/examples/widgets/text_area_selection.py" columns="42" lines="8"}
    ```

=== "text_area_selection.py"

    ```python
    --8<-- "docs/examples/widgets/text_area_selection.py"
    ```

    1. Selects the first two lines of text.

Note that selections can happen in both directions. That is, `Selection((2, 0), (0, 0))` is also valid.

!!! tip

    The `end` attribute of the `selection` is always equal to `TextArea.cursor_location`. In other words,
    the `cursor_location` attribute is simply a convenience for accessing `text_area.selection.end`.


### Reading content from `TextArea`

You can access the text inside the `TextArea` via the [`text`][textual.widgets._text_area.TextArea.text] property.

### Editing content inside `TextArea`

The content of the `TextArea` can be updated using the [`replace`][textual.widgets._text_area.TextArea.replace] method.
This method is the programmatic equivalent of selecting some text and then pasting.

All atomic (single-cursor) edits can be represented by a `replace` operation, but for
convenience, some other utility methods are provided, such as [`insert`][textual.widgets._text_area.TextArea.insert], [`delete`][textual.widgets._text_area.TextArea.delete], and [`clear`][textual.widgets._text_area.TextArea.clear].

### Themes

`TextArea` ships with some builtin themes, and you can easily add your own.

Themes give you control over the look and feel, including syntax highlighting,
the cursor, the selection, and gutter, and more.

#### Using builtin themes

The initial theme of the `TextArea` is determined by the `theme` parameter.

```python
# Create a TextArea with the 'dracula' theme.
yield TextArea("print(123)", language="python", theme="dracula")
```

You can check which themes are available using the [`available_themes`][textual.widgets._text_area.TextArea.available_themes] property.

```python
>>> text_area = TextArea()
>>> print(text_area.available_themes)
{'dracula', 'github_light', 'monokai', 'vscode_dark'}
```

After creating a `TextArea`, you can change the theme by setting the [`theme`][textual.widgets._text_area.TextArea.theme]
attribute to one of the available themes.

```python
text_area.theme = "vscode_dark"
```

On setting this attribute the `TextArea` will immediately refresh to display the updated theme.

#### Custom themes

Using custom (non-builtin) themes is two-step process:

1. Create an instance of [`TextAreaTheme`][textual.widgets.text_area.TextAreaTheme].
2. Register it using [`TextArea.register_theme`][textual.widgets._text_area.TextArea.register_theme].

##### 1. Creating a theme

Let's create a simple theme, `"my_cool_theme"`, which colors the cursor <span style="background-color: dodgerblue; color: white; padding: 0 2px;">blue</span>, and the cursor line <span style="background-color: yellow; color: black; padding: 0 2px;">yellow</span>.
Our theme will also syntax highlight strings as <span style="background-color: red; color: white; padding: 0 2px;">red</span>, and comments as <span style="background-color: magenta; color: black; padding: 0 2px;">magenta</span>.

```python
from rich.style import Style
from textual.widgets.text_area import TextAreaTheme
# ...
my_theme = TextAreaTheme(
    # This name will be used to refer to the theme...
    name="my_cool_theme",
    # Basic styles such as background, cursor, selection, gutter, etc...
    cursor_style=Style(color="white", bgcolor="blue"),
    cursor_line_style=Style(bgcolor="yellow"),
    # `token_styles` is for syntax highlighting.
    # It maps tokens parsed from the document to Rich styles.
    token_styles={
        "string": Style(color="red"),
        "comment": Style(color="magenta"),
    }
)
```

The `token_styles` attribute of `TextAreaTheme` is used for syntax highlighting.
For more details, see [syntax highlighting](#syntax-highlighting).

##### 2. Registering a theme

With our theme created, we can now register it with the `TextArea` instance.

```python
text_area.register_theme(my_theme)
```

After registering a theme, it'll appear in the `available_themes`:

```python
>>> print(text_area.available_themes)
{'dracula', 'github_light', 'monokai', 'vscode_dark', 'my_cool_theme'}
```

We can now switch to this theme:

```python
text_area.theme = "my_cool_theme"
```

Which immediately updates the appearance of our `TextArea`:

```{.textual path="docs/examples/widgets/text_area_custom_theme.py" columns="42" lines="8"}
```

### Advanced concepts

#### Syntax highlighting

Syntax highlighting inside the `TextArea` is powered by a library called [`tree-sitter`](https://tree-sitter.github.io/tree-sitter/).

Each time you update the document in a `TextArea`, an internal syntax tree is updated.
This tree is frequently _queried_ to find location ranges relevant to syntax highlighting.
We give these ranges _names_, and ultimately map them to Rich styles inside `TextAreaTheme.token_styles`.

Let's use the `markdown` language to illustrate how this works.

When the `language` attribute is set to `"markdown"`, a highlight query similar to the one below is used (trimmed for brevity).

```scheme
(heading_content) @heading
(link) @link
```

This highlight query maps `heading_content` nodes returned by the Markdown tree-sitter parser to the name `"heading"`,
and `link` nodes to the name `link`.

Inside our `TextAreaTheme.token_styles` dict, we can map the name `"heading"` to a Rich style.
Here's a snippet from the "Monokai" theme which does just that:

```python
TextAreaTheme(
    name="monokai",
    base_style=Style(color="#f8f8f2", bgcolor="#272822"),
    gutter_style=Style(color="#90908a", bgcolor="#272822"),
    # ...
    token_styles={
        # Colorise headings and make them bold
        "heading": Style(color="#F92672", bold=True),
        # Colorise and underline Markdown links
        "link": Style(color="#66D9EF", underline=True),
        # ...
    },
)
```

The exact queries `TextArea` uses for highlighting can be found inside `.scm` files in the GitHub repo.

#### Adding support for custom languages

To add support for a language to a `TextArea`, use the [`register_language`][textual.widgets._text_area.TextArea.register_language] method.

[`py-tree-sitter-languages`](https://github.com/grantjenks/py-tree-sitter-languages)

!!! note
    More built-in languages will be added in the future.


## Reactive attributes

| Name                   | Type                     | Default            | Description                                      |
|------------------------|--------------------------|--------------------|--------------------------------------------------|
| `language`             | `str | None`             | `None`               | The language to use for syntax highlighting.     |
| `theme`                | `str | None`             | `TextAreaTheme.default()` | The theme to use for syntax highlighting.         |
| `selection`            | `Selection`              | `Selection()`      | The current selection.                           |
| `show_line_numbers`    | `bool`                   | `True`             | Show or hide line numbers.                       |
| `indent_width`         | `int`                    | `4`                | The number of spaces to indent and width of tabs. |
| `match_cursor_bracket` | `bool`                   | `True`            | Enable/disable highlighting matching brackets under cursor. |
| `cursor_blink`         | `bool`                   | `True`            | Enable/disable blinking of the cursor when the widget has focus. |

## Bindings

The `TextArea` widget defines the following bindings:

::: textual.widgets._text_area.TextArea.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false


## Component classes

The `TextArea` widget defines no component classes.

Styling should be done exclusively via [`TextAreaTheme`][textual.widgets.text_area.TextAreaTheme].

## Additional notes

### Indentation

The character(s) inserted when you press tab is controlled by setting the `indent_type` attribute to either `tabs` or `spaces`.

If `indent_type == "spaces"`, pressing ++tab++ will insert `indent_width` spaces.

### Line separators

When content is loaded into `TextArea`, the content is scanned from beginning to end
and the first occurrence of a line separator is recorded.

This separator will then be used when content is later read from the `TextArea` via
the `text` property. The `TextArea` widget does not support exporting text which
contains mixed line endings.

Similarly, newline characters pasted into the `TextArea` will be converted.

You can check the line separator of the current document by inspecting `TextArea.document.newline`:

```python
>>> text_area = TextArea()
>>> text_area.document.newline
'\n'
```

### The gutter and line numbers

The gutter (column on the left containing line numbers) can be toggled by setting
the `show_line_numbers` attribute to `True` or `False`.

Setting this attribute will immediately repaint the `TextArea` to reflect the new value.

## See also

- [`Input`][textual.widgets.Input] - for single-line text input.
- [`TextAreaTheme`][textual.widgets.text_area.TextAreaTheme] - for theming the `TextArea`.

---

::: textual.widgets._text_area.TextArea
    options:
      heading_level: 2

---

::: textual.widgets.text_area
    options:
      heading_level: 2
