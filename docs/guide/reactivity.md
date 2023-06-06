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

=== "refresh01.css"

    ```sass
    --8<-- "docs/examples/guide/reactivity/refresh01.css"
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

=== "refresh02.css"

    ```sass hl_lines="7-9"
    --8<-- "docs/examples/guide/reactivity/refresh02.css"
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

=== "validate01.css"

    ```sass
    --8<-- "docs/examples/guide/reactivity/validate01.css"
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

=== "watch01.css"

    ```sass
    --8<-- "docs/examples/guide/reactivity/watch01.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/watch01.py" press="d,a,r,k,o,r,c,h,i,d"}
    ```

The color is parsed in `on_input_submitted` and assigned to `self.color`. Because `color` is reactive, Textual also calls `watch_color` with the old and new values.

### When are watch methods called?

Textual only calls watch methods if the value of a reactive attribute _changes_.
If the newly assigned value is the same as the previous value, the watch method is not called.
You can override this behaviour by passing `always_update=True` to `reactive`.

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

=== "computed01.css"

    ```sass
    --8<-- "docs/examples/guide/reactivity/computed01.css"
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
