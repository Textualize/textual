# OptionList

!!! tip "Added in version 0.17.0"

A widget for showing a vertical list of Rich renderable options.

- [x] Focusable
- [ ] Container

## Examples

### Options as simple strings

An `OptionList` can be constructed with a simple collection of string
options:

=== "Output"

    ```{.textual path="docs/examples/widgets/option_list_strings.py"}
    ```

=== "option_list_strings.py"

    ~~~python
    --8<-- "docs/examples/widgets/option_list_strings.py"
    ~~~

=== "option_list.css"

    ~~~python
    --8<-- "docs/examples/widgets/option_list.css"
    ~~~

### Options as `Option` instances

For finer control over the options, the `Option` class can be used; this
allows for setting IDs, setting initial disabled state, etc. The `Separator`
class can be used to add separator lines between options.

=== "Output"

    ```{.textual path="docs/examples/widgets/option_list_options.py"}
    ```

=== "option_list_options.py"

    ~~~python
    --8<-- "docs/examples/widgets/option_list_options.py"
    ~~~

=== "option_list.css"

    ~~~python
    --8<-- "docs/examples/widgets/option_list.css"
    ~~~

### Options as Rich renderables

Because the prompts for the options can be [Rich
renderables](https://rich.readthedocs.io/en/latest/protocol.html), this
means they can be any height you wish. As an example, here is an option list
comprised of [Rich
tables](https://rich.readthedocs.io/en/latest/tables.html):

=== "Output"

    ```{.textual path="docs/examples/widgets/option_list_tables.py"}
    ```

=== "option_list_tables.py"

    ~~~python
    --8<-- "docs/examples/widgets/option_list_tables.py"
    ~~~

=== "option_list.css"

    ~~~python
    --8<-- "docs/examples/widgets/option_list.css"
    ~~~

## Reactive Attributes

| Name          | Type            | Default | Description                                                               |
| ------------- | --------------- | ------- | ------------------------------------------------------------------------- |
| `highlighted` | `int` \| `None` | `None`  | The index of the highlighted option. `None` means nothing is highlighted. |

## Messages

- [OptionList.OptionHighlight][textual.widgets.OptionList.OptionHighlighted]
- [OptionList.OptionSelected][textual.widgets.OptionList.OptionSelected]

Both of the messages above inherit from this common base, which makes
available the following properties relating to the `OptionList` and the
related `Option`:

### Common message properties

Both of the above messages provide the following properties:

#### ::: textual.widgets.OptionList.OptionMessage.option
#### ::: textual.widgets.OptionList.OptionMessage.option_id
#### ::: textual.widgets.OptionList.OptionMessage.option_index
#### ::: textual.widgets.OptionList.OptionMessage.option_list

## Bindings

The option list widget defines the following bindings:

::: textual.widgets.OptionList.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The option list provides the following component classes:

::: textual.widgets.OptionList.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false



::: textual.widgets.OptionList
    options:
      heading_level: 2
