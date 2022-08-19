# Introduction

Welcome to the Textual Introduction!

By the end of this page you should have a good idea of the steps involved in creating an application with Textual.


## Stopwatch Application

We're going to build a stopwatch app. This app will display the elapsed time since the user hit a "Start" button. The user will be able to stop / resume / reset each stopwatch in addition to adding or removing them.

This is a simple yet **fully featured** app &mdash; you could distribute this app if you wanted to!

Here's what the finished app will look like:


```{.textual path="docs/examples/introduction/timers.py"}
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

The last lines in "stopwatch01.py" may be familiar to you. We create an instance of our app class, and run it within a `__name__ == "__main__"` conditional block. This is so that we could import `app` if we want to. Or we could run it with `python stopwatch01.py`. 

## Timers

=== "Timers Python"

    ```python title="timers.py"
    --8<-- "docs/examples/introduction/timers.py"
    ```

=== "Timers CSS"

    ```python title="timers.css"
    --8<-- "docs/examples/introduction/timers.css"
    ```


## Pre-requisites

- Python 3.7 or later. If you have a choice, pick the most recent version.
- Installed `textual` from Pypi.
- Basic Python skills.


```{.textual path="docs/examples/introduction/timers.py"}

``` 

## A Simple App

Let's looks at the simplest possible Textual app.

If you would like to follow along and run the examples, navigate to the `docs/examples/introduction` directory from the command prompt. We will be looking at `intro01.py`, which you can see here:

```python title="intro01.py"
--8<-- "docs/examples/introduction/intro01.py"
```

Enter the following command to run the application:

```bash
python intro01.py
```

The command prompt should disappear and you will see a blank screen:

```{.textual path="docs/examples/introduction/intro01.py"}

```

Hit ++Ctrl+c++ to exit and return to the command prompt.

### Application mode

The first step in all Textual applications is to import the `App` class from `textual.app` and extend it:

```python hl_lines="1 2 3 4 5" title="intro01.py"
--8<-- "docs/examples/introduction/intro01.py"
```

This App class is responsible for loading data, setting up the screen, managing events etc. In a real app most of the core logic of your application will be contained within methods on this class.

The last two lines create an instance of the application and call the `run()` method:

```python hl_lines="8 9" title="intro01.py"
--8<-- "docs/examples/introduction/intro01.py"
```

The `run` method will put your terminal in to "application mode" which disables the prompt and allows Textual to take over input and output. When you press ++ctrl+c++ the application will exit application mode and re-enable the command prompt.

## Handling Events

Most real-world applications will need to interact with the user in some way. To do this we can make use of _event handler_ methods, which are called in response to things the user does such as pressing keys, moving the mouse, resizing the terminal, etc.

Each event type is represented by an instance of one of a number of Event objects. These event objects may contain additional information regarding the event. For instance, the `Key` event contains the key the user pressed and a `Mouse` event will contain the coordinates of the mouse cursor.

!!! note

    Although `intro01.py` did not explicitly define any event handlers, Textual still had to respond to events to catch ++ctrl+c++, otherwise you wouldn't be able to exit the app.

The next example demonstrates handling events. Try running `intro02.py` in the `docs/examples/introduction` directory:

```python title="intro02.py"
--8<-- "docs/examples/introduction/intro02.py"
```

When you run this app you should see a blue screen in your terminal, like the following:

```{.textual path="docs/examples/introduction/intro02.py"}

```

If you hit any of the number keys ++0++-++9++, the background will change color and you should hear a beep. As before, pressing ++ctrl+c++ will exit the app and return you to your prompt.

!!! note

    The "beep" is your terminal's *bell*. Some terminals may be configured to play different noises or a visual indication of a bell rather than a noise.

There are two event handlers in this app. Event handlers start with the text `on_` followed by the name of the event in lower case. Hence `on_mount` is called for the `Mount` event, and `on_key` is called for the `Key` event.

!!! note

    Event class names are transformed to _camel case_ when used in event handlers. So the `MouseMove` event will be handled by a method called `on_mouse_move`.

The first event handler to run is `on_mount`. The `Mount` event is sent to your application immediately after entering application mode.

```python hl_lines="19 20" title="intro02.py"
--8<-- "docs/examples/introduction/intro02.py"
```

The above `on_mount` method sets the `background` attribute of `self.styles` to `"darkblue"` which makes the background blue when the application starts. There are a lot of other style properties which define how your app looks. We will explore those later.

!!! note

    You may have noticed there is no function call to repaint the screen in this example. Textual is smart enough to know when the screen needs to be updated, and will do it automatically.

The second event handler will receive `Key` events whenever you press a key on the keyboard:

```python hl_lines="22 23 24 25" title="intro02.py"
--8<-- "docs/examples/introduction/intro02.py"
```

This method has an `event` positional argument which will receive the event object; in this case the `Key` event. The body of the method sets the background to a corresponding color in the `COLORS` list when you press one of the digit keys. It also calls `bell()` to plays your terminal's bell sound.

!!! note

    Every event has a corresponding `Event` object. Textual will call your event handler with an event object only if you have it in the argument list. It does this by inspecting the handler method prior to calling it. So if you don't need the event object, you may leave it out.

## Widgets

Most Textual applications will make use of one or more `Widget` classes. A Widget is a self contained component responsible for defining how a given part of the screen should look. Widgets respond to events in much the same way as the App does.

Let's look at an app with a simple Widget to show the current time and date. Here is the code for `"clock01.py"` which is in the same directory as the previous examples:

```python title="clock01.py"
--8<-- "docs/examples/introduction/clock01.py"
```

Here's what you will see if you run this code:

```{.textual path="docs/examples/introduction/clock01.py"}

```

This script imports `App` as before and also the `Widget` class from `textual.widget`. To create a Clock widget we extend from the Widget base class.

```python title="clock01.py" hl_lines="7 8 9 10 11 12 13"
--8<-- "docs/examples/introduction/clock01.py"
```

Widgets support many of the same events as the Application itself, and can be thought of as mini-applications in their own right. The Clock widget responds to a Mount event which is the first event received when a widget is _mounted_ (added to the App). The mount handler (`Clock.on_mount`) sets `styles.content_align` to `("center", "middle")` which tells Textual to center align its contents horizontally and vertically. If you size the terminal you should see that the text remains centered.

The second line in `on_mount` calls `self.set_interval` which tells Textual to invoke the `self.refresh` method once per second, so our clock remains up-to-date.

When Textual refreshes a widget it calls it's `render` method:

```python title="clock01.py" hl_lines="12 13"
--8<-- "docs/examples/introduction/clock01.py"
```

The Clock's `render` method uses the datetime module to format the current date and time. It returns a string, but can also return a [Rich](https://github.com/Textualize/rich) _renderable_. Don't worry if you aren't familiar with Rich, we will cover that later.

Before a Widget can be displayed, it must first be mounted on the app. This is typically done within the application's Mount handler:

```python title="clock01.py" hl_lines="17 18"
--8<-- "docs/examples/introduction/clock01.py"
```

In the case of the clock application, we call `mount` with an instance of the `Clock` widget.

That's all there is to this Clock example. It will display the current time until you hit ++ctrl+c++

## Compose

Mounting "child" widgets from from an `on_mount` event is such a common pattern that Textual offers a convenience method to do that.

If you implement a `compose()` method on your App or Widget, Textual will invoke it to get your "sub-widgets". This method should return an _iterable_ such as a list, but you may find it easier to use the `yield` statement to turn it in to a Python generator:

```python title="clock02.py" hl_lines="17 18"
--8<-- "docs/examples/introduction/clock02.py"
```

Here's the clock example again using `compose()` rather than `on_mount`. Any Widgets yielded from this method will be mounted on to the App or Widget. In this case we mount our Clock widget as before.

More sophisticated apps will likely yield multiple widgets from `compose()`, and many widgets will also yield child widgets of their own.

## Next Steps

We've seen how Textual apps can respond to events, and how to mount widgets which are like mini-applications in their own right. These are key concepts in Textual which you can use to build more sophisticated apps.

The Guide covers this in much more detail and describes how arrange widgets on the screen and connect them with the core logic of your application.
