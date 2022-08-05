# Introduction

Welcome to the Textual Introduction!

This is a very gentle introduction to creating Textual applications. By the end of this document you should have an understanding of the basic concepts involved in using the Textual framework.

## Pre-requisites

- Python 3.7 or later. If you have a choice, pick the most recent version.
- Installed `textual` from Pypi.
- Basic Python skills.

## A Simple App

Let's looks at the simplest possible Textual app. It doesn't do much, but will demonstrate the basic steps you will need to create any application.

If you would like to follow along and run the examples, navigate to the `docs/examples/introduction` directory from the command prompt. We will be looking at `intro01.py`, which you can see here:

```python title="intro01.py"
--8<-- "docs/examples/introduction/intro01.py"
```

Enter the following command to run the application:

```bash
python intro01.py
```

The command prompt should disappear and you will see a blank screen. It will look something like the following:

```{.textual path="docs/examples/introduction/intro01.py"}

```

Hit ++ctrl+c++ to exit and return to the command prompt.

### The code

The first step in all Textual applications is to import the `App` class from `textual.app` and extend it:

```python hl_lines="1 2 3 4 5" title="intro01.py"
--8<-- "docs/examples/introduction/intro01.py"
```

This App class is responsible for loading data, setting up the screen, managing events etc. In a real app most of the core logic of your application will be contained within methods on this class.

The last two lines create an instance of the application and calls the `run()` method:

```python hl_lines="8 9" title="intro01.py"
--8<-- "docs/examples/introduction/intro01.py"
```

The `run` method will put your terminal in to "application mode" which disables the prompt and allows Textual to take over input and output. When you press ++ctrl+c++ the application will exit application mode and re-enable the command prompt.

## Handling Events

Most real-world applications will want to interact with the user in some way. To do this we can make use of _event handler_ methods, which are called in response to things the user does such as pressing a key(s), moving the mouse, resizing the terminal, etc.

Each event type is represented by an event object, which is an instance of a class containing information you may need to respond the the event. For instance the `Key` event contains the key the user pressed and a `Mouse` event will contain the coordinates of the mouse cursor.

!!! note

    Although `intro01.py` did not explicitly define any event handlers, Textual still had to respond to events to catch ++ctrl+c++, otherwise you wouldn't be able to exit the app.

The next example demonstrates handling events. Try running `intro02.py` in the `docs/examples/introduction`:

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

The first event handler to run is `on_mount`. The `Mount` is sent to your application immediately after entering application mode.

```python hl_lines="19 20" title="intro02.py"
--8<-- "docs/examples/introduction/intro02.py"
```

This `on_mount` method sets the `background` attribute of `self.styles` to `"darkblue"` which makes the background blue when the application starts. There are a lot of other properties on the Styles object, which define how your app looks. We will explore what you can do with this object later.

!!! note

    You may have noticed there is no function call to repaint the screen in this example. Textual is generally quite smart in detecting when a refresh is required, and updating the screen automatically.

The second event handler will receive `Key` events whenever you press a key on the keyboard:

```python hl_lines="22 23 24 25" title="intro02.py"
--8<-- "docs/examples/introduction/intro02.py"
```

This method has an `event` positional argument which will receive the event object; in this case the `Key` event. The body of the method sets the background to a corresponding color in the `COLORS` list when you press one of the digit keys. It also calls `bell()` which is a method on App that plays your terminal's bell.

!!! note

    Every event has a corresponding `Event` object, but Textual knows to only call the event handler with the event object if you have it in the argument list. It does this by inspecting the handler method prior to calling it. So if you don't need the event object, you may leave it out.

## Widgets

Most Textual applications will make use of one or more `Widget` classes. A Widget is a self contained component responsible for defining how a given part of the screen should look. Widgets respond to events in much the same way as the App does.

Let's look at an app with a simple Widget to show the current time and date. Here is the code for `"clock01.py"` which is in the same directory as the previous examples:

```python title="clock01.py"
--8<-- "docs/examples/introduction/clock01.py"
```

Here's what you will see if you run this code:

```{.textual path="docs/examples/introduction/clock01.py"}

```

This script imports App as before, but also the `Widget` class from `textual.widget`, which is the base class for all Widgets. To create a Clock widget we extend from the Widget base class:

```python title="clock01.py" hl_lines="7 8 9 10 11 12 13"
--8<-- "docs/examples/introduction/clock01.py"
```

Widgets support many of the same events as the Application itself, and can be thought of as mini-applications in their own right. The Clock widget responds to a Mount event which is the first event received when a widget is _mounted_ (added to the App). The code in `Clock.on_mount` sets `styles.content_align` to tuple of `("center", "middle")` which tells Textual to display the Widget's content aligned to the horizontal center, and in the middle vertically. If you resize the terminal, you should find the time remains in the center.

The second line in `on_mount` calls `self.set_interval` which tells Textual to invoke the `self.refresh` method once per second.

When Textual refreshes a widget it calls it's `render` method:

```python title="clock01.py" hl_lines="12 13"
--8<-- "docs/examples/introduction/clock01.py"
```

The Clocks `render` method uses the datetime module to format the current date and time. It returns a string, but can also return a _Rich renderable_. Don't worry if you aren't familiar with [Rich](https://github.com/Textualize/rich), we will cover that later.

Before a Widget can be displayed, it must first be mounted on the app. This is typically done within the applications Mount handler, so that an application's widgets are added when the application first starts:

```python title="clock01.py" hl_lines="17 18"
--8<-- "docs/examples/introduction/clock01.py"
```

In the case of the clock application, we call `mount` with an instance of the `Clock` widget.

That's all there is to this Clock example. It will display the current time until you hit ++ctrl+c++
