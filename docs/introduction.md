# Introduction

Welcome to the Textual Introduction!

This is a very gentle introduction to creating Textual applications.

## Pre-requisites

- Python 3.7 or later. If you have a choice, pick the most recent version.
- Installed `textual` from Pypi.
- Basic Python skills.

## A Simple App

Lets looks at the simplest possible Textual app. It doesn't do much, but will demonstrate the basic steps you will need to create any application.

If you would like to follow along and run the examples, navigate to the `docs/examples/introduction` directory from the command prompt. We will be looking at `intro01.py`, which you can see here:

=== "intro01.py"

    ```python
    --8<-- "docs/examples/introduction/intro01.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/introduction/intro01.py"}
    ```

Enter the following command to run the application:

```shell
python intro01.py
```

The command prompt should disappear and you will see a blank screen. Hit ++ctrl+c++ to exit and return to the command prompt.

Let's analyze this simple app.

The first step in all Textual applications is to import the `App` class from `textual.app` and extend it:

```python
from textual.app import App

class ExampleApp(App):
    pass
```

There will be a single App object in any Textual application. The App class is responsible for loading data, setting up the screen, managing events etc.

The following two lines create an instance of the application and calls `run()`:

```python
app = ExampleApp()
app.run()
```

The `run` method will put your terminal in to "application mode" which disables the prompt and allows Textual to take over input and output. The `run()` method will return when the application exits.

## Handling Events

In the previously example our app did next to nothing. Most applications will contain event handler methods, which are called in response to user actions (such as key presses, mouse action) and other changes your app needs to know about such as terminal resize, scrolling, timers, etc.

!!! note

    Although `intro01.py` did not explicitly define any event handlers, Textual still had to respond to the Key event to catch ++ctrl+c++, otherwise you wouldn't be able to exit the app.

In our next example, we are going to handle two such events; `Mount` and `Key`. The `Mount` event is sent when the app is first run, and a `Key` event is sent when the user presses a key on the keyboard. Try running `intro02.py` in the `docs/examples/introduction`:

=== "intro02.py"

    ```python
    --8<-- "docs/examples/introduction/intro02.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/introduction/intro02.py"}
    ```

When you run this app you should see a blue screen. If you hit any of the number keys ++0++-++9++, the background will change to another color. You may also hear a beep or some other noise when a key is pressed, depending on how your terminal is configured. As before, pressing ++ctrl+c++ will exit the app and return you to your prompt.

There are two event handlers in this app class. Event handlers start with the text `on_` followed by the name of the event in lower case. Hence `on_mount` is called for the `Mount` event, and `on_key` is called for the `Key` event.

Here's the `on_mount` method again:

```python
def on_mount(self):
    self.styles.background = "darkblue"
```

This method sets the `background` attribute on `self.styles` to `"darkblue"` which makes the application background blue when the app loads. The `styles` object contains a variety of properties which define how your app looks. We will explore what you can do with this object later.

The second event handler will receive `Key` events whenever you press a key on the keyboard:

```python
def on_key(self, event):
    if event.key.isdigit():
        self.styles.background = self.COLORS[int(event.key)]
    self.bell()
```

This method has an `event` positional argument which contains information regarding the key that was pressed. The body of the method sets the background to a corresponding color when you press one of the digit keys. It also calls `bell()` which is a method on App that plays your terminal's bell.

!!! note

    Every event has a corresponding `Event` object, but Textual knows to only call the event handler with the event object if you have it in the argument list. It does this by inspecting the handler method prior to calling it.

## Widgets

Most Textual applications will also make use of one or more `Widget` classes. A Widget is a self contained component which is responsible for defining how a given part of the screen should look. Widgets respond to events in much the same way as the App does. More sophisticated user interfaces can be built by combining various widgets.

Let's look at an app which defines a very simple Widget to show the current time and date. Here is the code for `"clock01.py"` which is n the same directory as the previous examples:

=== "clock01.py"

    ```python
    --8<-- "docs/examples/introduction/clock01.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/introduction/clock01.py"}
    ```

This script imports App as before, but also the `Widget` class from `textual.widget`, which is the base class for all Widgets. The `Clock` widget extends `Widget` and adds an `on_mount` handler which is called when the widget is first added to the application.

Lets have a look at the Clock's Mount event handler:

```python
    def on_mount(self):
        self.styles.content_align = ("center", "middle")
        self.set_interval(1, self.refresh)
```

The first line in that method sets the `content_align` attribute on the styles object, which defines how text is positioned within the Widget. We're setting it to a tuple of `("center", "middle")` which tells Textual to horizontally center the text, and place it in the middle vertically. If you resize the terminal you should notice that the text is automatically centered.

The second line calls `self.set_interval` to request that Textual calls `self.refresh` to update the screen once a second. When the screen is refreshed, Textual will call the widget's `render()` method, which we can see here:

```python
    def render(self):
        return datetime.now().strftime("%c")
```

This method uses the datetime module to format the current date and time. It returns a string, but can also return a _Rich renderable_. Don't worry if you aren't familiar with [Rich](https://github.com/Textualize/rich), we will cover that later.
