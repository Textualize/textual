# Tutorial

Welcome to the Textual Tutorial!

By the end of this page you should have a solid understanding of app development with Textual. 

!!! quote

    I've always thought the secret sauce in making a popular framework is for it to be fun.
    
    &mdash; **Will McGugan** (creator of Rich and Textual)


## Stopwatch Application

We're going to build a stopwatch application. This application should show a list of stopwatches with buttons to start, stop, and reset the stopwatches. We also want the user to be able to add and remove stopwatches as required.

This will be a simple yet **fully featured** app &mdash; you could distribute this app if you wanted to!

Here's what the finished app will look like:


```{.textual path="docs/examples/tutorial/stopwatch.py" press="tab,enter,_,tab,enter,_,tab,_,enter,_,tab,enter,_,_"}
```

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

We're a big fan of Python type hints at Textualize. If you haven't encountered type hinting, it's a way to express the types of your data, parameters, and return values. Type hinting allows tools like [Mypy](https://mypy.readthedocs.io/en/stable/) to catch bugs before your code runs.

The following function contains type hints:

```python
def repeat(text: str, count: int) -> str:
    """Repeat a string a given number of times."""
    return text * count
```

Parameter types follow a colon. So `text: str` indicates that `text` requires a string and `count: int` means that `count` requires an integer.

Return types follow `->`. So `-> str:` indicates this method returns a string.


## The App class

The first step in building a Textual app is to import and extend the `App` class. Here's our basic app class with a few methods we will cover below.

```python title="stopwatch01.py" 
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

If you run this code, you should see something like the following:


```{.textual path="docs/examples/tutorial/stopwatch01.py"}
```

Hit the ++d++ key to toggle between light and dark mode.

```{.textual path="docs/examples/tutorial/stopwatch01.py" press="d" title="TimerApp + dark"}
```

Hit ++ctrl+c++ to exit the app and return to the command prompt.

### A closer look at the App class

Let's examine stopwatch01.py in more detail.

```python title="stopwatch01.py" hl_lines="1 2"
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

The first line imports the Textual `App` class. The second line imports two builtin widgets: `Footer` which shows available keys and `Header` which shows a title and the current time. Widgets are re-usable components responsible for managing a part of the screen. We will cover how to build such widgets in this tutorial.

The following lines define the app itself:

```python title="stopwatch01.py" hl_lines="5-17"
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

The App class is where most of the logic of Textual apps is written. It is responsible for loading configuration, setting up widgets, handling keys, and more.

Here's what the above app defines:

- `BINDINGS` is a list of tuples that maps (or *binds*) keys to actions in your app. The first value in the tuple is the key; the second value is the name of the action; the final value is a short description. The name of the action (`"toggle_dark"`) is mapped on to the `"action_toggle_dark"` method (see below) which is called when you hit the ++d++ key.

-  `compose()` is where we construct a user interface with widgets. The `compose()` method may return a list of widgets, but it is generally easier to _yield_ them (making this method a generator). In the example code we yield instances of the widget classes we imported, i.e. the header and the footer.

- `action_toggle_dark()` defines an _action_ method. Actions are methods beginning with `action_` followed by the name of the action. The `BINDINGS` list above tells Textual to run this action when the user hits the ++d++ key.

```python title="stopwatch01.py" hl_lines="20-22"
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

The final three lines create an instance of the app and call [run()][textual.app.App.run] method within a `__name__ == "__main__"` block. This is so we can call `python stopwatch01.py` to run the app, or we could import `stopwatch01` as part of a larger application.

It's the run method that puts the terminal in to *application mode* so that Textual can take over updating the terminal and handling keyboard and mouse input.

## Designing a UI with widgets

The header and footer are builtin widgets. For our Stopwatch application we will need to build custom widgets.

Let's sketch out a design for our app:

<div class="excalidraw">
--8<-- "docs/images/stopwatch.excalidraw.svg"
</div>

We will need to build a `Stopwatch` widget composed of the following _child_ widgets:

- A "Start" button
- A "Stop" button
- A "Reset" button
- A time display

Textual has a builtin `Button` widget which takes care of the first three components. All we need to build is the time display widget which will show the elapsed time and the stopwatch widget itself.

Let's add those to the app. Just a skeleton for now, we will add the rest of the features as we go.

```python title="stopwatch02.py" hl_lines="3 6-7 10-18 30"
--8<-- "docs/examples/tutorial/stopwatch02.py"
```

### Extending widget classes

We've imported two new widgets in this code: `Button`, which creates a clickable button, and `Static` which is a base class for a simple control. We've also imported `Container` from `textual.layout`. As the name suggests, `Container` is a Widget which contains other widgets. We will use this container to create a scrolling list of stopwatches.

We're extending Static as a foundation for our `TimeDisplay` widget. There are no methods on this class yet. 

The Stopwatch class extends Static to define a new widget. This class has a `compose()` method which yields its child widgets, consisting of three `Button` objects and a single `TimeDisplay`. These are all we need to build a stopwatch as in the sketch.

The Button constructor takes a label to be displayed in the button ("Start", "Stop", or "Reset"). Additionally some of the buttons set the following parameters:

- `id` is an identifier we can use to tell the buttons apart in code and apply styles. More on that later.
- `variant` is a string which selects a default style. The "success" variant makes the button green, and the "error" variant makes it red. 

### Composing the widgets

To add widgets to our application we first need to yield them from the app's `compose()` method:

The new line in `Stopwatch.compose()` yields a single `Container` object which will create a scrolling list of stopwatches. When classes contain other widgets (like `Container`) they will typically accept their child widgets as positional arguments. We want to start the app with three stopwatches, so we construct three `Stopwatch` instances and pass them to the container's constructor.


### The unstyled app

Let's see what happens when we run "stopwatch02.py".

```{.textual path="docs/examples/tutorial/stopwatch02.py" title="stopwatch02.py"}
```

The elements of the stopwatch application are there. The buttons are clickable and you can scroll the container but it doesn't look like the sketch. This is because we have yet to apply any _styles_ to our new widgets.

## Writing Textual CSS

Every widget has a `styles` object with a number of attributes that impact how the widget will appear. Here's how you might set white text and a blue background for a widget:

```python
self.styles.background = "blue"
self.styles.color = "white"
```

!!! info inline end

    Don't worry if you have never worked with CSS before. The dialect of CSS we use is greatly simplified over web based CSS and easy to learn!

    
While it's possible to set all styles for an app this way, it is rarely necessary. Textual has support for CSS (Cascading Style Sheets), a technology used by web browsers. CSS files are data files loaded by your app which contain information about styles to apply to your widgets. 

Let's add a CSS file to our application.

```python title="stopwatch03.py" hl_lines="37"
--8<-- "docs/examples/tutorial/stopwatch03.py"
```

Adding the `css_path` attribute to the app constructor tells Textual to load the following file when it starts the app:

```sass title="stopwatch03.css" 
--8<-- "docs/examples/tutorial/stopwatch03.css"
```

If we run the app now, it will look *very* different.

```{.textual path="docs/examples/tutorial/stopwatch03.py" title="stopwatch03.py"}
```

This app looks much more like our sketch. Textual has read style information from `stopwatch03.css` and applied it to the widgets. 

### CSS basics

CSS files contain a number of _declaration blocks_. Here's the first such block from `stopwatch03.css` again:

```sass 
Stopwatch {
    layout: horizontal;
    background: $panel-darken-1;
    height: 5;
    padding: 1;
    margin: 1;
}
```

The first line tells Textual that the styles should apply to the `Stopwatch` widget. The lines between the curly brackets contain the styles themselves.

Here's how this CSS code changes how the `Stopwatch` widget is displayed.

<div class="excalidraw">
--8<-- "docs/images/stopwatch_widgets.excalidraw.svg"
</div>

- `layout: horizontal` aligns child widgets horizontally from left to right.
- `background: $panel-darken-1` sets the background color to `$panel-darken-1`. The `$` prefix picks a pre-defined color from the builtin theme. There are other ways to specify colors such as `"blue"` or `rgb(20,46,210)`.
- `height: 5` sets the height of our widget to 5 lines of text.
- `padding: 1` sets a padding of 1 cell around the child widgets.
- `margin: 1` sets a margin of 1 cell around the Stopwatch widget to create a little space between widgets in the list.


Here's the rest of `stopwatch03.css` which contains further declaration blocks:

```sass
TimeDisplay {
    content-align: center middle;
    opacity: 60%;
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

The `TimeDisplay` block aligns text to the center (`content-align`), fades it slightly (`opacity`), and sets its height (`height`) to 3 lines.

The `Button` block sets the width (`width`) of buttons to 16 cells (character widths).

The last 3 blocks have a slightly different format. When the declaration begins with a `#` then the styles will be applied to widgets with a matching "id" attribute. We've set an ID on the Button widgets we yielded in compose. For instance the first button has `id="start"` which matches `#start` in the CSS.

The buttons have a `dock` style which aligns the widget to a given edge. The start and stop buttons are docked to the left edge, while the reset button is docked to the right edge.

You may have noticed that the stop button (`#stop` in the CSS) has `display: none;`. This tells Textual to not show the button. We do this because we don't want to display the stop button when the timer is *not* running. Similarly we don't want to show the start button when the timer is running. We will cover how to manage such dynamic user interfaces in the next section.

### Dynamic CSS

We want our Stopwatch widget to have two states: a default state with a Start and Reset button; and a _started_ state with a Stop button. When a stopwatch is started it should also have a green background and bold text.

We can accomplish this with a CSS _class_. Not to be confused with a Python class, a CSS class is like a tag you can add to a widget to modify its styles.

Here's the new CSS:

```sass title="stopwatch04.css" hl_lines="33-53"
--8<-- "docs/examples/tutorial/stopwatch04.css"
```

These new rules are prefixed with `.started`. The `.` indicates that `.started` refers to a CSS class called "started". The new styles will be applied only to widgets that have this CSS class.

<div class="excalidraw">
--8<-- "docs/images/css_stopwatch.excalidraw.svg"
</div>

Some of the new styles have more than one selector separated by a space. The space indicates that the rule should match the second selector if it is a child of the first. Let's look at one of these styles:

```sass
.started #start {
    display: none
}
```

The `.started` selector matches any widget with a `"started"` CSS class. While `#start` matches a child widget with an ID of "start". So it matches the Start button only for Stopwatches in a started state.

The rule is `"display: none"` which tells Textual to hide the button.

### Manipulating classes

Modifying a widget's CSS classes it a convenient way to modify visuals without introducing a lot of messy display related code.

You can add and remove CSS classes with the [add_class()][textual.dom.DOMNode.add_class] and [remove_class()][textual.dom.DOMNode.remove_class] methods. We will use these methods to connect the started state to the Start / Stop buttons.

The following code will start or stop the stopwatches in response to clicking a button.

```python title="stopwatch04.py" hl_lines="13-18"
--8<-- "docs/examples/tutorial/stopwatch04.py"
```

The `on_button_pressed` method is an *event handler*. Event handlers are methods called by Textual in response to an *event* such as a key press, mouse click, etc. Event handlers begin with `on_` followed by the name of the event they will handler. Hence `on_button_pressed` will handle the button pressed event.

If you run "stopwatch04.py" now you will be able to toggle between the two states by clicking the first button:

```{.textual path="docs/examples/tutorial/stopwatch04.py" title="stopwatch04.py" press="tab,tab,tab,enter,_,_"}
```

## Reactive attributes

A recurring theme in Textual is that you rarely need to explicitly update a widget. It is possible: you can call [refresh()][textual.widget.Widget.refresh] to display new data. However, Textual prefers to do this automatically via _reactive_ attributes.

You can declare a reactive attribute with [reactive][textual.reactive.reactive]. Let's use this feature to create a timer that displays elapsed time and keeps it updated.

```python title="stopwatch05.py" hl_lines="1 5 12-27"
--8<-- "docs/examples/tutorial/stopwatch05.py"
```

We have added two reactive attributes: `start_time` will contain the time in seconds when the stopwatch was started, and `time` will contain the time to be displayed on the Stopwatch.

Both attributes will be available on `self` as if you had assigned them in `__init__`. If you write to either of these attributes the widget will update automatically.

!!! info 

    The `monotonic` function in this example is imported from the standard library `time` module. It is similar to `time.time` but won't go backwards if the system clock is changed.

The first argument to `reactive` may be a default value or a callable that returns the default value. The default for `start_time` is `monotonic`. When `TimeDisplay` is added to the app, the `start_time` attribute will be set to the result of `monotonic()`.

The `time` attribute has a simple float as the default value, so `self.time` will be `0` on start.


The `on_mount` method is an event handler which is called then the widget is first added to the application (or _mounted_). In this method we call [set_interval()][textual.message_pump.MessagePump.set_interval] to create a timer which calls `self.update_time` sixty times a second. This `update_time` method calculates the time elapsed since the widget started and assigns it to `self.time`. Which brings us to one of Reactive's super-powers.

If you implement a method that begins with `watch_` followed by the name of a reactive attribute (making it a _watch method_), that method will be called when the attribute is modified.

Because `watch_time` watches the `time` attribute, when we update `self.time` 60 times a second we also implicitly call `watch_time` which converts the elapsed time in to a string and updates the widget with a call to `self.update`.

The end result is that the `Stopwatch` widgets show the time elapsed since the widget was created:

```{.textual path="docs/examples/tutorial/stopwatch05.py" title="stopwatch05.py"}
```

We've seen how we can update widgets with a timer, but we still need to wire up the buttons so we can operate Stopwatches independently.

### Wiring buttons

We need to be able to start, stop, and reset each stopwatch independently. We can do this by adding a few more methods to the `TimeDisplay` class.


```python title="stopwatch06.py" hl_lines="14 30-44 50-61"
--8<-- "docs/examples/tutorial/stopwatch06.py"
```

Here's a summary of the changes made to `TimeDisplay`.

- We've added a `total` reactive attribute to store the total time elapsed between clicking that start and stop buttons.
- The call to `set_interval` has grown a `pause=True` argument which starts the timer in pause mode (when a timer is paused it won't run until [resume()][textual.timer.Timer.resume] is called). This is because we don't want the time to update until the user hits the start button.
- We've stored the result of `set_interval` which returns a Timer object. We will use this later to _resume_ the timer when we start the Stopwatch.
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

- The first line retrieves the button's ID, which we will use to decide what to do in response.
- The second line calls `query_one` to get a reference to the `TimeDisplay` widget.
- We call the method on `TimeDisplay` that matches the pressed button.
- We add the "started" class when the Stopwatch is started (`self.add_class("started)`), and remove it (`self.remove_class("started")`) when it is stopped. This will update the Stopwatch visuals via CSS.

If you run stopwatch06.py you will be able to use the stopwatches independently.

```{.textual path="docs/examples/tutorial/stopwatch06.py" title="stopwatch06.py" press="tab,enter,_,_,tab,enter,_,tab"}
```

The only remaining feature of the Stopwatch app left to implement is the ability to add and remove timers.

## Dynamic widgets

It's convenient to build a user interface with the `compose` method. We may also want to add or remove widgets while the app is running.

To add a new child widget call `mount()` on the parent. To remove a widget, call its `remove()` method.

Let's use these to implement adding and removing stopwatches to our app.

```python title="stopwatch.py" hl_lines="76-77 86-90 92-96"
--8<-- "docs/examples/tutorial/stopwatch.py"
```

Here's a summary of the changes:

- Added `action_add_stopwatch` to add a new stopwatch.
- Added `action_remove_stopwatch` to remove a stopwatch.
- Added keybindings for the actions.

The `action_add_stopwatch` method creates and mounts a new stopwatch. Note the call to [query_one()][textual.dom.DOMNode.query_one] with a CSS selector of `"#timers"` which gets the timer's container via its ID. Once mounted, the new Stopwatch will appear in the terminal. That last line in `action_add_stopwatch` calls [scroll_visible()][textual.widget.Widget.scroll_visible] which will scroll the container to make the new Stopwatch visible (if required).

The `action_remove_stopwatch` function calls [query()][textual.dom.DOMNode.query] with a CSS selector of `"Stopwatch"` which gets all the `Stopwatch` widgets. If there are stopwatches then the action calls [last()][textual.css.query.DOMQuery.last] to get the last stopwatch, and [remove()][textual.css.query.DOMQuery.remove] to remove it.

If you run `stopwatch.py` now you can add a new stopwatch with the ++a++ key and remove a stopwatch with ++r++.

```{.textual path="docs/examples/tutorial/stopwatch.py" press="d,a,a,a,a,a,a,a,tab,enter,_,_,_,_,tab,_"}
```

## What next?

Congratulations on building your first Textual application! This tutorial has covered a lot of ground. If you are the type that prefers to learn a framework by coding, feel free. You could tweak stopwatch.py or look through the examples.

Read the guide for the full details on how to build sophisticated TUI applications with Textual.
