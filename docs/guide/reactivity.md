# Reactivity

Textual's reactive attributes are attributes _with superpowers_. In this chapter we will look at how reactive attributes can simplify your apps.

!!! quote

    With great power comes great responsibility.

    &mdash; Uncle Ben

## Reactive attributes

Textual provides an alternative way of adding attributes to your widget or App, which doesn't require adding them to your class constructor (`__init__`). To create these attributes import [reactive][textual.reactive.reactive] from `textual.reactive`, and assign them in the class scope.

The following code illustrates how to create reactive attributes:

```python
from textual.reactive import reactive
from textual.widget import Widget

class Reactive(Widget):

    name = reactive("Paul")  # (1)!
    count = reactive(0) # (2)!
    is_cool = reactive(True)  # (3)!
```

1. Create a string attribute with a default of `"Paul"`
2. Creates an integer attribute with a default of `0`.
3. Creates a boolean attribute with a default of `True`.

The `reactive` constructor accepts a default value as the first positional argument.

!!! information

    Textual uses Python's _descriptor protocol_ to create reactive attributes, which is the same protocol used by the builtin `property` decorator.

You can get and set these attributes in the same way as if you had assigned them in an `__init__` method. For instance `self.name = "Jessica"`, `self.count += 1`, or `print(self.is_cool)`.

### Dynamic defaults

You can also set the default to a function (or other callable). Textual will call this function to get the default value. The following code illustrates a reactive value which will be automatically assigned the current time when the widget is created:

```python
from time import time
from textual.reactive import reactive
from textual.widget import Widget

class Timer(Widget):

    start_time = reactive(time)  # (1)!
```

1. The `time` function returns the current time in seconds.

### Typing reactive attributes

There is no need to specify a type hint if a reactive attribute has a default value, as type checkers will assume the attribute is the same type as the default.

You may want to add explicit type hints if the attribute type is a superset of the default type. For instance if you want to make an attribute optional. Here's how you would create a reactive string attribute which may be `None`:

```python
    name: reactive[str | None] = reactive("Paul")
```

## Smart refresh

The first superpower we will look at is "smart refresh". When you modify a reactive attribute, Textual will make note of the fact that it has changed and refresh automatically.

!!! information

    If you modify multiple reactive attributes, Textual will only do a single refresh to minimize updates.

Let's look at an example which illustrates this. In the following app, the value of an input is used to update a "Hello, World!" type greeting.

=== "refresh01.py"

    ```python hl_lines="7-13 24"
    --8<-- "docs/examples/guide/reactivity/refresh01.py"
    ```

=== "refresh01.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/refresh01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/refresh01.py" press="T,e,x,t,u,a,l"}
    ```

The `Name` widget has a reactive `who` attribute. When the app modifies that attribute, a refresh happens automatically.

!!! information

    Textual will check if a value has really changed, so assigning the same value wont prompt an unnecessary refresh.

### Disabling refresh

If you *don't* want an attribute to prompt a refresh or layout but you still want other reactive superpowers, you can use [var][textual.reactive.var] to create an attribute. You can import `var` from `textual.reactive`.

The following code illustrates how you create non-refreshing reactive attributes.

```python
class MyWidget(Widget):
    count = var(0)  # (1)!
```

1. Changing `self.count` wont cause a refresh or layout.

### Layout

The smart refresh feature will update the content area of a widget, but will not change its size. If modifying an attribute should change the size of the widget, you can set `layout=True` on the reactive attribute. This ensures that your CSS layout will update accordingly.

The following example modifies "refresh01.py" so that the greeting has an automatic width.

=== "refresh02.py"

    ```python hl_lines="10"
    --8<-- "docs/examples/guide/reactivity/refresh02.py"
    ```

    1. This attribute will update the layout when changed.

=== "refresh02.tcss"

    ```css hl_lines="7-9"
    --8<-- "docs/examples/guide/reactivity/refresh02.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/refresh02.py" press="n,a,m,e"}
    ```

If you type in to the input now, the greeting will expand to fit the content. If you were to set `layout=False` on the reactive attribute, you should see that the box remains the same size when you type.

## Validation

The next superpower we will look at is _validation_, which can check and potentially modify a value you assign to a reactive attribute.

If you add a method that begins with `validate_` followed by the name of your attribute, it will be called when you assign a value to that attribute. This method should accept the incoming value as a positional argument, and return the value to set (which may be the same or a different value).

A common use for this is to restrict numbers to a given range. The following example keeps a count. There is a button to increase the count, and a button to decrease it. The validation ensures that the count will never go above 10 or below zero.

=== "validate01.py"

    ```python hl_lines="12-18 30 32"
    --8<-- "docs/examples/guide/reactivity/validate01.py"
    ```

=== "validate01.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/validate01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/validate01.py"}
    ```

If you click the buttons in the above example it will show the current count. When `self.count` is modified in the button handler, Textual runs `validate_count` which performs the validation to limit the value of count.

## Watch methods

Watch methods are another superpower.
Textual will call watch methods when reactive attributes are modified.
Watch method names begin with `watch_` followed by the name of the attribute, and should accept one or two arguments.
If the method accepts a single argument, it will be called with the new assigned value.
If the method accepts *two* positional arguments, it will be called with both the *old* value and the *new* value.

The following app will display any color you type in to the input. Try it with a valid color in Textual CSS. For example `"darkorchid"` or `"#52de44"`.

=== "watch01.py"

    ```python hl_lines="17-19 28"
    --8<-- "docs/examples/guide/reactivity/watch01.py"
    ```

    1. Creates a reactive [color][textual.color.Color] attribute.
    2. Called when `self.color` is changed.
    3. New color is assigned here.

=== "watch01.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/watch01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/watch01.py" press="d,a,r,k,o,r,c,h,i,d"}
    ```

The color is parsed in `on_input_submitted` and assigned to `self.color`. Because `color` is reactive, Textual also calls `watch_color` with the old and new values.

### When are watch methods called?

Textual only calls watch methods if the value of a reactive attribute _changes_.
If the newly assigned value is the same as the previous value, the watch method is not called.
You can override this behavior by passing `always_update=True` to `reactive`.


### Dynamically watching reactive attributes

You can programmatically add watchers to reactive attributes with the method [`watch`][textual.dom.DOMNode.watch].
This is useful when you want to react to changes to reactive attributes for which you can't edit the watch methods.

The example below shows a widget `Counter` that defines a reactive attribute `counter`.
The app that uses `Counter` uses the method `watch` to keep its progress bar synced with the reactive attribute:

=== "dynamic_watch.py"

    ```python hl_lines="9 28-29 31"
    --8<-- "docs/examples/guide/reactivity/dynamic_watch.py"
    ```

    1. `counter` is a reactive attribute defined inside `Counter`.
    2. `update_progress` is a custom callback that will update the progress bar when `counter` changes.
    3. We use the method `watch` to set `update_progress` as an additional watcher for the reactive attribute `counter`.

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/dynamic_watch.py" press="enter,enter,enter"}
    ```

## Recompose

An alternative to a refresh is *recompose*.
If you set `recompose=True` on a reactive, then Textual will remove all the child widgets and call [`compose()`][textual.widget.Widget.compose] again, when the reactive attribute changes.
The process of removing and mounting new widgets occurs in a single update, so it will appear as though the content has simply updated.

The following example uses recompose:

=== "refresh03.py"

    ```python hl_lines="10 12-13"
    --8<-- "docs/examples/guide/reactivity/refresh03.py"
    ```

    1. Setting `recompose=True` will cause all child widgets to be removed and `compose` called again to add new widgets.
    2. This `compose()` method will be called when `who` is changed.

=== "refresh03.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/refresh03.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/refresh03.py" press="P,a,u,l"}
    ```

While the end-result is identical to `refresh02.py`, this code works quite differently.
The main difference is that recomposing creates an entirely new set of child widgets rather than updating existing widgets.
So when the `who` attribute changes, the `Name` widget will replace its `Label` with a new instance (containing updated content).

!!! warning 

    You should avoid storing a reference to child widgets when using recompose.
    Better to [query](../guide/queries.md) for a child widget when you need them.

It is important to note that any child widgets will have their state reset after a recompose.
For simple content, that doesn't matter much.
But widgets with an internal state (such as [`DataTable`](../widgets/data_table.md), [`Input`](../widgets/input.md), or [`TextArea`](../widgets/text_area.md)) would not be particularly useful if recomposed.

Recomposing is slightly less efficient than a simple refresh, and best avoided if you need to update rapidly or you have many child widgets.
That said, it can often simplify your code.
Let's look at a practical example.
First a version *without* recompose:

=== "recompose01.py"

    ```python hl_lines="20 26-27"
    --8<-- "docs/examples/guide/reactivity/recompose01.py"
    ```

    1. Called when the `time` attribute changes.
    2. Update the time once a second.

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/recompose01.py" }
    ```

This displays a clock which updates once a second.
The code is straightforward, but note how we format the time in two places: `compose()` *and* `watch_time()`.
We can simplify this by recomposing rather than refreshing:

=== "recompose02.py"

    ```python hl_lines="15"
    --8<-- "docs/examples/guide/reactivity/recompose02.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/recompose02.py" }
    ```

In this version, the app is recomposed when the `time` attribute changes, which replaces the `Digits` widget with a new instance and updated time.
There's no need for the `watch_time` method, because the new `Digits` instance will already show the current time.


## Compute methods

Compute methods are the final superpower offered by the `reactive` descriptor. Textual runs compute methods to calculate the value of a reactive attribute. Compute methods begin with `compute_` followed by the name of the reactive value.

You could be forgiven in thinking this sounds a lot like Python's property decorator. The difference is that Textual will cache the value of compute methods, and update them when any other reactive attribute changes.

The following example uses a computed attribute. It displays three inputs for each color component (red, green, and blue). If you enter numbers in to these inputs, the background color of another widget changes.

=== "computed01.py"

    ```python hl_lines="25-26 28-29"
    --8<-- "docs/examples/guide/reactivity/computed01.py"
    ```

    1. Combines color components in to a Color object.
    2. The watch method is called when the _result_ of `compute_color` changes.

=== "computed01.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/computed01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/computed01.py"}
    ```

Note the `compute_color` method which combines the color components into a [Color][textual.color.Color] object. It will be recalculated when any of the `red` , `green`, or `blue` attributes are modified.

When the result of `compute_color` changes, Textual will also call `watch_color` since `color` still has the [watch method](#watch-methods) superpower.

!!! note

    Textual will first attempt to call the compute method for a reactive attribute, followed by the validate method, and finally the watch method.

!!! note

    It is best to avoid doing anything slow or CPU-intensive in a compute method. Textual calls compute methods on an object when _any_ reactive attribute changes.

## Setting reactives without superpowers 

You may find yourself in a situation where you want to set a reactive value, but you *don't* want to invoke watchers or the other super powers.
This is fairly common in constructors which run prior to mounting; any watcher which queries the DOM may break if the widget has not yet been mounted.

To work around this issue, you can call [set_reactive][textual.dom.DOMNode.set_reactive] as an alternative to setting the attribute.
The `set_reactive` method accepts the reactive attribute (as a class variable) and the new value.

Let's look at an example.
The following app is intended to cycle through various greeting when you press ++space++, however it contains a bug.

```python title="set_reactive01.py"
--8<-- "docs/examples/guide/reactivity/set_reactive01.py"
```

1. Setting this reactive attribute invokes a watcher.
2. The watcher attempts to update a label before it is mounted.

If you run this app, you will find Textual raises a `NoMatches` error in `watch_greeting`. 
This is because the constructor has assigned the reactive before the widget has fully mounted.

The following app contains a fix for this issue:

=== "set_reactive02.py"

    ```python hl_lines="33 34"
    --8<-- "docs/examples/guide/reactivity/set_reactive02.py"
    ```

    1. The attribute is set via `set_reactive`, which avoids calling the watcher.

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/set_reactive02.py"}
    ```

The line `self.set_reactive(Greeter.greeting, greeting)` sets the `greeting` attribute but doesn't immediately invoke the watcher.

## Mutable reactives

Textual can detect when you set a reactive to a new value, but it can't detect when you _mutate_ a value.
In practice, this means that Textual can detect changes to basic types (int, float, str, etc.), but not if you update a collection, such as a list or dict. 

You can still use collections and other mutable objects in reactives, but you will need to call [`mutate_reactive`][textual.dom.DOMNode.mutate_reactive] after making changes for the reactive superpowers to work.

Here's an example, that uses a reactive list:

=== "set_reactive03.py"

    ```python hl_lines="16"
    --8<-- "docs/examples/guide/reactivity/set_reactive03.py"
    ```

    1. Creates a reactive list of strings.
    2. Explicitly mutate the reactive list.

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/set_reactive03.py" press="W,i,l,l,enter"}
    ```

Note the call to `mutate_reactive`. Without it, the display would not update when a new name is appended to the list.

## Data binding

Reactive attributes may be *bound* (connected) to attributes on child widgets, so that changes to the parent are automatically reflected in the children.
This can simplify working with compound widgets where the value of an attribute might be used in multiple places.

To bind reactive attributes, call [data_bind][textual.dom.DOMNode.data_bind] on a widget.
This method accepts reactives (as class attributes) in positional arguments or keyword arguments.

Let's look at an app that could benefit from data binding.
In the following code we have a `WorldClock` widget which displays the time in any given timezone.


!!! note

    This example uses the [pytz](https://pypi.org/project/pytz/) library for working with timezones.
    You can install pytz with `pip install pytz`.


=== "world_clock01.py"

    ```python
    --8<-- "docs/examples/guide/reactivity/world_clock01.py"
    ```

    1. Update the `time` reactive attribute of every `WorldClock`.

=== "world_clock01.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/world_clock01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/world_clock01.py"}
    ```

We've added three world clocks for London, Paris, and Tokyo.
The clocks are kept up-to-date by watching the app's `time` reactive, and updating the clocks in a loop.

While this approach works fine, it does require we take care to update every `WorldClock` we mount.
Let's see how data binding can simplify this.

The following app calls `data_bind` on the world clock widgets to connect the app's `time` with the widget's `time` attribute:

=== "world_clock02.py"

    ```python hl_lines="34-36"
    --8<-- "docs/examples/guide/reactivity/world_clock02.py"
    ```

    1. Bind the `time` attribute, so that changes to `time` will also change the `time` attribute on the `WorldClock` widgets. The `data_bind` method also returns the widget, so we can yield its return value.

=== "world_clock01.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/world_clock01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/world_clock02.py"}
    ```

Note how the addition of the `data_bind` methods negates the need for the watcher in `world_clock01.py`.


!!! note

    Data binding works in a single direction.
    Setting `time` on the app updates the clocks.
    But setting `time` on the clocks will *not* update `time` on the app.


In the previous example app, the call to `data_bind(WorldClockApp.time)` worked because both reactive attributes were named `time`.
If you want to bind a reactive attribute which has a different name, you can use keyword arguments.

In the following app we have changed the attribute name on `WorldClock` from `time` to `clock_time`.
We can make the app continue to work by changing the `data_bind` call to `data_bind(clock_time=WorldClockApp.time)`:


=== "world_clock03.py"

    ```python hl_lines="34-38"
    --8<-- "docs/examples/guide/reactivity/world_clock03.py"
    ```

    1. Uses keyword arguments to bind the `time` attribute of `WorldClockApp` to `clock_time` on `WorldClock`.

=== "world_clock01.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/world_clock01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/world_clock02.py"}
    ```
