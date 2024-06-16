# Actions

Actions are allow-listed functions with a string syntax you can embed in links and bind to keys. In this chapter we will discuss how to create actions and how to run them.

## Action methods

Action methods are methods on your app or widgets prefixed with `action_`. Aside from the prefix these are regular methods which you could call directly if you wished.

!!! information

    Action methods may be coroutines (defined with the `async` keyword).

Let's write an app with a simple action method.

```python title="actions01.py" hl_lines="6-7 11"
--8<-- "docs/examples/guide/actions/actions01.py"
```

The `action_set_background` method is an action method which sets the background of the screen. The key handler above will call this action method if you press the ++r++ key.

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

- The name of an action on its own will call the action method with no parameters. For example, an action string of `"bell"` will call `action_bell()`.
- Action strings may be followed by parenthesis containing Python objects. For example, the action string `set_background("red")` will call `action_set_background("red")`.
- Action strings may be prefixed with a _namespace_ ([see below](#namespaces)) and a dot.

<div class="excalidraw">
--8<-- "docs/images/actions/format.excalidraw.svg"
</div>

### Parameters

If the action string contains parameters, these must be valid Python literals, which means you can include numbers, strings, dicts, lists, etc., but you can't include variables or references to any other Python symbols.

Consequently `"set_background('blue')"` is a valid action string, but `"set_background(new_color)"` is not &mdash; because `new_color` is a variable and not a literal.

## Links

Actions may be embedded as links within console markup. You can create such links with a `@click` tag.

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

=== "actions05.tcss"

    ```css title="actions05.tcss"
    --8<-- "docs/examples/guide/actions/actions05.tcss"
    ```

There are two instances of the custom widget mounted. If you click the links in either of them it will change the background for that widget only. The ++r++, ++g++, and ++b++ key bindings are set on the App so will set the background for the screen.

You can optionally prefix an action with a _namespace_, which tells Textual to run actions for a different object.

Textual supports the following action namespaces:

- `app` invokes actions on the App.
- `screen` invokes actions on the screen.
- `focused` invokes actions on the currently focused widget (if there is one).

In the previous example if you wanted a link to set the background on the app rather than the widget, we could set a link to `app.set_background('red')`.


## Dynamic actions

!!! tip "Added in version 0.61.0"

There may be situations where an action is temporarily unavailable due to some internal state within your app.
For instance, consider an app with a fixed number of pages and actions to go to the next and previous page.
It doesn't make sense to go to the previous page if we are on the first, or the next page when we are on the last page.

We could easily add this logic to the action methods, but the [footer][textual.widgets.Footer] would still display the keys even if they would have no effect.
The user may wonder why the app is showing keys that don't appear to work.

We can solve this issue by implementing the [`check_action`][textual.dom.DOMNode.check_action] on our app, screen, or widget.
This method is called with the name of the action and any parameters, prior to running actions or refreshing the footer.
It should return one of the following values:

- `True` to show the key and run the action as normal.
- `False` to hide the key and prevent the action running.
- `None` to disable the key (show dimmed), and prevent the action running.

Let's write an app to put this into practice:

=== "actions06.py"

    ```python title="actions06.py" hl_lines="27 32 35-43"
    --8<-- "docs/examples/guide/actions/actions06.py"
    ```

    1. Prompts the footer to refresh, if bindings change.
    2. Prompts the footer to refresh, if bindings change.
    3. Guards the actions from running and also what keys are displayed in the footer.

=== "actions06.tcss"

    ```css title="actions06.tcss"
    --8<-- "docs/examples/guide/actions/actions06.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/actions/actions06.py"}
    ```

This app has key bindings for ++n++ and ++p++ to navigate the pages.
Notice how the keys are hidden from the footer when they would have no effect.

The actions above call [`refresh_bindings`][textual.dom.DOMNode.refresh_bindings] to prompt Textual to refresh the footer.
An alternative to doing this manually is to set `bindings=True` on a [reactive](./reactivity.md), which will refresh the bindings if the reactive changes.

Let's make this change.
We will also demonstrate what the footer will show if we return `None` from `check_action` (rather than `False`):


=== "actions07.py"

    ```python title="actions06.py" hl_lines="17 36 38"
    --8<-- "docs/examples/guide/actions/actions07.py"
    ```

    1. The `bindings=True` causes the footer to refresh when `page_no` changes.
    2. Returning `None` disables the key in the footer rather than hides it
    3. Returning `None` disables the key in the footer rather than hides it.

=== "actions06.tcss"

    ```css title="actions06.tcss"
    --8<-- "docs/examples/guide/actions/actions06.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/actions/actions07.py"}
    ```

Note how the logic is the same but we don't need to explicitly call [`refresh_bindings`][textual.dom.DOMNode.refresh_bindings].
The change to `check_action` also causes the disabled footer keys to be grayed out, indicating they are temporarily unavailable.


## Builtin actions

Textual supports the following builtin actions which are defined on the app.

- [action_add_class][textual.app.App.action_add_class]
- [action_back][textual.app.App.action_back]
- [action_bell][textual.app.App.action_bell]
- [action_focus_next][textual.app.App.action_focus_next]
- [action_focus_previous][textual.app.App.action_focus_previous]
- [action_focus][textual.app.App.action_focus]
- [action_pop_screen][textual.app.App.action_pop_screen]
- [action_push_screen][textual.app.App.action_push_screen]
- [action_quit][textual.app.App.action_quit]
- [action_remove_class][textual.app.App.action_remove_class]
- [action_screenshot][textual.app.App.action_screenshot]
- [action_simulate_key][textual.app.App.action_simulate_key]
- [action_suspend_process][textual.app.App.action_suspend_process]
- [action_switch_screen][textual.app.App.action_switch_screen]
- [action_toggle_class][textual.app.App.action_toggle_class]
- [action_toggle_dark][textual.app.App.action_toggle_dark]
