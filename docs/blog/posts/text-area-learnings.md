---
draft: false
date: 2023-09-18
categories:
  - DevLog
authors:
  - darrenburns
---

# Learnings from building Textual's TextArea widget

Working on the `TextArea` widget for Textual taught me that there are many subtle features in my text
editor that I'd been taking for granted.

<!-- more -->

### Vertical cursor movement

When you move the cursor vertically, you can't simply keep the same column index.
Editors should maintain the last visual horizontal offset the user navigated to.

![maintain_offset.gif](../images/text-area-learnings/maintain_offset.gif)

In the clip above, notice how the column offset of the cursor changes as the cursor moves vertically between rows.

```python
from itertools import cycle
from pathlib import Path

from textual import on
from textual._text_area_theme import TextAreaTheme, _BUILTIN_THEMES
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.document._document import Selection
from textual.widgets import Footer, Select, TextArea, DirectoryTree, Static

SAMPLE_TEXT = [
    "Hello, world!",
    "",
    "你好，世界！",  # Chinese characters, which are usually double-width
    "こんにちは、世界！",  # Japanese characters, also usually double-width
    "안녕하세요, 세계!",  # Korean characters, also usually double-width
    "    This line has leading white space",
    "This line has trailing white space    ",
    "    This line has both leading and trailing white space    ",
    "    ",  # Line with only spaces
    "こんにちは、world! 你好，world!",  # Mixed script line
    "Hello, 🌍! Hello, 🌏! Hello, 🌎!",  # Line with emoji (which are often double-width)
    "The quick brown 🦊 jumps over the lazy 🐶.",  # Line with emoji interspersed in text
    "Special characters: ~!@#$%^&*()_+`-={}|[]\\:\";'<>?,./",
    # Line with special characters
    "Unicode example: Привет, мир!",  # Russian text
    "Unicode example: Γειά σου Κόσμε!",  # Greek text
]

YAML = """\
# This is a comment in YAML

# Scalars
string: "Hello, world!"
integer: 42
float: 3.14
boolean: true

# Sequences (Arrays)
fruits:
  - Apple
  - Banana
  - Cherry

# Nested sequences
persons:
  - name: John
    age: 28
    is_student: false
  - name: Jane
    age: 22
    is_student: true

# Mappings (Dictionaries)
address:
  street: 123 Main St
  city: Anytown
  state: CA
  zip: '12345'

# Multiline string
description: |
  This is a multiline
  string in YAML.

# Inline and nested collections
colors: { red: FF0000, green: 00FF00, blue: 0000FF }
"""

SMALL_SAMPLE = "0123\n0123\n0123"

PYTHON_SNIPPET = """\
def render_line(self, y: int) -> Strip:
    '''Render a line of the widget. y is relative to the top of the widget.'''

    row_index = y // 4  # A checkerboard square consists of 4 rows

    if row_index >= 8:  # Generate blank lines when we reach the end
        return Strip.blank(self.size.width)

    is_odd = row_index % 2  # Used to alternate the starting square on each row

    white = Style.parse("on white")  # Get a style object for a white background
    black = Style.parse("on black")  # Get a style object for a black background

    # Generate a list of segments with alternating black and white space characters
    segments = [
        Segment(" " * 8, black if (column + is_odd) % 2 else white)
        for column in range(8)
    ]
    strip = Strip(segments, 8 * 8)
    return strip"""

TOML = """\
# This is a comment in TOML

string = "Hello, world!"
integer = 42
float = 3.14
boolean = true
datetime = 1979-05-27T07:32:00Z

fruits = ["apple", "banana", "cherry"]

[address]
street = "123 Main St"
city = "Anytown"
state = "CA"
zip = "12345"

[person.john]
name = "John Doe"
age = 28
is_student = false


[[animals]]
name = "Fido"
type = "dog"
"""

JSON = """\
{
    "name": "John Doe",
    "age": 30,
    "isStudent": false,
    "address": {
        "street": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "zip": "12345"
    },
    "phoneNumbers": [
        {
            "type": "home",
            "number": "555-555-1234"
        },
        {
            "type": "work",
            "number": "555-555-5678"
        }
    ],
    "hobbies": ["reading", "hiking", "swimming"],
    "pets": [
        {
            "type": "dog",
            "name": "Fido"
        },
    ],
    "graduationYear": null
}
"""

SQL = """\
-- This is a comment in SQL

-- Create tables
CREATE TABLE Authors (
    AuthorID INT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Country VARCHAR(50)
);

CREATE TABLE Books (
    BookID INT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    AuthorID INT,
    PublishedDate DATE,
    FOREIGN KEY (AuthorID) REFERENCES Authors(AuthorID)
);

-- Insert data
INSERT INTO Authors (AuthorID, Name, Country) VALUES (1, 'George Orwell', 'UK');

INSERT INTO Books (BookID, Title, AuthorID, PublishedDate) VALUES (1, '1984', 1, '1949-06-08');

-- Update data
UPDATE Authors SET Country = 'United Kingdom' WHERE Country = 'UK';

-- Select data with JOIN
SELECT Books.Title, Authors.Name
FROM Books
JOIN Authors ON Books.AuthorID = Authors.AuthorID;

-- Delete data (commented to preserve data for other examples)
-- DELETE FROM Books WHERE BookID = 1;

-- Alter table structure
ALTER TABLE Authors ADD COLUMN BirthDate DATE;

-- Create index
CREATE INDEX idx_author_name ON Authors(Name);

-- Drop index (commented to avoid actually dropping it)
-- DROP INDEX idx_author_name ON Authors;

-- End of script
"""


different_width_text = """\
# Hello, world!

# こんにちは、世界！

Here is some text.
"""

class TextAreaDemo(App):
    CSS = """\
    * {
        scrollbar-size-vertical: 1;
    }
    TextArea {
        height: auto;
    }
    #file-tree {
        width: 25%;
    }
    #debug {
        height: auto;
        background: $primary-darken-1 25%;
        padding: 1 2;
    }
    #options {
        dock: bottom;
        align-horizontal: right;
        height: auto;
        margin-bottom: 1;
        width: 40;
    }
    #location-bar {
        color: $text;
        background: $accent;
        padding: 0 3;
    }
    """

    BINDINGS = [
        Binding("ctrl+l", "gutter", "Toggle Gutter"),
        Binding("ctrl+n", "tab_size_cycle", "Cycle Tab Size"),
        Binding("f9", "print_highlights", "Print highlights"),
    ]

    def compose(self) -> ComposeResult:
        code_path = Path("/Users/darrenburns/Code/textual/sandbox/darren/sample.py")
        text = code_path.read_text()

        default_language = "markdown"
        text_area = TextArea(different_width_text, language=default_language, theme="vscode_dark")

        with Horizontal(id="body"):
            yield DirectoryTree(Path(".").resolve(), id="file-tree")
            with Vertical():
                yield text_area
                yield Static(id="location-bar")

        with Horizontal(id="options"):
            yield Select(
                [(lang, lang) for lang in text_area.available_languages],
                value=default_language,
                prompt="Language",
                id="language-select",
            )
            yield Select(
                [(theme, theme) for theme in text_area.available_themes],
                prompt="Theme",
                value="vscode_dark",
                id="theme-select",
            )
        yield Footer()

    def on_mount(self) -> None:
        self.watch(self.query_one(TextArea), "selection", self._update_location)

    def _update_location(self, selection: Selection) -> None:
        text_area = self.query_one(TextArea)
        location_bar = self.query_one("#location-bar", Static)
        row, column = text_area.cursor_location
        location_bar.update(f"column = {column}")

    @on(DirectoryTree.FileSelected)
    def navigate_to_definition(self, event: DirectoryTree.FileSelected) -> None:
        editor = self.query_one(TextArea)
        print("loading text")
        editor.load_text(event.path.read_text())

    @on(Select.Changed, selector="#language-select")
    def update_language(self, event: Select.Changed) -> None:
        language = event.value
        print("language selected")
        editor = self.query_one(TextArea)
        editor.language = language

    @on(Select.Changed, selector="#theme-select")
    def update_theme(self, event: Select.Changed) -> None:
        theme = event.value
        print("theme selected")
        editor = self.query_one(TextArea)
        editor.theme = theme

    def action_gutter(self):
        editor = self.query_one(TextArea)
        editor.show_line_numbers = not editor.show_line_numbers

    tab_sizes = cycle([2, 4, 8])

    def action_tab_size_cycle(self):
        editor = self.query_one(TextArea)
        editor.indent_width = next(self.tab_sizes)

    def action_print_highlights(self) -> None:
        area = self.query_one(TextArea)
        print(area._highlights)


app = TextAreaDemo()
if __name__ == "__main__":
    app.run()

```
