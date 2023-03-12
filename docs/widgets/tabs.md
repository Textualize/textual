# Tabs

Displays a number of tab headers which may be clicked or navigated with cursor keys.

- [x] Focusable
- [ ] Container

You can construct a `Tabs` widget with strings or [Text][rich.text.Text] objects as positional arguments. Here's an example with three tabs:

```python
def compose(self) -> ComposeResult:
    yield Tabs("First tab", "Second tab", Text.from_markup("[u]Third[/u] tab"))
```

This will create [Tab][textual.widgets.Tab] widgets internally, with an auto-incrementing `id` attribute (`"tab-1"`, `"tab-2"` etc).
You can also supply `Tab` objects directly in the constructor, which will allow you to explicitly set an `id`. Here's an example:

```python
def compose(self) -> ComposeResult:
    yield Tabs(
        Tab("First tab", id="one"),
        Tab("Second tab", id="two")
    )
```

When the user switches to a tab by clicking or pressing keys, then Tabs will send a [Tabs.TabActivated][textual.widgets.Tabs.TabActivated] messages which contains the `tab` that was activated.
You can use `event.tab.id` attribute to respond the the tab that was activated.


## Example

The following example adds a Tabs widget above a text label. Press ++a++ to add a tab, ++c++ to clear the tabs.

=== "Output"

    ```{.textual path="docs/examples/widgets/tabs.py" press="a,a,a,a,right,right"}
    ```

=== "tabs.py"

    ```python
    --8<-- "docs/examples/widgets/tabs.py"
    ```


## Reactive Attributes

| Name     | Type  | Default | Description              |
| -------- | ----- | ------- | ------------------------ |
| `active` | `str` | `""`    | The ID of the active tab |


## Messages

### ::: textual.widgets.Tabs.TabActivated


## Bindings

The Tabs widget defines the following bindings:

::: textual.widgets.Tabs.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## See Also

- [Tabs](../api/tabs.md) code reference
