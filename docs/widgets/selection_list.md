# SelectionList

!!! tip "Added in version 0.27.0"

A widget for showing a vertical list of selectable options.

- [x] Focusable
- [ ] Container

## Typing

The `SelectionList` control is a
[`Generic`](https://docs.python.org/3/library/typing.html#typing.Generic),
which allows you to set the type of the
[selection values][textual.widgets.selection_list.Selection.value]. For instance, if
the data type for your values is an integer, you would type the widget as
follows:

```python
selections = [("First", 1), ("Second", 2)]
my_selection_list: SelectionList[int] =  SelectionList(*selections)
```

!!! note

    Typing is entirely optional.

    If you aren't familiar with typing or don't want to worry about it right now, feel free to ignore it.

## Examples

A selection list is designed to be built up of single-line prompts (which
can be [Rich `Text`](https://rich.readthedocs.io/en/stable/text.html)) and
an associated unique value.

### Selections as tuples

A selection list can be built with tuples, either of two or three values in
length. Each tuple must contain a prompt and a value, and it can also
optionally contain a flag for the initial selected state of the option.

=== "Output"

    ```{.textual path="docs/examples/widgets/selection_list_tuples.py"}
    ```

=== "selection_list_tuples.py"

    ~~~python
    --8<-- "docs/examples/widgets/selection_list_tuples.py"
    ~~~

    1. Note that the `SelectionList` is typed as `int`, for the type of the values.

=== "selection_list.tcss"

    ~~~css
    --8<-- "docs/examples/widgets/selection_list.tcss"
    ~~~

### Selections as Selection objects

Alternatively, selections can be passed in as
[`Selection`][textual.widgets.selection_list.Selection]s:

=== "Output"

    ```{.textual path="docs/examples/widgets/selection_list_selections.py"}
    ```

=== "selection_list_selections.py"

    ~~~python
    --8<-- "docs/examples/widgets/selection_list_selections.py"
    ~~~

    1. Note that the `SelectionList` is typed as `int`, for the type of the values.

=== "selection_list.tcss"

    ~~~css
    --8<-- "docs/examples/widgets/selection_list.tcss"
    ~~~

### Handling changes to the selections

Most of the time, when using the `SelectionList`, you will want to know when
the collection of selected items has changed; this is ideally done using the
[`SelectedChanged`][textual.widgets.SelectionList.SelectedChanged] message.
Here is an example of using that message to update a `Pretty` with the
collection of selected values:

=== "Output"

    ```{.textual path="docs/examples/widgets/selection_list_selected.py"}
    ```

=== "selection_list_selections.py"

    ~~~python
    --8<-- "docs/examples/widgets/selection_list_selected.py"
    ~~~

    1. Note that the `SelectionList` is typed as `str`, for the type of the values.

=== "selection_list.tcss"

    ~~~css
    --8<-- "docs/examples/widgets/selection_list_selected.tcss"
    ~~~

## Reactive Attributes

| Name          | Type            | Default | Description                                                                  |
|---------------|-----------------|---------|------------------------------------------------------------------------------|
| `highlighted` | `int` \| `None` | `None`  | The index of the highlighted selection. `None` means nothing is highlighted. |

## Messages

- [SelectionList.SelectionHighlighted][textual.widgets.SelectionList.SelectionHighlighted]
- [SelectionList.SelectionToggled][textual.widgets.SelectionList.SelectionToggled]
- [SelectionList.SelectedChanged][textual.widgets.SelectionList.SelectedChanged]

## Bindings

The selection list widget defines the following bindings:

::: textual.widgets.SelectionList.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

It inherits from [`OptionList`][textual.widgets.OptionList]
and so also inherits the following bindings:

::: textual.widgets.OptionList.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The selection list provides the following component classes:

::: textual.widgets.SelectionList.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

It inherits from [`OptionList`][textual.widgets.OptionList] and so also
makes use of the following component classes:

::: textual.widgets.OptionList.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

::: textual.widgets.SelectionList
    options:
      heading_level: 2

::: textual.widgets.selection_list
    options:
      heading_level: 2
