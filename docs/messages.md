# Messages & Events

Each component of a Textual application has it its heart a queue of messages and a task which monitors this queue and calls Python code in response. The queue and task are collectively known as a _message pump_.

You will most often deal with _events_ which are a particular type of message that are created in response to user actions, such as key presses and mouse clicks, but also internal events such as timers. These events typically originate from a Driver class which sends them to an App class which is where you write code to respond to those events.

Lets write an _app_ which responds to a key event. This is probably the simplest Textual application that I can conceive of:

```python
from textual.app import App


class Beeper(App):
    async def on_key(self, event):
        self.console.bell()


Beeper.run()
```

If you run the above code, Textual will switch the terminal in to _application mode_. The terminal will go blank and the app will start processing events. If you hit any key you should hear a beep. Hit ctrl+C (control key and C key at the same time) to exit application mode and return to the terminal.

Although simple, this app follows the same pattern as more sophisticated applications. It starts by deriving a class from `App`; in this case `Beeper`. Calling the classmethod `run()` starts the application.

In our Beeper class there is a single event handler `on_key` which is called in response to a `Key` event. The method name is assumed by concatenating `on_` with the event name, hence `on_key` for a Key event, `on_timer` for a Timer event, etc. In Beeper, the on_key event calls `self.console.bell()` which is what plays the beep noise (if supported by your terminal).

The `on_key` method is preceded by the keyword `async` making it an asynchronous method. Textual is an asynchronous framework so event handlers and most methods are async.

Out Beeper app is missing typing information. Although completely optional, I recommend adding typing information which will help catch bugs (using tools such as [Mypy](https://mypy.readthedocs.io/en/stable/)). Here is the Beeper class with added typing:

```python
from textual.app import App
from textual import events


class Beeper(App):
    async def on_key(self, event: events.Key) -> None:
        self.console.bell()


Beeper.run()
```
