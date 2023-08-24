---
title: "How do I pass arguments to an app?"
alt_titles:
  - "pass arguments to an application"
  - "pass parameters to an app"
  - "pass parameters to an application"
---

When creating your `App` class, override `__init__` as you would when
inheriting normally. For example:

```python
from textual.app import App, ComposeResult
from textual.widgets import Static

class Greetings(App[None]):

    def __init__(self, greeting: str="Hello", to_greet: str="World") -> None:
        self.greeting = greeting
        self.to_greet = to_greet
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Static(f"{self.greeting}, {self.to_greet}")
```

Then the app can be run, passing in various arguments; for example:

```python
# Running with default arguments.
Greetings().run()

# Running with a keyword argument.
Greetings(to_greet="davep").run()

# Running with both positional arguments.
Greetings("Well hello", "there").run()
```
