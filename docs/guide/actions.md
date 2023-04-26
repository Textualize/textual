# Actions

Actions are allow-listed functions with a string syntax you can embed in links and bind to keys. In this chapter we will discuss how to create actions and how to run them.

## Action methods

Action methods are methods on your app or widgets prefixed with `action_`. Aside from the prefix these are regular methods which you could call directly if you wished.

!!! information

    Action methods may be coroutines (defined with the `async` keyword).

Let's write an app with a simple action.

```python title="actions01.py" hl_lines="6-7 11"
--8<-- "docs/examples/guide/actions/actions01.py"
```

The `action_set_background` method is an action which sets the background of the screen. The key handler above will call this action if you press the ++r++ key.

Although it is possible (and occasionally useful) to call action methods in this way, they are intended to be parsed from an _action string_. For instance, the string `"set_background('red')"` is an action string which would call `self.action_set_background('red')`.

The following example replaces the immediate call with a call to [run_action()][textual.widgets.Widget.run_action] which parses an action string and dispatches it to the appropriate method.

```python title="actions02.py" hl_lines="9-11"
--8<-- "docs/examples/guide/actions/actions02.py"
```

Note that the `run_action()` method is a coroutine so `on_key` needs to be prefixed with the `async` keyword.

You will not typically need this in a real app as Textual will run actions in links or key bindings. Before we discuss these, let's have a closer look at the syntax for action strings.

## Syntax

Action strings have a simple syntax, which for the most part replicates Python's function call syntax.

!!! important

    As much as they *look* like Python code, Textual does **not** call Python's `eval` function to compile action strings.

Action strings have the following format:

- The name of an action on is own will call the action method with no parameters. For example, an action string of `"bell"` will call `action_bell()`.
- Actions may be followed by braces containing Python objects. For example, the action string `set_background("red")` will call `action_set_background("red")`.
- Actions may be prefixed with a _namespace_ (see below) followed by a dot.

<div class="excalidraw">
--8<-- "docs/images/actions/format.excalidraw.svg"
</div>

### Parameters

If the action string contains parameters, these must be valid Python literals. Which means you can include numbers, strings, dicts, lists etc. but you can't include variables or references to any other Python symbols.

Consequently `"set_background('blue')"` is a valid action string, but `"set_background(new_color)"` is not &mdash; because `new_color` is a variable and not a literal.

## Links

Actions may be embedded as links within console markup. You can create such links with a  `@click` tag.

The following example mounts simple static text with embedded action links.

=== "actions03.py"

    ```python title="actions03.py" hl_lines="4-9 13-14"
    --8<-- "docs/examples/guide/actions/actions03.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/actions/actions03.py"}
    ```

When you click any of the links, Textual runs the `"set_background"` action to change the background to the given color.

## Bindings

Textual will run actions bound to keys. The following example adds key [bindings](./input.md#bindings) for the ++r++, ++g++, and ++b++ keys which call the `"set_background"` action.

=== "actions04.py"

    ```python title="actions04.py" hl_lines="13-17"
    --8<-- "docs/examples/guide/actions/actions04.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/actions/actions04.py" press="g"}
    ```

If you run this example, you can change the background by pressing keys in addition to clicking links.

See the previous section on [input](./input.md#bindings) for more information on bindings.

## Namespaces

Textual will look for action methods in the class where they are defined (App, Screen, or Widget). If we were to create a [custom widget](./widgets.md#custom-widgets) it can have its own set of actions.

The following example defines a custom widget with its own `set_background` action.

=== "actions05.py"

    ```python title="actions05.py" hl_lines="13-14"
    --8<-- "docs/examples/guide/actions/actions05.py"
    ```

=== "actions05.css"

    ```sass title="actions05.css"
    --8<-- "docs/examples/guide/actions/actions05.css"
    ```

There are two instances of the custom widget mounted. If you click the links in either of them it will changed the background for that widget only. The ++r++, ++g++, and ++b++ key bindings are set on the App so will set the background for the screen.

You can optionally prefix an action with a _namespace_, which tells Textual to run actions for a different object.

Textual supports the following action namespaces:

- `app` invokes actions on the App.
- `screen` invokes actions on the screen.

In the previous example if you wanted a link to set the background on the app rather than the widget, we could set a link to `app.set_background('red')`.


## Builtin actions

Textual supports the following builtin actions which are defined on the app.

- [action_add_class][textual.app.App.action_add_class]
- [action_back][textual.app.App.action_back]
- [action_bell][textual.app.App.action_bell]
- [action_check_bindings][textual.app.App.action_check_bindings]
- [action_focus][textual.app.App.action_focus]
- [action_focus_next][textual.app.App.action_focus_next]
- [action_focus_previous][textual.app.App.action_focus_previous]
- [action_pop_screen][textual.app.App.action_pop_screen]
- [action_push_screen][textual.app.App.action_push_screen]
- [action_quit][textual.app.App.action_quit]
- [action_remove_class][textual.app.App.action_remove_class]
- [action_screenshot][textual.app.App.action_screenshot]
- [action_switch_screen][textual.app.App.action_switch_screen]
- [action_toggle_class][textual.app.App.action_toggle_class]
- [action_toggle_dark][textual.app.App.action_toggle_dark]
