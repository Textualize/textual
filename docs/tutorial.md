---
hide:
  - navigation
---

# Tutorial

Welcome to the Textual Tutorial!

By the end of this page you should have a solid understanding of app development with Textual.

!!! quote

    If you want people to build things, make it fun.

    &mdash; **Will McGugan** (creator of Rich and Textual)

## Video series

This tutorial has an accompanying [video series](https://www.youtube.com/playlist?list=PLHhDR_Q5Me1MxO4LmfzMNNQyKfwa275Qe) which covers the same content.

## Stopwatch Application

We're going to build a stopwatch application. This application should show a list of stopwatches with buttons to start, stop, and reset the stopwatches. We also want the user to be able to add and remove stopwatches as required.

This will be a simple yet **fully featured** app &mdash; you could distribute this app if you wanted to!

Here's what the finished app will look like:


```{.textual path="docs/examples/tutorial/stopwatch.py" title="stopwatch.py" press="tab,enter,tab,enter,tab,enter,tab,enter"}
```

!!! info

    Did you notice the `^p palette` at the bottom right hand corner?
    This is the [Command Palette](./guide/command_palette.md).
    You can think of it as a dedicated command prompt for your app.

### Try it out!

The following is *not* a screenshot, but a fully interactive Textual app running in your browser.


!!! textualize "Try in Textual-web"

    <div class="textual-web-demo" data-app="tutorial"></div>


!!! tip

    See [textual-web](https://github.com/Textualize/textual-web) if you are interested in publishing your Textual apps on the web.


### Get the code

If you want to try the finished Stopwatch app and follow along with the code, first make sure you have [Textual installed](getting_started.md) then check out the [Textual](https://github.com/Textualize/textual) repository:

=== "HTTPS"

    ```bash
    git clone https://github.com/Textualize/textual.git
    ```

=== "SSH"

    ```bash
    git clone git@github.com:Textualize/textual.git
    ```

=== "GitHub CLI"

    ```bash
    gh repo clone Textualize/textual
    ```


With the repository cloned, navigate to `docs/examples/tutorial` and run `stopwatch.py`.

```bash
cd textual/docs/examples/tutorial
python stopwatch.py
```

## Type hints (in brief)

!!! tip inline end

    Type hints are entirely optional in Textual. We've included them in the example code but it's up to you whether you add them to your own projects.

We're a big fan of Python type hints at Textualize. If you haven't encountered type hinting, it's a way to express the types of your data, parameters, and return values. Type hinting allows tools like [mypy](https://mypy.readthedocs.io/en/stable/) to catch bugs before your code runs.

The following function contains type hints:

```python
def repeat(text: str, count: int) -> str:
    """Repeat a string a given number of times."""
    return text * count
```

Parameter types follow a colon. So `text: str` indicates that `text` requires a string and `count: int` means that `count` requires an integer.

Return types follow `->`. So `-> str:` indicates this method returns a string.


## The App class

The first step in building a Textual app is to import and extend the `App` class. Here's a basic app class we will use as a starting point for the stopwatch app.

```python title="stopwatch01.py"
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

If you run this code, you should see something like the following:


```{.textual path="docs/examples/tutorial/stopwatch01.py" title="stopwatch01.py"}
```

Hit the ++d++ key to toggle between light and dark themes.

```{.textual path="docs/examples/tutorial/stopwatch01.py" press="d" title="stopwatch01.py"}
```

Hit ++ctrl+c++ to exit the app and return to the command prompt.

### A closer look at the App class

Let's examine `stopwatch01.py` in more detail.

```python title="stopwatch01.py" hl_lines="1 2"
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

The first line imports `App` class, which is the base class for all Textual apps.
The second line imports two builtin widgets: [`Footer`](widgets/footer.md) which shows a bar at the bottom of the screen with bound keys, and [`Header`](widgets/header) which shows a title at the top of the screen.
Widgets are re-usable components responsible for managing a part of the screen.
We will cover how to build widgets in this tutorial.

The following lines define the app itself:

```python title="stopwatch01.py" hl_lines="5-19"
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

The App class is where most of the logic of Textual apps is written. It is responsible for loading configuration, setting up widgets, handling keys, and more.

Here's what the above app defines:

- `BINDINGS` is a list of tuples that maps (or *binds*) keys to actions in your app. The first value in the tuple is the key; the second value is the name of the action; the final value is a short description. We have a single binding which maps the ++d++ key on to the "toggle_dark" action. See [key bindings](./guide/input.md#bindings) in the guide for details.

-  `compose()` is where we construct a user interface with widgets. The `compose()` method may return a list of widgets, but it is generally easier to _yield_ them (making this method a generator). In the example code we yield an instance of each of the widget classes we imported, i.e. `Header()` and `Footer()`.

- `action_toggle_dark()` defines an _action_ method. Actions are methods beginning with `action_` followed by the name of the action. The `BINDINGS` list above tells Textual to run this action when the user hits the ++d++ key. See [actions](./guide/actions.md) in the guide for details.

```python title="stopwatch01.py" hl_lines="22-24"
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

The final three lines create an instance of the app and calls the [run()][textual.app.App.run] method which puts your terminal in to *application mode* and runs the app until you exit with ++ctrl+c++. This happens within a `__name__ == "__main__"` block so we could run the app with `python stopwatch01.py` or import it as part of a larger project.

## Designing a UI with widgets

Textual has a large number of [builtin widgets](./widget_gallery.md).
For our app we will need new widgets, which we can create by extending and combining the builtin widgets.

Before we dive in to building widgets, let's first sketch a design for the app &mdash; so we know what we're aiming for.


<div class="excalidraw">
--8<-- "docs/images/stopwatch.excalidraw.svg"
</div>

### Custom widgets

We need a `Stopwatch` widget composed of the following _child_ widgets:

- A "Start" button
- A "Stop" button
- A "Reset" button
- A time display

Let's add those to the app.
Just a skeleton for now, we will add the rest of the features as we go.

```python title="stopwatch02.py" hl_lines="2-3 6-7 10-18 30"
--8<-- "docs/examples/tutorial/stopwatch02.py"
```

We've imported two new widgets in this code: [`Button`](widgets/button.md) for the buttons and [`Digits`](widgets/digits.md) for the time display.
Additionally, we've imported [`Horizontal`][textual.containers.Horizontal] and [`VerticalScroll`][textual.containers.VerticalScroll] from `textual.containers` (as the name of the module suggests, *containers* are widgets which contain other widgets).
We will use these container widgets to define the general layout of our interface.

The `TimeDisplay` is currently very simple, all it does is extend `Digits` without adding any new features. We will flesh this out later.

The `Stopwatch` widget class extends the `HorizontalGroup` container class, which will arrange its children into a horizontal row. The Stopwatch's `compose()` adds those children, which correspond to the components from the sketch above.


#### The buttons

The Button constructor takes a label to be displayed in the button (`"Start"`, `"Stop"`, or `"Reset"`). Additionally, some of the buttons set the following parameters:

- `id` is an identifier we can use to tell the buttons apart in code and apply styles. More on that later.
- `variant` is a string which selects a default style. The "success" variant makes the button green, and the "error" variant makes it red.

### Composing the widgets

The new line in `StopwatchApp.compose()` yields a single `VerticalScroll` which will scroll if the contents don't quite fit. This widget also takes care of key bindings required for scrolling, like ++up++, ++down++, ++pgdn++, ++pgup++, ++home++, ++end++, etc.

When widgets contain other widgets (like `VerticalScroll`) they will typically accept their child widgets as positional arguments.
So the line `yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch())` creates a `VerticalScroll` containing three `Stopwatch` widgets.


### The unstyled app

Let's see what happens when we run `stopwatch02.py`.

```{.textual path="docs/examples/tutorial/stopwatch02.py" title="stopwatch02.py"}
```

The elements of the stopwatch application are there, but it doesn't look much like the sketch. This is because we have yet to apply any _styles_ to our new widgets.

## Writing Textual CSS

Every widget has a `styles` object with a number of attributes that impact how the widget will appear. Here's how you might set white text and a blue background for a widget:

```python
self.styles.background = "blue"
self.styles.color = "white"
```

While it's possible to set all styles for an app this way, it is rarely necessary. Textual has support for CSS (Cascading Style Sheets), a technology used by web browsers. CSS files are data files loaded by your app which contain information about styles to apply to your widgets.

!!! info

    The dialect of CSS used in Textual is greatly simplified over web based CSS and easier to learn.


CSS makes it easy to iterate on the design of your app and enables [live-editing](./guide/devtools.md#live-editing) &mdash; you can edit CSS and see the changes without restarting the app!


Let's add a CSS file to our application.

```python title="stopwatch03.py" hl_lines="24"
--8<-- "docs/examples/tutorial/stopwatch03.py"
```

Adding the `CSS_PATH` class variable tells Textual to load the following file when the app starts:

```css title="stopwatch03.tcss"
--8<-- "docs/examples/tutorial/stopwatch03.tcss"
```

If we run the app now, it will look *very* different.

```{.textual path="docs/examples/tutorial/stopwatch03.py" title="stopwatch03.py"}
```

This app looks much more like our sketch. Let's look at how Textual uses `stopwatch03.tcss` to apply styles.

### CSS basics

CSS files contain a number of _declaration blocks_. Here's the first such block from `stopwatch03.tcss` again:

```css
Stopwatch {
    background: $boost;
    height: 5;
    margin: 1;
    min-width: 50;
    padding: 1;
}
```

The first line tells Textual that the styles should apply to the `Stopwatch` widget. The lines between the curly brackets contain the styles themselves.

Here's how this CSS code changes how the `Stopwatch` widget is displayed.

<div class="excalidraw">
--8<-- "docs/images/stopwatch_widgets.excalidraw.svg"
</div>

- `background: $boost` sets the background color to `$boost`. The `$` prefix picks a pre-defined color from the builtin theme. There are other ways to specify colors such as `"blue"` or `rgb(20,46,210)`.
- `height: 5` sets the height of our widget to 5 lines of text.
- `margin: 1` sets a margin of 1 cell around the `Stopwatch` widget to create a little space between widgets in the list.
- `min-width: 50` sets the minimum width of our widget to 50 cells.
- `padding: 1` sets a padding of 1 cell around the child widgets.


Here's the rest of `stopwatch03.tcss` which contains further declaration blocks:

```css
TimeDisplay {   
    text-align: center;
    color: $foreground-muted;
    height: 3;
}

Button {
    width: 16;
}

#start {
    dock: left;
}

#stop {
    dock: left;
    display: none;
}

#reset {
    dock: right;
}
```

The `TimeDisplay` block aligns text to the center (`text-align:`), sets its color (`color:`), and sets its height (`height:`) to 3 lines.

The `Button` block sets the width (`width:`) of buttons to 16 cells (character widths).

The last 3 blocks have a slightly different format. When the declaration begins with a `#` then the styles will be applied to widgets with a matching "id" attribute. We've set an ID on the `Button` widgets we yielded in `compose`. For instance the first button has `id="start"` which matches `#start` in the CSS.

The buttons have a `dock` style which aligns the widget to a given edge.
The start and stop buttons are docked to the left edge, while the reset button is docked to the right edge.

You may have noticed that the stop button (`#stop` in the CSS) has `display: none;`. This tells Textual to not show the button. We do this because we don't want to display the stop button when the timer is *not* running. Similarly, we don't want to show the start button when the timer is running. We will cover how to manage such dynamic user interfaces in the next section.

### Dynamic CSS

We want our `Stopwatch` widget to have two states: a default state with a Start and Reset button; and a _started_ state with a Stop button. When a stopwatch is started it should also have a green background to indicate it is currently active.

<div class="excalidraw">
--8<-- "docs/images/css_stopwatch.excalidraw.svg"
</div>


We can accomplish this with a CSS _class_. Not to be confused with a Python class, a CSS class is like a tag you can add to a widget to modify its styles. A widget may have any number of CSS classes, which may be added and removed to change its appearance.

Here's the new CSS:

```css title="stopwatch04.tcss" hl_lines="32-52"
--8<-- "docs/examples/tutorial/stopwatch04.tcss"
```

These new rules are prefixed with `.started`. The `.` indicates that `.started` refers to a CSS class called "started". The new styles will be applied only to widgets that have this CSS class.

Some of the new styles have more than one selector separated by a space. The space indicates that the rule should match the second selector if it is a child of the first. Let's look at one of these styles:

```css
.started #start {
    display: none
}
```

The `.started` selector matches any widget with a `"started"` CSS class.
While `#start` matches a widget with an ID of `"start"`.
Combining the two selectors with a space (`.started #start`) creates a new selector that will match the start button *only* if it is also inside a container with a CSS class of "started".

As before, the `display: none` rule will cause any matching widgets to be hidden from view. 

If we were to write this in English, it would be something like: "Hide the start button if the widget is already started".

### Manipulating classes

Modifying a widget's CSS classes is a convenient way to update visuals without introducing a lot of messy display related code.

You can add and remove CSS classes with the [add_class()][textual.dom.DOMNode.add_class] and [remove_class()][textual.dom.DOMNode.remove_class] methods.
We will use these methods to connect the started state to the Start / Stop buttons.

The following code will start or stop the stopwatches in response to clicking a button:

```python title="stopwatch04.py" hl_lines="13-18"
--8<-- "docs/examples/tutorial/stopwatch04.py"
```

The `on_button_pressed` method is an *event handler*. Event handlers are methods called by Textual in response to an *event* such as a key press, mouse click, etc.
Event handlers begin with `on_` followed by the name of the event they will handle.
Hence `on_button_pressed` will handle the button pressed event.

See the guide on [message handlers](./guide/events.md#message-handlers) for the details on how to write event handlers.

If you run `stopwatch04.py` now you will be able to toggle between the two states by clicking the first button:

```{.textual path="docs/examples/tutorial/stopwatch04.py" title="stopwatch04.py" press="tab,tab,tab,enter"}
```

When the button event handler adds or removes the `"started"` CSS class, Textual re-applies the CSS and updates the visuals.


## Reactive attributes

A recurring theme in Textual is that you rarely need to explicitly update a widget's visuals.
It is possible: you can call [refresh()][textual.widget.Widget.refresh] to display new data.
However, Textual prefers to do this automatically via _reactive_ attributes.

Reactive attributes work like any other attribute, such as those you might set in an `__init__` method, but allow Textual to detect when you assign to them, in addition to some other [*superpowers*](./guide/reactivity.md).

To add a reactive attribute, import [reactive][textual.reactive.reactive] and create an instance in your class scope.

Let's add reactives to our stopwatch to calculate and display the elapsed time.

```python title="stopwatch05.py" hl_lines="1 5 12-27 45"
--8<-- "docs/examples/tutorial/stopwatch05.py"
```

We have added two reactive attributes to the `TimeDisplay` widget: `start_time` will contain the time the stopwatch was started (in seconds), and `time` will contain the time to be displayed in the `Stopwatch` widget.

Both attributes will be available on `self` as if you had assigned them in `__init__`.
If you write to either of these attributes the widget will update automatically.

!!! info

    The `monotonic` function in this example is imported from the standard library `time` module.
    It is similar to `time.time` but won't go backwards if the system clock is changed.

The first argument to `reactive` may be a default value for the attribute or a callable that returns a default value.
We set the default for `start_time` to the `monotonic` function which will be called to initialize the attribute with the current time when the `TimeDisplay` is added to the app.
The `time` attribute has a simple float as the default, so `self.time` will be initialized to `0`.


The `on_mount` method is an event handler called when the widget is first added to the application (or _mounted_ in Textual terminology). In this method we call [set_interval()][textual.message_pump.MessagePump.set_interval] to create a timer which calls `self.update_time` sixty times a second. This `update_time` method calculates the time elapsed since the widget started and assigns it to `self.time` &mdash; which brings us to one of Reactive's super-powers.

If you implement a method that begins with `watch_` followed by the name of a reactive attribute, then the method will be called when the attribute is modified.
Such methods are known as *watch methods*.

Because `watch_time` watches the `time` attribute, when we update `self.time` 60 times a second we also implicitly call `watch_time` which converts the elapsed time to a string and updates the widget with a call to `self.update`.
Because this happens automatically, we don't need to pass in an initial argument to `TimeDisplay`.

The end result is that the `Stopwatch` widgets show the time elapsed since the widget was created:

```{.textual path="docs/examples/tutorial/stopwatch05.py" title="stopwatch05.py"}
```

We've seen how we can update widgets with a timer, but we still need to wire up the buttons so we can operate stopwatches independently.

### Wiring buttons

We need to be able to start, stop, and reset each stopwatch independently. We can do this by adding a few more methods to the `TimeDisplay` class.


```python title="stopwatch06.py" hl_lines="14 18 22 30-44 50-61"
--8<-- "docs/examples/tutorial/stopwatch06.py"
```

Here's a summary of the changes made to `TimeDisplay`.

- We've added a `total` reactive attribute to store the total time elapsed between clicking the start and stop buttons.
- The call to `set_interval` has grown a `pause=True` argument which starts the timer in pause mode (when a timer is paused it won't run until [resume()][textual.timer.Timer.resume] is called). This is because we don't want the time to update until the user hits the start button.
- The `update_time` method now adds `total` to the current time to account for the time between any previous clicks of the start and stop buttons.
- We've stored the result of `set_interval` which returns a [Timer](textual.timer.Timer) object. We will use this to _resume_ the timer when we start the Stopwatch.
- We've added `start()`, `stop()`, and `reset()` methods.

In addition, the `on_button_pressed` method on `Stopwatch` has grown some code to manage the time display when the user clicks a button. Let's look at that in detail:

```python
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()
```

This code supplies missing features and makes our app useful. We've made the following changes.

- The first line retrieves `id` attribute of the button that was pressed. We can use this to decide what to do in response.
- The second line calls [`query_one`][textual.dom.DOMNode.query_one] to get a reference to the `TimeDisplay` widget.
- We call the method on `TimeDisplay` that matches the pressed button.
- We add the `"started"` class when the Stopwatch is started (`self.add_class("started")`), and remove it (`self.remove_class("started")`) when it is stopped. This will update the Stopwatch visuals via CSS.

If you run `stopwatch06.py` you will be able to use the stopwatches independently.

```{.textual path="docs/examples/tutorial/stopwatch06.py" title="stopwatch06.py" press="tab,enter,tab,enter,tab"}
```

The only remaining feature of the Stopwatch app left to implement is the ability to add and remove stopwatches.

## Dynamic widgets

The Stopwatch app creates widgets when it starts via the `compose` method. We will also need to create new widgets while the app is running, and remove widgets we no longer need. We can do this by calling [mount()][textual.widget.Widget.mount] to add a widget, and [remove()][textual.widget.Widget.remove] to remove a widget.

Let's use these methods to implement adding and removing stopwatches to our app.

```python title="stopwatch.py" hl_lines="78-79 86 88-92 94-98"
--8<-- "docs/examples/tutorial/stopwatch.py"
```

Here's a summary of the changes:

- The `VerticalScroll` object in `StopWatchApp` grew a `"timers"` ID.
- Added `action_add_stopwatch` to add a new stopwatch.
- Added `action_remove_stopwatch` to remove a stopwatch.
- Added keybindings for the actions.

The `action_add_stopwatch` method creates and mounts a new stopwatch. Note the call to [query_one()][textual.dom.DOMNode.query_one] with a CSS selector of `"#timers"` which gets the timer's container via its ID.
Once mounted, the new Stopwatch will appear in the terminal. That last line in `action_add_stopwatch` calls [scroll_visible()][textual.widget.Widget.scroll_visible] which will scroll the container to make the new `Stopwatch` visible (if required).

The `action_remove_stopwatch` function calls [query()][textual.dom.DOMNode.query] with a CSS selector of `"Stopwatch"` which gets all the `Stopwatch` widgets.
If there are stopwatches then the action calls [last()][textual.css.query.DOMQuery.last] to get the last stopwatch, and [remove()][textual.css.query.DOMQuery.remove] to remove it.

If you run `stopwatch.py` now you can add a new stopwatch with the ++a++ key and remove a stopwatch with ++r++.

```{.textual path="docs/examples/tutorial/stopwatch.py" title="stopwatch.py" press="d,a,a,a,a,a,a,a,tab,enter,tab"}
```

## What next?

Congratulations on building your first Textual application! This tutorial has covered a lot of ground. If you are the type that prefers to learn a framework by coding, feel free. You could tweak `stopwatch.py` or look through the examples.

Read the guide for the full details on how to build sophisticated TUI applications with Textual.
