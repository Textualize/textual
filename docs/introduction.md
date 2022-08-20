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


```python title="stopwatch01.py" hl_lines="5-14"
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


### The unstyled app

Let's see what happens when we run "stopwatch02.py":

```{.textual path="docs/examples/introduction/stopwatch02.py" title="stopwatch02.py"}
```

The elements of the stopwatch application are there. The buttons are clickable and you can scroll the container, but it doesn't look much like the sketch. This is because we have yet to apply any _styles_ to our new widget.

## Writing Textual CSS

Every widget has a `styles` object which contains information regarding how that widget will look. Setting any of the attributes on that styles object will change how Textual renders the widget.

Here's how you might change the widget to use white text on a blue background:

```python
self.styles.background = "blue"
self.styles.color = "white"
```

While its possible to set all styles for an app this way, Textual prefers to use CSS.

CSS files are data files loaded by your app which contain information about what styles to apply to your widgets. 

!!! note

    Don't worry if you have never worked with CSS before. The dialect of CSS we use is greatly simplified over web based CSS and easy to learn!

To load a CSS file you can set the `css_path` attribute of your app.

```python title="stopwatch03.py" hl_lines="31"
--8<-- "docs/examples/introduction/stopwatch03.py"
```

This will tell Textual to load the following file when it starts the app:

```css title="stopwatch03.css" 
--8<-- "docs/examples/introduction/stopwatch03.css"
```

The only change was setting the css path. Our app will now look very different:

```{.textual path="docs/examples/introduction/stopwatch03.py" title="stopwatch03.py"}
```

This app looks much more like our sketch. Textual has read style information from `stopwatch03.css` and applied it to the widgets. In effect setting attributes on `widget.styles`.

CSS files contain a number of _declaration blocks_. Here's the first such block from `stopwatch03.css` again:

```css 
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

- `layout: horizontal` aligns child widgets from left to right rather than top to bottom.
- `background: $panel-darken-1` sets the background color to `$panel-darken-1`. The `$` prefix picks a pre-defined color from the builtin theme. There are other ways to specify colors such as `"blue"` or `rgb(20,46,210)`.
- `height: 5` sets the height of our widget to 5 lines of text.
- `padding: 1` sets a padding of 1 cell around the child widgets.
- `margin: 1` sets a margin of 1 cell around the Stopwatch widget to create a little space between widgets in the list.


Here's the rest of `stopwatch03.css` which contains further declaration blocks:

```css
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

The last 3 blocks have a slightly different format. When the declaration begins with a `#` then the styles will be applied to any widget with a matching "id" attribute. We've set an id attribute on the Button widgets we yielded in compose. For instance the first button has `id="start"` which matches `#start` in the CSS.

The buttons have a `dock` style which aligns the widget to a given edge. The start and stop buttons are docked to the left edge, while the reset button is docked to the right edge.

You may have noticed that the stop button (`#stop` in the CSS) has `display: none;`. This tells Textual to not show the button. We do this because there is no point in displaying the stop button when the timer is *not* running. Similarly we don't want to show the start button when the timer is running. We will cover how to manage such dynamic user interfaces in the next section.
