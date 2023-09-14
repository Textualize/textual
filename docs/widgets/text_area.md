
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

    ```{.textual path="docs/examples/widgets/text_area_example.py" columns="42" lines="8"}
    ```

=== "text_area_example.py"

    ```python
    --8<-- "docs/examples/widgets/text_area_example.py"
    ```

To load content into the `TextArea` after it has already been created,
use the [`load_text`][textual.widgets._text_area.TextArea.load_text] method.

To update the parser used for syntax highlighting, set the [`language`][textual.widgets._text_area.TextArea.language] reactive attribute:

```python
# Set the language to Markdown
text_area.language = "markdown"
```

!!! note
    Syntax highlighting is unavailable on Apple Silicon machines running Python 3.7.

!!! note
    More built-in languages will be added in the future. For now, you can [add your own](#adding-support-for-custom-languages).


### Reading content from `TextArea`

There are a number of ways to retrieve content from the `TextArea`:

- The [`TextArea.text`][textual.widgets._text_area.TextArea.text] property returns all content in the text area as a string.
- The [`TextArea.selected_text`][textual.widgets._text_area.TextArea.selected_text] property returns the text corresponding to the current selection.
- The [`TextArea.get_text_range`][textual.widgets._text_area.TextArea.get_text_range] method returns the text between two locations.

In all cases, when multiple lines of text are retrieved, the [document line separator](#line-separators) will be used.

### Editing content inside `TextArea`

The content of the `TextArea` can be updated using the [`replace`][textual.widgets._text_area.TextArea.replace] method.
This method is the programmatic equivalent of selecting some text and then pasting.

All atomic (single-cursor) edits can be represented by a `replace` operation, but for
convenience, some other utility methods are provided, such as [`insert`][textual.widgets._text_area.TextArea.insert], [`delete`][textual.widgets._text_area.TextArea.delete], and [`clear`][textual.widgets._text_area.TextArea.clear].

### Working with the cursor

#### Moving the cursor

The cursor location is available via the [`cursor_location`][textual.widgets._text_area.TextArea.cursor_location] property, which represents
the location of the cursor as a tuple `(row_index, column_index)`. These indices are zero-based.
Writing a new value to `cursor_location` will immediately update the location of the cursor.

```python
>>> text_area = TextArea()
>>> text_area.cursor_location
(0, 0)
>>> text_area.cursor_location = (0, 4)
>>> text_area.cursor_location
(0, 4)
```

`cursor_location` is a simple way to move the cursor programmatically, but it doesn't let us select text.

#### Selecting text

To select text, we can use the `selection` reactive attribute.
Let's select the first two lines of text in a document by adding `text_area.selection = Selection(start=(0, 0), end=(2, 0))` to our code:

=== "Output"

    ```{.textual path="docs/examples/widgets/text_area_selection.py" columns="42" lines="8"}
    ```

=== "text_area_selection.py"

    ```python hl_lines="17"
    --8<-- "docs/examples/widgets/text_area_selection.py"
    ```

    1. Selects the first two lines of text.

Note that selections can happen in both directions. That is, `Selection((2, 0), (0, 0))` is also valid.

!!! tip

    The `end` attribute of the `selection` is always equal to `TextArea.cursor_location`. In other words,
    the `cursor_location` attribute is simply a convenience for accessing `text_area.selection.end`.

#### More cursor utilities

There are a number of additional utility methods available for interacting with the cursor.

##### Location information

A number of properties exist on `TextArea` which give information about the current cursor location.
These properties begin with `cursor_at_`, and return booleans.
For example, [`cursor_at_start_of_line`][textual.widgets._text_area.TextArea.cursor_at_start_of_line] tells us if the cursor is at a start of line.

We can also check the location the cursor _would_ arrive at if we were to move it.
For example, [`get_cursor_right_location`][textual.widgets._text_area.TextArea.get_cursor_right_location] returns the location
the cursor would move to if it were to move right.
A number of similar methods exist, with names like `get_cursor_*_location`.

##### Cursor movement methods

The [`move_cursor`][textual.widgets._text_area.TextArea.move_cursor] method allows you to move the cursor to a new location while selecting
text, or move the cursor and scroll to keep it centered.

```python
# Move the cursor from its current location to row index 4,
# column index 8, while selecting all the text between.
text_area.move_cursor((4, 8), select=True)
```

The [`move_cursor_relative`][textual.widgets._text_area.TextArea.move_cursor_relative] method offers a very similar interface, but moves the cursor relative
to its current location.

##### Common selections

There are some methods available which make common selections easier:

- [`select_line`][textual.widgets._text_area.TextArea.select_line] selects a line by index. Bound to ++f6++ by default.
- [`select_all`][textual.widgets._text_area.TextArea.select_all] selects all text. Bound to ++f7++ by default.

### Themes

`TextArea` ships with some builtin themes, and you can easily add your own.

Themes give you control over the look and feel, including syntax highlighting,
the cursor, selection, gutter, and more.

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
    # `syntax_styles` is for syntax highlighting.
    # It maps tokens parsed from the document to Rich styles.
    syntax_styles={
        "string": Style(color="red"),
        "comment": Style(color="magenta"),
    }
)
```

Attributes like `cursor_style` and `cursor_line_style` apply general language-agnostic
styling to the widget.

The `syntax_styles` attribute of `TextAreaTheme` is used for syntax highlighting and
depends on the `language` currently in use.
For more details, see [syntax highlighting](#syntax-highlighting).

If you wish to build on an existing theme, you can obtain a reference to it using the [`TextAreaTheme.get_builtin_theme`][textual.widgets.text_area.TextAreaTheme.get_builtin_theme] classmethod:

```python
from textual.widgets.text_area import TextAreaTheme

monokai = TextAreaTheme.get_builtin_theme("monokai")
```

##### 2. Registering a theme

Our theme can now be registered with the `TextArea` instance.

```python
text_area.register_theme(my_theme)
```

After registering a theme, it'll appear in the `available_themes`:

```python
>>> print(text_area.available_themes)
{'dracula', 'github_light', 'monokai', 'vscode_dark', 'my_cool_theme'}
```

We can now switch to it:

```python
text_area.theme = "my_cool_theme"
```

This immediately updates the appearance of the `TextArea`:

```{.textual path="docs/examples/widgets/text_area_custom_theme.py" columns="42" lines="8"}
```

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

### Line numbers

The gutter (column on the left containing line numbers) can be toggled by setting
the `show_line_numbers` attribute to `True` or `False`.

Setting this attribute will immediately repaint the `TextArea` to reflect the new value.

### Advanced concepts

#### Syntax highlighting

Syntax highlighting inside the `TextArea` is powered by a library called [`tree-sitter`](https://tree-sitter.github.io/tree-sitter/).

Each time you update the document in a `TextArea`, an internal syntax tree is updated.
This tree is frequently _queried_ to find location ranges relevant to syntax highlighting.
We give these ranges _names_, and ultimately map them to Rich styles inside `TextAreaTheme.syntax_styles`.

To illustrate how this works, lets look at how the "Monokai" `TextAreaTheme` highlights Markdown files.

When the `language` attribute is set to `"markdown"`, a highlight query similar to the one below is used (trimmed for brevity).

```scheme
(heading_content) @heading
(link) @link
```

This highlight query maps `heading_content` nodes returned by the Markdown parser to the name `@heading`,
and `link` nodes to the name `@link`.

Inside our `TextAreaTheme.syntax_styles` dict, we can map the name `@heading` to a Rich style.
Here's a snippet from the "Monokai" theme which does just that:

```python
TextAreaTheme(
    name="monokai",
    base_style=Style(color="#f8f8f2", bgcolor="#272822"),
    gutter_style=Style(color="#90908a", bgcolor="#272822"),
    # ...
    syntax_styles={
        # Colorise @heading and make them bold
        "heading": Style(color="#F92672", bold=True),
        # Colorise and underline @link
        "link": Style(color="#66D9EF", underline=True),
        # ...
    },
)
```

To understand which names can be mapped inside `syntax_styles`, we recommend looking at the existing
themes and highlighting queries (`.scm` files) in the Textual repository.

!!! tip

    You may also wish to take a look at the contents of `TextArea._highlights` on an
    active `TextArea` instance to see which highlights have been generated for the
    open document.

#### Adding support for custom languages

To add support for a language to a `TextArea`, use the [`register_language`][textual.widgets._text_area.TextArea.register_language] method.

To register a language, we require two things:

1. A tree-sitter `Language` object which contains the grammar for the language.
2. A highlight query which is used for [syntax highlighting](#syntax-highlighting).

##### Example - adding Java support

The easiest way to obtain a `Language` object is using the [`py-tree-sitter-languages`](https://github.com/grantjenks/py-tree-sitter-languages) package. Here's how we can use this package to obtain a reference to a `Language` object representing Java:

```python
from tree_sitter_languages import get_language
java_language = get_language("java")
```

!!! note

    `py-tree-sitter-languages` may not be available on some architectures (e.g. Macbooks with Apple Silicon running Python 3.7).

The exact version of the parser used when you call `get_language` can be checked via
the [`repos.txt` file](https://github.com/grantjenks/py-tree-sitter-languages/blob/a6d4f7c903bf647be1bdcfa504df967d13e40427/repos.txt) in
the version of `py-tree-sitter-languages` you're using. This file contains links to the GitHub
repos and commit hashes of the tree-sitter parsers. In these repos you can often find pre-made highlight queries at `queries/highlights.scm`,
and a file showing all the available node types which can be used in highlight queries at `src/node-types.json`.

Since we're adding support for Java, lets grab the Java highlight query from the repo by following these steps:

1. Open [`repos.txt` file](https://github.com/grantjenks/py-tree-sitter-languages/blob/a6d4f7c903bf647be1bdcfa504df967d13e40427/repos.txt) from the `py-tree-sitter-languages` repo.
2. Find the link corresponding to `tree-sitter-java` and go to the repo on GitHub (you may also need to go to the specific commit referenced in `repos.txt`).
3. Go to [`queries/highlights.scm`](https://github.com/tree-sitter/tree-sitter-java/blob/ac14b4b1884102839455d32543ab6d53ae089ab7/queries/highlights.scm) to see the example highlight query for Java.

Be sure to check the license in the repo to ensure it can be freely copied.

!!! warning

    It's important to use a highlight query which is compatible with the parser in use, so
    pay attention to the commit hash when visiting the repo via `repos.txt`.

We now have our `Language` and our highlight query, so we can register Java as a language.

```python
--8<-- "docs/examples/widgets/text_area_custom_language.py"
```

Running our app, we can see that the Java code is highlighted.
We can freely edit the text, and the syntax highlighting will update immediately.

```{.textual path="docs/examples/widgets/text_area_custom_language.py" columns="52" lines="8"}
```

Recall that we map names (like `@heading`) from the tree-sitter highlight query to Rich style objects inside the `TextAreaTheme.syntax_styles` dictionary.
If you notice some highlights are missing after registering a language, the issue may be:

1. The current `TextAreaTheme` doesn't contain a mapping for the name in the highlight query. Adding a new to `syntax_styles` should resolve the issue.
2. The highlight query doesn't assign a name to the pattern you expect to be highlighted. In this case you'll need to update the highlight query to assign to the name.

!!! tip

    The names assigned in tree-sitter highlight queries are often reused across multiple languages.
    For example, `@string` is used in many languages to highlight strings.

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

## See also

- [`Input`][textual.widgets.Input] - for single-line text input.
- [`TextAreaTheme`][textual.widgets.text_area.TextAreaTheme] - for theming the `TextArea`.
- The tree-sitter documentation [website](https://tree-sitter.github.io/tree-sitter/).
- The tree-sitter Python bindings [repository](https://github.com/tree-sitter/py-tree-sitter).
- `py-tree-sitter-languages` [repository](https://github.com/grantjenks/py-tree-sitter-languages) (provides binary wheels for a large variety of tree-sitter languages).

---

::: textual.widgets._text_area.TextArea
    options:
      heading_level: 2

---

::: textual.widgets.text_area
    options:
      heading_level: 2
