PYTHON = """\
import math
from os import path

# I'm a comment :)

string_var = "Hello, world!"
int_var = 42
float_var = 3.14
complex_var = 1 + 2j

list_var = [1, 2, 3, 4, 5]
tuple_var = (1, 2, 3, 4, 5)
set_var = {1, 2, 3, 4, 5}
dict_var = {"a": 1, "b": 2, "c": 3}

def function_no_args():
    return "No arguments"

def function_with_args(a, b):
    return a + b

def function_with_default_args(a=0, b=0):
    return a * b

lambda_func = lambda x: x**2

if int_var == 42:
    print("It's the answer!")
elif int_var < 42:
    print("Less than the answer.")
else:
    print("Greater than the answer.")

for index, value in enumerate(list_var):
    print(f"Index: {index}, Value: {value}")

counter = 0
while counter < 5:
    print(f"Counter value: {counter}")
    counter += 1

squared_numbers = [x**2 for x in range(10) if x % 2 == 0]

try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
finally:
    print("End of try-except block.")

class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        raise NotImplementedError("Subclasses must implement this method.")

class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

for num in fibonacci(5):
    print(num)

with open('test.txt', 'w') as f:
    f.write("Testing with statement.")

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
"""


MARKDOWN = """\
Heading
=======

Sub-heading
-----------

### Heading

#### H4 Heading

##### H5 Heading

###### H6 Heading


Paragraphs are separated
by a blank line.

Two spaces at the end of a line  
produces a line break.

Text attributes _italic_, 
**bold**, `monospace`.

Horizontal rule:

---

Bullet list:

  * apples
  * oranges
  * pears

Numbered list:

  1. lather
  2. rinse
  3. repeat

An [example](http://example.com).

> Markdown uses email-style > characters for blockquoting.
>
> Lorem ipsum

![progress](https://github.com/textualize/rich/raw/master/imgs/progress.gif)


```
a=1
```

```python
import this
```

```somelang
foobar
```

    import this


1. List item

       Code block
"""

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

CSS = """\
/* This is a comment in CSS */

/* Basic selectors and properties */
body {
    font-family: Arial, sans-serif;
    background-color: #f4f4f4;
    margin: 0;
    padding: 0;
}

/* Class and ID selectors */
.header {
    background-color: #333;
    color: #fff;
    padding: 10px 0;
    text-align: center;
}

#logo {
    font-size: 24px;
    font-weight: bold;
}

/* Descendant and child selectors */
.nav ul {
    list-style-type: none;
    padding: 0;
}

.nav > li {
    display: inline-block;
    margin-right: 10px;
}

/* Pseudo-classes */
a:hover {
    text-decoration: underline;
}

input:focus {
    border-color: #007BFF;
}

/* Media query */
@media (max-width: 768px) {
    body {
        font-size: 16px;
    }
    
    .header {
        padding: 5px 0;
    }
}

/* Keyframes animation */
@keyframes slideIn {
    from {
        transform: translateX(-100%);
    }
    to {
        transform: translateX(0);
    }
}

.slide-in-element {
    animation: slideIn 0.5s forwards;
}
"""

HTML = """\
<!DOCTYPE html>
<html lang="en">

<head>
    <!-- Meta tags -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Title -->
    <title>HTML Test Page</title>
    <!-- Link to CSS -->
    <link rel="stylesheet" href="styles.css">
</head>

<body>
    <!-- Header section -->
    <header class="header">
        <h1 id="logo">HTML Test Page</h1>
    </header>

    <!-- Navigation -->
    <nav class="nav">
        <ul>
            <li><a href="#">Home</a></li>
            <li><a href="#">About</a></li>
            <li><a href="#">Contact</a></li>
        </ul>
    </nav>

    <!-- Main content area -->
    <main>
        <article>
            <h2>Welcome to the Test Page</h2>
            <p>This is a paragraph to test the HTML structure.</p>
            <img src="test-image.jpg" alt="Test Image" width="300">
        </article>
    </main>

    <!-- Form -->
    <section>
        <form action="/submit" method="post">
            <label for="name">Name:</label>
            <input type="text" id="name" name="name">
            <input type="submit" value="Submit">
        </form>
    </section>

    <!-- Footer -->
    <footer>
        <p>&copy; 2023 HTML Test Page</p>
    </footer>

    <!-- Script tag -->
    <script src="scripts.js"></script>
</body>

</html>
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

REGEX = r"""^abc            # Matches any string that starts with "abc"
abc$            # Matches any string that ends with "abc"
^abc$           # Matches the string "abc" and nothing else
a.b             # Matches any string containing "a", any character, then "b"
a[.]b           # Matches the string "a.b"
a|b             # Matches either "a" or "b"
a{2}            # Matches "aa"
a{2,}           # Matches two or more consecutive "a" characters
a{2,5}          # Matches between 2 and 5 consecutive "a" characters
a?              # Matches "a" or nothing (0 or 1 occurrence of "a")
a*              # Matches zero or more consecutive "a" characters
a+              # Matches one or more consecutive "a" characters
\d              # Matches any digit (equivalent to [0-9])
\D              # Matches any non-digit
\w              # Matches any word character (equivalent to [a-zA-Z0-9_])
\W              # Matches any non-word character
\s              # Matches any whitespace character (spaces, tabs, line breaks)
\S              # Matches any non-whitespace character
(?i)abc         # Case-insensitive match for "abc"
(?:a|b)         # Non-capturing group for either "a" or "b"
(?<=a)b         # Positive lookbehind: matches "b" that is preceded by "a"
(?<!a)b         # Negative lookbehind: matches "b" that is not preceded by "a"
a(?=b)          # Positive lookahead: matches "a" that is followed by "b"
a(?!b)          # Negative lookahead: matches "a" that is not followed by "b"
"""

GO = """\
package main

import (
    "fmt"
    "math"
    "strings"
)

const PI = 3.14159

type Shape interface {
    Area() float64
}

type Circle struct {
    Radius float64
}

func (c Circle) Area() float64 {
    return PI * c.Radius * c.Radius
}

func main() {
    var name string = "John"
    age := 30
    isStudent := true

    fmt.Printf("Hello, %s! You are %d years old.\n", name, age)

    if age >= 18 && isStudent {
        fmt.Println("You are an adult student.")
    } else if age >= 18 {
        fmt.Println("You are an adult.")
    } else {
        fmt.Println("You are a minor.")
    }

    numbers := []int{1, 2, 3, 4, 5}
    sum := 0
    for _, num := range numbers {
        sum += num
    }
    fmt.Printf("The sum is: %d\n", sum)

    message := "Hello, World!"
    uppercaseMessage := strings.ToUpper(message)
    fmt.Println(uppercaseMessage)

    circle := Circle{Radius: 5}
    fmt.Printf("Circle area: %.2f\n", circle.Area())

    result := factorial(5)
    fmt.Printf("Factorial of 5: %d\n", result)

    defer fmt.Println("Program finished.")

    sqrt := func(x float64) float64 {
        return math.Sqrt(x)
    }
    fmt.Printf("Square root of 16: %.2f\n", sqrt(16))
}

func factorial(n int) int {
    if n == 0 {
        return 1
    }
    return n * factorial(n-1)
}
"""

SNIPPETS = {
    "python": PYTHON,
    "markdown": MARKDOWN,
    "yaml": YAML,
    "toml": TOML,
    "sql": SQL,
    "css": CSS,
    "html": HTML,
    "json": JSON,
    "regex": REGEX,
    "go": GO,
}
