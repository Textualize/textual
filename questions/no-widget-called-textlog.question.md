---
title: "No widget called TextLog"
alt_titles:
  - "ImportError with TextLog"
  - "TextLog does not exist"
---

The `TextLog` widget was renamed to `RichLog` in Textual 0.32.0.
You will need to replace all references to `TextLog` in your code, with `RichLog`.
Most IDEs will have a search and replace function which will help you do this.

Here's how you should import RichLog:

```python
from textual.widgets import RichLog
```
