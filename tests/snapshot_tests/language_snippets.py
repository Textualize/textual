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

    fmt.Printf("Hello, %s! You are %d years old.", name, age)

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
    fmt.Printf("The sum is: %d", sum)

    message := "Hello, World!"
    uppercaseMessage := strings.ToUpper(message)
    fmt.Println(uppercaseMessage)

    circle := Circle{Radius: 5}
    fmt.Printf("Circle area: %.2f", circle.Area())

    result := factorial(5)
    fmt.Printf("Factorial of 5: %d", result)

    defer fmt.Println("Program finished.")

    sqrt := func(x float64) float64 {
        return math.Sqrt(x)
    }
    fmt.Printf("Square root of 16: %.2f", sqrt(16))
}

func factorial(n int) int {
    if n == 0 {
        return 1
    }
    return n * factorial(n-1)
}
"""

JAVASCRIPT = """\
// Variable declarations
const name = "John";
let age = 30;
var isStudent = true;

// Template literals
console.log(`Hello, ${name}! You are ${age} years old.`);

// Conditional statements
if (age >= 18 && isStudent) {
  console.log("You are an adult student.");
} else if (age >= 18) {
  console.log("You are an adult.");
} else {
  console.log("You are a minor.");
}

// Arrays and array methods
const numbers = [1, 2, 3, 4, 5];
const doubledNumbers = numbers.map((num) => num * 2);
console.log("Doubled numbers:", doubledNumbers);

// Objects
const person = {
  firstName: "John",
  lastName: "Doe",
  getFullName() {
    return `${this.firstName} ${this.lastName}`;
  },
};
console.log("Full name:", person.getFullName());

// Classes
class Rectangle {
  constructor(width, height) {
    this.width = width;
    this.height = height;
  }

  getArea() {
    return this.width * this.height;
  }
}
const rectangle = new Rectangle(5, 3);
console.log("Rectangle area:", rectangle.getArea());

// Async/Await and Promises
async function fetchData() {
  try {
    const response = await fetch("https://api.example.com/data");
    const data = await response.json();
    console.log("Fetched data:", data);
  } catch (error) {
    console.error("Error:", error);
  }
}
fetchData();

// Arrow functions
const greet = (name) => {
  console.log(`Hello, ${name}!`);
};
greet("Alice");

// Destructuring assignment
const [a, b, ...rest] = [1, 2, 3, 4, 5];
console.log(a, b, rest);

// Spread operator
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const combinedArr = [...arr1, ...arr2];
console.log("Combined array:", combinedArr);

// Ternary operator
const message = age >= 18 ? "You are an adult." : "You are a minor.";
console.log(message);
"""

BASH = """\
#!/bin/bash

# Variables
name="John"
age=30
is_student=true

# Printing variables
echo "Hello, $name! You are $age years old."

# Conditional statements
if [[ $age -ge 18 && $is_student == true ]]; then
  echo "You are an adult student."
elif [[ $age -ge 18 ]]; then
  echo "You are an adult."
else
  echo "You are a minor."
fi

# Arrays
numbers=(1 2 3 4 5)
echo "Numbers: ${numbers[@]}"

# Loops
for num in "${numbers[@]}"; do
  echo "Number: $num"
done

# Functions
greet() {
  local name=$1
  echo "Hello, $name!"
}
greet "Alice"

# Command substitution
current_date=$(date +%Y-%m-%d)
echo "Current date: $current_date"

# File operations
touch file.txt
echo "Some content" > file.txt
cat file.txt

# Conditionals with file checks
if [[ -f file.txt ]]; then
  echo "file.txt exists."
else
  echo "file.txt does not exist."
fi

# Case statement
case $age in
  18)
    echo "You are 18 years old."
    ;;
  30)
    echo "You are 30 years old."
    ;;
  *)
    echo "You are neither 18 nor 30 years old."
    ;;
esac

# While loop
counter=0
while [[ $counter -lt 5 ]]; do
  echo "Counter: $counter"
  ((counter++))
done

# Until loop
until [[ $counter -eq 0 ]]; do
  echo "Counter: $counter"
  ((counter--))
done

# Heredoc
cat << EOF
This is a heredoc.
It allows you to write multiple lines of text.
EOF

# Redirection
ls > file_list.txt
grep "file" file_list.txt > filtered_list.txt

# Pipes
cat file_list.txt | wc -l

# Arithmetic operations
result=$((10 + 5))
echo "Result: $result"

# Exporting variables
export DB_PASSWORD="secret"

# Sourcing external files
source config.sh
"""

KOTLIN = """\
// Variables
val name = "John"
var age = 30
var isStudent = true

// Printing variables
println("Hello, $name! You are $age years old.")

// Conditional statements
when {
    age >= 18 && isStudent -> println("You are an adult student.")
    age >= 18 -> println("You are an adult.")
    else -> println("You are a minor.")
}

// Arrays
val numbers = arrayOf(1, 2, 3, 4, 5)
println("Numbers: ${numbers.contentToString()}")

// Lists
val fruits = listOf("apple", "banana", "orange")
println("Fruits: $fruits")

// Loops
for (num in numbers) {
    println("Number: $num")
}

// Functions
fun greet(name: String) {
    println("Hello, $name!")
}
greet("Alice")

// Lambda functions
val square = { num: Int -> num * num }
println("Square of 5: ${square(5)}")

// Extension functions
fun String.reverse(): String {
    return this.reversed()
}
val reversed = "Hello".reverse()
println("Reversed: $reversed")

// Data classes
data class Person(val name: String, val age: Int)
val person = Person("John", 30)
println("Person: $person")

// Null safety
var nullable: String? = null
println("Length: ${nullable?.length}")

// Elvis operator
val length = nullable?.length ?: 0
println("Length (Elvis): $length")

// Smart casts
fun printLength(obj: Any) {
    if (obj is String) {
        println("Length: ${obj.length}")
    }
}
printLength("Hello")

// Object expressions
val comparator = object : Comparator<Int> {
    override fun compare(a: Int, b: Int): Int {
        return a - b
    }
}
val sortedNumbers = numbers.sortedWith(comparator)
println("Sorted numbers: ${sortedNumbers.contentToString()}")

// Companion objects
class MyClass {
    companion object {
        fun create(): MyClass {
            return MyClass()
        }
    }
}
val obj = MyClass.create()

// Sealed classes
sealed class Result {
    data class Success(val data: String) : Result()
    data class Error(val message: String) : Result()
}
val result: Result = Result.Success("Data")
when (result) {
    is Result.Success -> println("Success: ${result.data}")
    is Result.Error -> println("Error: ${result.message}")
}
"""

RUST = """\
use std::collections::HashMap;

// Constants
const PI: f64 = 3.14159;

// Structs
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }
}

// Enums
enum Result<T, E> {
    Ok(T),
    Err(E),
}

// Functions
fn greet(name: &str) {
    println!("Hello, {}!", name);
}

fn main() {
    // Variables
    let name = "John";
    let mut age = 30;
    let is_student = true;

    // Printing variables
    println!("Hello, {}! You are {} years old.", name, age);

    // Conditional statements
    if age >= 18 && is_student {
        println!("You are an adult student.");
    } else if age >= 18 {
        println!("You are an adult.");
    } else {
        println!("You are a minor.");
    }

    // Arrays
    let numbers = [1, 2, 3, 4, 5];
    println!("Numbers: {:?}", numbers);

    // Vectors
    let mut fruits = vec!["apple", "banana", "orange"];
    fruits.push("grape");
    println!("Fruits: {:?}", fruits);

    // Loops
    for num in &numbers {
        println!("Number: {}", num);
    }

    // Pattern matching
    let result = Result::Ok(42);
    match result {
        Result::Ok(value) => println!("Value: {}", value),
        Result::Err(error) => println!("Error: {:?}", error),
    }

    // Ownership and borrowing
    let s1 = String::from("hello");
    let s2 = s1.clone();
    println!("s1: {}, s2: {}", s1, s2);

    // References
    let rect = Rectangle {
        width: 10,
        height: 20,
    };
    println!("Rectangle area: {}", rect.area());

    // Hash maps
    let mut scores = HashMap::new();
    scores.insert("Alice", 100);
    scores.insert("Bob", 80);
    println!("Alice's score: {}", scores["Alice"]);

    // Closures
    let square = |num: i32| num * num;
    println!("Square of 5: {}", square(5));

    // Traits
    trait Printable {
        fn print(&self);
    }

    impl Printable for Rectangle {
        fn print(&self) {
            println!("Rectangle: width={}, height={}", self.width, self.height);
        }
    }
    rect.print();

    // Modules
    greet("Alice");
}
"""

JAVA = """\
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Classes and interfaces
interface Shape {
    double getArea();
}

class Rectangle implements Shape {
    private double width;
    private double height;

    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }

    @Override
    public double getArea() {
        return width * height;
    }
}

// Enums
enum DaysOfWeek {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
}

public class Main {
    // Constants
    private static final double PI = 3.14159;

    // Methods
    public static int sum(int a, int b) {
        return a + b;
    }

    public static void main(String[] args) {
        // Variables
        String name = "John";
        int age = 30;
        boolean isStudent = true;

        // Printing variables
        System.out.println("Hello, " + name + "! You are " + age + " years old.");

        // Conditional statements
        if (age >= 18 && isStudent) {
            System.out.println("You are an adult student.");
        } else if (age >= 18) {
            System.out.println("You are an adult.");
        } else {
            System.out.println("You are a minor.");
        }

        // Arrays
        int[] numbers = {1, 2, 3, 4, 5};
        System.out.println("Numbers: " + Arrays.toString(numbers));

        // Lists
        List<String> fruits = new ArrayList<>();
        fruits.add("apple");
        fruits.add("banana");
        fruits.add("orange");
        System.out.println("Fruits: " + fruits);

        // Loops
        for (int num : numbers) {
            System.out.println("Number: " + num);
        }

        // Hash maps
        Map<String, Integer> scores = new HashMap<>();
        scores.put("Alice", 100);
        scores.put("Bob", 80);
        System.out.println("Alice's score: " + scores.get("Alice"));

        // Exception handling
        try {
            int result = 10 / 0;
        } catch (ArithmeticException e) {
            System.out.println("Error: " + e.getMessage());
        }

        // Instantiating objects
        Rectangle rect = new Rectangle(10, 20);
        System.out.println("Rectangle area: " + rect.getArea());

        // Enums
        DaysOfWeek today = DaysOfWeek.MONDAY;
        System.out.println("Today is " + today);

        // Calling methods
        int sum = sum(5, 10);
        System.out.println("Sum: " + sum);

        // Ternary operator
        String message = age >= 18 ? "You are an adult." : "You are a minor.";
        System.out.println(message);
    }
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
    "javascript": JAVASCRIPT,
    "bash": BASH,
    "kotlin": KOTLIN,
    "rust": RUST,
    "java": JAVA,
}
