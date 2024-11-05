# Workers

In this chapter we will explore the topic of *concurrency* and how to use Textual's Worker API to make it easier.

!!! tip "The Worker API was added in version 0.18.0"

## Concurrency

There are many interesting uses for Textual which require reading data from an internet service.
When an app requests data from the network it is important that it doesn't prevent the user interface from updating.
In other words, the requests should be concurrent (happen at the same time) as the UI updates.

This is also true for anything that could take a significant time (more than a few milliseconds) to complete.
For instance, reading from a [subprocess](https://docs.python.org/3/library/asyncio-subprocess.html#asyncio-subprocess) or doing compute heavy work.

Managing this concurrency is a tricky topic, in any language or framework.
Even for experienced developers, there are gotchas which could make your app lock up or behave oddly.
Textual's Worker API makes concurrency far less error prone and easier to reason about.

## Workers

Before we go into detail, let's see an example that demonstrates a common pitfall for apps that make network requests.

The following app uses [httpx](https://www.python-httpx.org/) to get the current weather for any given city, by making a request to [wttr.in](https://wttr.in/).

=== "weather01.py"

    ```python title="weather01.py"
    --8<-- "docs/examples/guide/workers/weather01.py"
    ```

=== "weather.tcss"

    ```css title="weather.tcss"
    --8<-- "docs/examples/guide/workers/weather.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/workers/weather01.py"}
    ```

If you were to run this app, you should see weather information update as you type.
But you may find that the input is not as responsive as usual, with a noticeable delay between pressing a key and seeing it echoed in screen.
This is because we are making a request to the weather API within a message handler, and the app will not be able to process other messages until the request has completed (which may be anything from a few hundred milliseconds to several seconds later).

To resolve this we can use the [run_worker][textual.dom.DOMNode.run_worker] method which runs the `update_weather` coroutine (`async def` function) in the background. Here's the code:

```python title="weather02.py" hl_lines="21"
--8<-- "docs/examples/guide/workers/weather02.py"
```

This one line change will make typing as responsive as you would expect from any app.

The `run_worker` method schedules a new *worker* to run `update_weather`, and returns a [Worker][textual.worker.Worker] object. This happens almost immediately, so it won't prevent other messages from being processed. The `update_weather` function is now running concurrently, and will finish a second or two later.

!!! tip

    The [Worker][textual.worker.Worker] object has a few useful methods on it, but you can often ignore it as we did in `weather02.py`.

The call to `run_worker` also sets `exclusive=True` which solves an additional problem with concurrent network requests: when pulling data from the network, there is no guarantee that you will receive the responses in the same order as the requests.
For instance, if you start typing "Paris", you may get the response for "Pari" *after* the response for "Paris", which could show the wrong weather information.
The `exclusive` flag tells Textual to cancel all previous workers before starting the new one.

### Work decorator

An alternative to calling `run_worker` manually is the [work][textual.work] decorator, which automatically generates a worker from the decorated method.

Let's use this decorator in our weather app:

```python title="weather03.py" hl_lines="4 22 24"
--8<-- "docs/examples/guide/workers/weather03.py"
```

The addition of `@work(exclusive=True)` converts the `update_weather` coroutine into a regular function which when called will create and start a worker.
Note that even though `update_weather` is an `async def` function, the decorator means that we don't need to use the `await` keyword when calling it.

!!! tip

    The decorator takes the same arguments as `run_worker`.

### Worker return values

When you run a worker, the return value of the function won't be available until the work has completed.
You can check the return value of a worker with the `worker.result` attribute which will initially be `None`, but will be replaced with the return value of the function when it completes.

If you need the return value you can call [worker.wait][textual.worker.Worker.wait] which is a coroutine that will wait for the work to complete.
But note that if you do this in a message handler it will also prevent the widget from updating until the worker returns.
Often a better approach is to handle [worker events](#worker-events) which will notify your app when a worker completes, and the return value is available without waiting.

### Cancelling workers

You can cancel a worker at any time before it is finished by calling [Worker.cancel][textual.worker.Worker.cancel].
This will raise a [CancelledError][asyncio.CancelledError] within the coroutine, and should cause it to exit prematurely.

### Worker errors

The default behavior when a worker encounters an exception is to exit the app and display the traceback in the terminal.
You can also create workers which will *not* immediately exit on exception, by setting `exit_on_error=False` on the call to `run_worker` or the `@work` decorator.

### Worker lifetime

Workers are managed by a single [WorkerManager][textual.worker_manager.WorkerManager] instance, which you can access via `app.workers`.
This is a container-like object which you iterate over to see your active workers.

Workers are tied to the DOM node (widget, screen, or app) where they are created.
This means that if you remove the widget or pop the screen where they are created, then the tasks will be cleaned up automatically.
Similarly if you exit the app, any running tasks will be cancelled.

Worker objects have a `state` attribute which will contain a [WorkerState][textual.worker.WorkerState] enumeration that indicates what the worker is doing at any given time.
The `state` attribute will contain one of the following values:


| Value     | Description                                                                         |
| --------- | ----------------------------------------------------------------------------------- |
| PENDING   | The worker was created, but not yet started.                                        |
| RUNNING   | The worker is currently running.                                                    |
| CANCELLED | The worker was cancelled and is no longer running.                                  |
| ERROR     | The worker raised an exception, and `worker.error` will contain the exception.      |
| SUCCESS   | The worker completed successful, and `worker.result` will contain the return value. |

Workers start with a `PENDING` state, then go to `RUNNING`. From there, they will go to `CANCELLED`, `ERROR` or `SUCCESS`.

<div class="excalidraw">
--8<-- "docs/images/workers/lifetime.excalidraw.svg"
</div>

### Worker events

When a worker changes state, it sends a [Worker.StateChanged][textual.worker.Worker.StateChanged] event to the widget where the worker was created.
You can handle this message by defining an `on_worker_state_changed` event handler.
For instance, here is how we might log the state of the worker that updates the weather:

```python title="weather04.py" hl_lines="4 40-42"
--8<-- "docs/examples/guide/workers/weather04.py"
```

If you run the above code with `textual` you should see the worker lifetime events logged in the Textual [console](./devtools.md#console).

```
textual run weather04.py --dev
```

### Thread workers

In previous examples we used `run_worker` or the `work` decorator in conjunction with coroutines.
This works well if you are using an async API like `httpx`, but if your API doesn't support async you may need to use *threads*.

!!! info "What are threads?"

    Threads are a form of concurrency supplied by your Operating System. Threads allow your code to run more than a single function simultaneously.

You can create threads by setting `thread=True` on the `run_worker` method or the `work` decorator.
The API for thread workers is identical to async workers, but there are a few differences you need to be aware of when writing code for thread workers.

The first difference is that you should avoid calling methods on your UI directly, or setting reactive variables.
You can work around this with the [App.call_from_thread][textual.app.App.call_from_thread] method which schedules a call in the main thread.

The second difference is that you can't cancel threads in the same way as coroutines, but you *can* manually check if the worker was cancelled.

Let's demonstrate thread workers by replacing `httpx` with `urllib.request` (in the standard library).
The `urllib` module is not async aware, so we will need to use threads:

```python title="weather05.py" hl_lines="1-2 27-44"
--8<-- "docs/examples/guide/workers/weather05.py"
```

In this example, the `update_weather` is not asynchronous (i.e. a regular function).
The `@work` decorator has `thread=True` which makes it a thread worker.
Note the use of [get_current_worker][textual.worker.get_current_worker] which the function uses to check if it has been cancelled or not.

!!! important

    Textual will raise an exception if you add the `work` decorator to a regular function without `thread=True`.


#### Posting messages

Most Textual functions are not thread-safe which means you will need to use [call_from_thread][textual.app.App.call_from_thread] to run them from a thread worker.
An exception would be [post_message][textual.widget.Widget.post_message] which *is* thread-safe.
If your worker needs to make multiple updates to the UI, it is a good idea to send [custom messages](./events.md) and let the message handler update the state of the UI.
