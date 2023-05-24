# SelectionList

!!! tip "Added in version 0.??.0"

A widget for showing a vertical list check boxes.

- [x] Focusable
- [ ] Container

## Examples

Some super-cool examples will appear here!

## Reactive Attributes

| Name          | Type            | Default | Description                                                                  |
|---------------|-----------------|---------|------------------------------------------------------------------------------|
| `highlighted` | `int` \| `None` | `None`  | The index of the highlighted selection. `None` means nothing is highlighted. |

## Messages

The following messages will be posted as the user interacts with the list:

- [SelectionList.SelectionHighlighted][textual.widgets.SelectionList.SelectionHighlighted]
- [SelectionList.SelectionToggled][textual.widgets.SelectionList.SelectionToggled]

The following message will be posted if the content of
[`selected`][textual.widgets.SelectionList.selected] changes, either by user
interaction or by API calls:

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
