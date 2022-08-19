# Introduction

Welcome to the Textual Introduction!

By the end of this page you should have a good idea of the steps involved in creating an application with Textual.


## Stopwatch Application

We're going to build a stopwatch app. This app will display the elapsed time since the user hit a "Start" button. The user will be able to stop / resume / reset each stopwatch in addition to adding or removing them.

This is a simple yet **fully featured** app &mdash; you could distribute this app if you wanted to!

Here's what the finished app will look like:


```{.textual path="docs/examples/introduction/stopwatch.py"}
```

If you want to try this out before reading the rest of this introduction (we recommend it), navigate to "docs/examples/introduction" within the repository and run the following:

```bash
python stopwatch.py
```

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

Let's example stopwatch01.py in more detail.

```python title="stopwatch01.py" hl_lines="1 2"
--8<-- "docs/examples/introduction/stopwatch01.py"
```


The first line imports the Textual `App` class. The second line imports two builtin widgets: `Footer` which shows available keys and `Header` which shows a title and the current time.

Widgets are re-usable components responsible for managing a part of the screen. We will cover how to build such widgets in this introduction.


```python title="stopwatch01.py" hl_lines="5-15"
--8<-- "docs/examples/introduction/stopwatch01.py"
```

The App class is where most of the logic of Textual apps is written. It is responsible for loading configuration, setting up widgets, handling keys, and more.

There are three methods in our stopwatch app currently. 

-  **`compose()`** is where we construct a user interface with widgets. The `compose()` method may return a list of widgets, but it is generally easier to _yield_ them (making this method a generator). In the example code we yield instances of the widget classes we imported, i.e. the header and the footer.

- **`on_load()`** is an _event handler_ method. Event handlers are called by Textual in response to external events like keys and mouse movements, and internal events needed to manage your application. Event handler methods begin with `on_` followed by the name of the event (in lower case). Hence, `on_load` it is called in response to the Load event which is sent just after the app starts. We're using this event to call `App.bind()` which connects a key to an _action_.

- **`action_toggle_dark()`** defines an _action_ method. Actions are methods beginning with `action_` followed by the name of the action. The call to `bind()` in `on_load()` binds this action to the ++d++ key. The body of this method flips the state of the `dark` boolean to toggle dark mode.

!!! note

    You may have noticed that the the `toggle_dark` doesn't do anything to explicitly change the _screen_, and yet hitting ++d++ refreshes and updates the whole terminal. This is an example of _reactivity_. Changing certain attributes will schedule an automatic update.


```python title="stopwatch01.py" hl_lines="17-19"
--8<-- "docs/examples/introduction/stopwatch01.py"
```

The last lines in "stopwatch01.py" may be familiar to you. We create an instance of our app class, and call `run()` within a `__name__ == "__main__"` conditional block. This is so that we could import `app` if we want to. Or we could run it with `python stopwatch01.py`. 

## Creating a custom widget

The header and footer were builtin widgets. For our stopwatch application we will need to build a custom widget for stopwatches.

Let's sketch out what we are trying to achieve here:

<div class="excalidraw">
--8<-- "docs/images/stopwatch.excalidraw.svg"
</div>


An individual stopwatch consists of several parts, which themselves can be widgets.

Out stopwatch widgets is going to need the following widgets:

- A "start" button
- A "stop" button
- A "reset" button
- A time display

Textual has a builtin `Button` widgets which takes care of the first three components. All we need to build is the time display which will show the elapsed time in HOURS:MINUTES:SECONDS format, and the stopwatch itself.

Let's add those to our app:

```python title="stopwatch02.py" hl_lines="3 6-7 10-15 22 31"
--8<-- "docs/examples/introduction/stopwatch02.py"
```

### New widgets

We've imported two new widgets in this code: Button, which creates a clickable button, and Static which is a base class for a simple control. We've also imported `Container` from `textual.layout`. As the name suggests, `Container` is a Widget which contains other widgets. We will use this container to form a scrolling list of stopwatches.

We're extending Static as a foundation for our `TimeDisplay` widget. There are no methods on this class yet. 

The Stopwatch also extends Static to define a new widget. This class has a `compose()` method which yields its _child_ widgets, consisting of of three `Button` objects and a single `TimeDisplay`. These are all we need to build a stopwatch like the sketch.

The Button constructor takes a label to be displayed to the user ("Start", "Stop", or "Reset")  so they know what will happen when they click on it. There are two additional parameters to the Button constructor we are using:

- **`id`** is an identifier so we can tell the buttons apart in code. We can also use this to style the buttons. More on that later.
- **`variant`** is a string which selects a default style. The "success" variant makes the button green, and the "error" variant makes it red.

### Composing the widgets

To see our widgets with we need to yield them from the app's `compose()` method:

This new line in `Stopwatch.compose()` adds a single `Container` object which will create a scrolling list. The constructor for `Container` takes its _child_ widgets as positional arguments, to which we pass three instances of the `Stopwatch` we just built.

### Setting the CSS path

The `StopwatchApp` constructor has a new argument: `css_path` is set to the file `stopwatch02.css` which is blank:

```python title="stopwatch02.css" 
--8<-- "docs/examples/introduction/stopwatch02.css"
```

### The unstyled app

Let's see what happens when we run "stopwatch02.py":

```{.textual path="docs/examples/introduction/stopwatch02.py" title="stopwatch02.py"}
```

The elements of the stopwatch application are there. The buttons are clickable and you can scroll the container, but it doesn't look much like the sketch. This is because we have yet to add any _styles_ to the CSS file.

Textual uses CSS files to define what widgets look like. With CSS we can apply styles for color, borders, alignment, positioning, animation, and more.

!!! note

    Don't worry if you have never worked with CSS before. The dialect of CSS we use is greatly simplified over web based CSS and easy to learn!

## Writing Textual CSS

