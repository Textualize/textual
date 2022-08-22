# Introduction

Welcome to the Textual Introduction!

By the end of this page you should have a good idea of the steps involved in creating an application with Textual.

!!! quote

    This page goes in to more detail than you may expect from an introduction. I like documentation to have complete working examples and I wanted the first app to be realistic. 
    
    &mdash; **Will McGugan** (creator of Rich and Textual)




## Stopwatch Application

We're going to build a stopwatch app. This app will display the elapsed time since the user hit a "Start" button. The user will be able to stop, resume, and reset each stopwatch in addition to adding or removing them.

This will be a simple yet **fully featured** app &mdash; you could distribute this app if you wanted to!

Here's what the finished app will look like:


```{.textual path="docs/examples/introduction/stopwatch.py"}
```

### Try the code

If you want to try this out before reading the rest of this introduction (we recommend it), navigate to "docs/examples/introduction" within the repository and run the following:

**TODO**: instructions how to checkout repo

```bash
python stopwatch.py
```

## Type hints (in brief)

We're a big fan of Python type hints at Textualize. If you haven't encountered type hinting, its a way to express the types of your data, parameters, and returns. Type hinting allows tools like [Mypy](https://mypy.readthedocs.io/en/stable/) to catch potential bugs before your code runs.

The following function contains type hints:

```python
def repeat(text: str, count: int) -> str:
    return text * count
```

- Parameter types follow a colon, so `text: str` means that `text` should be a string and `count: int` means that `count` should be an integer.
- Return types follow `->` So `-> str:` says that this method returns a string.


!!! note

    Type hints are entirely optional in Textual. We've included them in the example code but it's up to you wether you add them to your own projects.

## The App class

The first step in building a Textual app is to import and extend the `App` class. Here's our basic app class with a few methods which we will cover below.

```python title="stopwatch01.py" 
--8<-- "docs/examples/introduction/stopwatch01.py"
```

If you run this code, you should see something like the following:


```{.textual path="docs/examples/introduction/stopwatch01.py"}
```

Hit the ++d++ key to toggle dark mode.

```{.textual path="docs/examples/introduction/stopwatch01.py" press="d" title="TimerApp + dark"}
```

Hit ++ctrl+c++ to exit the app and return to the command prompt.

### Looking at the code

Let's examine stopwatch01.py in more detail.

```python title="stopwatch01.py" hl_lines="1 2"
--8<-- "docs/examples/introduction/stopwatch01.py"
```


The first line imports the Textual `App` class. The second line imports two builtin widgets: `Footer` which shows available keys and `Header` which shows a title and the current time.

Widgets are re-usable components responsible for managing a part of the screen. We will cover how to build such widgets in this introduction.


```python title="stopwatch01.py" hl_lines="5-19"
--8<-- "docs/examples/introduction/stopwatch01.py"
```

The App class is where most of the logic of Textual apps is written. It is responsible for loading configuration, setting up widgets, handling keys, and more.

There are three methods in our stopwatch app currently. 

-  **`compose()`** is where we construct a user interface with widgets. The `compose()` method may return a list of widgets, but it is generally easier to _yield_ them (making this method a generator). In the example code we yield instances of the widget classes we imported, i.e. the header and the footer.

- **`on_load()`** is an _event handler_ method. Event handlers are called by Textual in response to external events like keys and mouse movements, and internal events needed to manage your application. Event handler methods begin with `on_` followed by the name of the event (in lower case). Hence, `on_load` it is called in response to the Load event which is sent just after the app starts. We're using this event to call `App.bind()` which connects a key to an _action_.

- **`action_toggle_dark()`** defines an _action_ method. Actions are methods beginning with `action_` followed by the name of the action. The call to `bind()` in `on_load()` binds this the ++d++ key to this action. The body of this method flips the state of the `dark` boolean to toggle dark mode.

!!! note

    You may have noticed that the the `toggle_dark` doesn't do anything to explicitly change the _screen_, and yet hitting ++d++ refreshes and updates the whole terminal. This is an example of _reactivity_. Changing certain attributes will schedule an automatic update.


```python title="stopwatch01.py" hl_lines="22-24"
--8<-- "docs/examples/introduction/stopwatch01.py"
```

The last lines in "stopwatch01.py" may be familiar to you. We create an instance of our app class, and call `run()` within a `__name__ == "__main__"` conditional block. This is so that we could import `app` if we want to. Or we could run it with `python stopwatch01.py`. 

## Creating a custom widget

The header and footer are builtin widgets. For our Stopwatch application we will need to build custom widgets.

Let's sketch out a design for our app:

<div class="excalidraw">
--8<-- "docs/images/stopwatch.excalidraw.svg"
</div>

We will need to build a `Stopwatch` widget composed of the following _child_ widgets:

- A "start" button
- A "stop" button
- A "reset" button
- A time display

Textual has a builtin `Button` widgets which takes care of the first three components. All we need to build is the time display which will show the elapsed time in HOURS:MINUTES:SECONDS format, and the stopwatch itself.

Let's add those to the app. Just a skeleton for now, we will add the rest of the features as we go.

```python title="stopwatch02.py" hl_lines="3 6-7 10-18 28"
--8<-- "docs/examples/introduction/stopwatch02.py"
```

### Extending widget classes

We've imported two new widgets in this code: `Button`, which creates a clickable button, and `Static` which is a base class for a simple control. We've also imported `Container` from `textual.layout`. As the name suggests, `Container` is a Widget which contains other widgets. We will use this container to create a scrolling list of stopwatches.

We're extending Static as a foundation for our `TimeDisplay` widget. There are no methods on this class yet. 

The Stopwatch class also extends Static to define a new widget. This class has a `compose()` method which yields its child widgets, consisting of of three `Button` objects and a single `TimeDisplay`. These are all we need to build a stopwatch as in the sketch.

The Button constructor takes a label to be displayed in the button ("Start", "Stop", or "Reset"). There are two additional parameters to the Button constructor we are using:

- **`id`** is an identifier we can use to tell the buttons apart in code and apply styles. More on that later.
- **`variant`** is a string which selects a default style. The "success" variant makes the button green, and the "error" variant makes it red. 

### Composing the widgets

To see our widgets with we first need to yield them from the app's `compose()` method:

The new line in `Stopwatch.compose()` yields a single `Container` object which will create a scrolling list. When classes contain other widgets (like `Container`) they will typically accept their child widgets as positional arguments. We want to start the app with three stopwatches, so we construct three `Stopwatch` instances as child widgets of the container.


### The unstyled app

Let's see what happens when we run "stopwatch02.py":

```{.textual path="docs/examples/introduction/stopwatch02.py" title="stopwatch02.py"}
```

The elements of the stopwatch application are there. The buttons are clickable and you can scroll the container, but it doesn't look much like the sketch. This is because we have yet to apply any _styles_ to our new widget.

## Writing Textual CSS

Every widget has a `styles` object which contains information regarding how that widget will look. Setting any of the attributes on that styles object will change how Textual displays the widget.

Here's how you might set white text and a blue background for a widget:

```python
self.styles.background = "blue"
self.styles.color = "white"
```

While its possible to set all styles for an app this way, Textual prefers to use CSS.

CSS files are data files loaded by your app which contain information about styles to apply to your widgets. 

!!! note

    Don't worry if you have never worked with CSS before. The dialect of CSS we use is greatly simplified over web based CSS and easy to learn!

Let's add a CSS file to our application.

```python title="stopwatch03.py" hl_lines="39"
--8<-- "docs/examples/introduction/stopwatch03.py"
```

Adding the `css_path` attribute to the app constructor tells textual to load the following file when it starts the app:

```sass title="stopwatch03.css" 
--8<-- "docs/examples/introduction/stopwatch03.css"
```

If we run the app now, it will look *very* different.

```{.textual path="docs/examples/introduction/stopwatch03.py" title="stopwatch03.py"}
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

Here's how the Stopwatch block in the CSS impacts our `Stopwatch` widget:

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

The last 3 blocks have a slightly different format. When the declaration begins with a `#` then the styles will be applied widgets with a matching "id" attribute. We've set an ID attribute on the Button widgets we yielded in compose. For instance the first button has `id="start"` which matches `#start` in the CSS.

The buttons have a `dock` style which aligns the widget to a given edge. The start and stop buttons are docked to the left edge, while the reset button is docked to the right edge.

You may have noticed that the stop button (`#stop` in the CSS) has `display: none;`. This tells Textual to not show the button. We do this because we don't want to dsplay the stop button when the timer is *not* running. Similarly we don't want to show the start button when the timer is running. We will cover how to manage such dynamic user interfaces in the next section.

### Dynamic CSS

We want our Stopwatch widget to have two states: a default state with a Start and Reset button; and a _started_ state with a Stop button. When a stopwatch is started it should also have a green background and bold text.

We can accomplish this with a CSS _class_. Not to be confused with a Python class, a CSS class is like a tag you can add to a widget to modify its styles.

Here's the new CSS:

```sass title="stopwatch04.css" hl_lines="33-53"
--8<-- "docs/examples/introduction/stopwatch04.css"
```

These new rules are prefixed with `.started`. The `.` indicates that `.started` refers to a CSS class called "started". The new styles will be applied only to widgets that have these styles.

Some of the new styles have more than one selector separated by a space. The space indicates that the rule should match the second selector if it is a child of the first. Let's look at one of these styles:

```sass
.started #start {
    display: none
}
```

The purpose of this CSS is to hide the start button when the stopwatch has started. The `.started` selector matches any widget with a "started" CSS class. While "#start" matches a child widget with an id of "start". The rule is applied to the button, so `"display: none"` tells Textual to _hide_ the button.

### Manipulating classes

The easiest way to manipulate visuals with Textual is to modify CSS classes. This way your (Python) code can remain free of display related code which tends to be hard to maintain.

You can add and remove CSS classes with the `add_class()` and `remove_class()` methods. We will use these methods to connect the started state to the Start / Stop buttons.

The following code adds a event handler for the `Button.Pressed` event.

```python title="stopwatch04.py" hl_lines="13-18"
--8<-- "docs/examples/introduction/stopwatch04.py"
```

The `on_button_pressed` event handler is called when the user clicks a button. This method adds the "started" class when the "start" button was clicked, and removes the class when the "stop" button is clicked.

If you run "stopwatch04.py" now you will be able to toggle between the two states by clicking the first button:

```{.textual path="docs/examples/introduction/stopwatch04.py" title="stopwatch04.py" press="tab,tab,tab,enter"}
```


