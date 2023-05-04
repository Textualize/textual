---
title: "Why doesn't the `DataTable` scroll programmatically?"
alt_titles:
  - "Scroll bindings from `DataTable` not working."
  - "Datatable cursor goes off screen and doesn't scroll."
---

If scrolling in your `DataTable` is _apparently_ broken, it may be because your `DataTable` is using the default value of `height: auto`.
This means that the `DataTable` itself does not have a scrollbar and it cannot scroll itself.
The scrollbar(s) you see belong to the container(s) of the `DataTable`.

To see the difference, try running the app below with and without the comment in the attribute `TableApp.CSS`.
Press <kbd>E</kbd> to scroll the `DataTable` to the end.
If the `CSS` is commented out, the `DataTable` does not have its own scrollbar and it cannot scroll.

<details>
<summary>Example app.</summary>

```py
from textual.app import App, ComposeResult
from textual.widgets import DataTable


class TableApp(App):
    # CSS = "DataTable { height: 100% }"

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_column("n")
        table.add_rows([(n,) for n in range(300)])

    def key_e(self) -> None:
        self.query_one(DataTable).action_scroll_end()


app = TableApp()
if __name__ == "__main__":
    app.run()
```

</details>
