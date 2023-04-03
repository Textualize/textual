# Workers

In this chapter we will explore the topic of *concurrency* and how to use Textual's Worker API to make it easier.

!!! tip "The worker API was added in version 0.18.0"

## Concurrency

There are many interesting uses for Textual which required reading data from an internet service.
When an app requests data from the network it is important that it doesn't prevent the user interface from updating.
In other words, the requests should be concurrent (happen at the same time) with the UI updates.

Managing this concurrency is a tricky topic, in any language or framework.
Even for experienced developers, there are many gotchas which could make your app lock up or behave oddly.
Textual's Worker API makes concurrency less error prone and easier to reason about.

## Workers

Before we go in to detail, lets see an example that demonstrates a common pitfall for apps that make network requests.

The following app uses [httpx](https://www.python-httpx.org/) query the weather with [wttr.in](https://wttr.in/) for any city name you enter in to an input:

=== "weather01.py"

    ```python title="weather01.py"
    --8<-- "docs/examples/guide/workers/weather01.py"
    ```

=== "weather.css"

    ```sass title="weather.css"
    --8<-- "docs/examples/guide/workers/weather.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/workers/weather01.py"}
    ```

If you were to run this app, you should see weather information update as you type.
But you may find that the input is not as responsive as usual, with a noticeable delay between pressing a key and seeing it echoed in screen.
This is because we are making a request to the weather API within a message handler, and the input will not be able to process the next key until the request has completed (which may be anything from a few hundred milliseconds to several seconds later).

To resolve this we can use the [run_worker][textual.dom.DOMNode.run_worker] function which runs the `update_weather` coroutine (async function) in the background. Here's the code:

```python title="weather02.py" hl_lines="22"
--8<-- "docs/examples/guide/workers/weather02.py"
```

This one line change will make typing as responsive as you would expect from any app.

The `run_worker` method schedules a new *worker* to run `update_weather`, and returns a [Worker](textual.worker.Worker) object.
This Worker object has a few useful methods on it, but you can often ignore it as we did in `weather02.py`.

The call to `run_worker` also sets `exclusive=True` which solves an additional problem with concurrent network requests: when pulling data from the network there is no guarantee that you will receive the responses in the same order as the requests.
For example if you start typing `Paris`, you may get the response for `Pari` *after* the response for `Paris`, which could show the wrong weather information.
The `exclusive` flag tells textual to cancel all previous workers before starting the new one.

### Work decorator

An alternative to calling `run_worker` manually is the [work][textual.work] decorator, which automatically generates a worker from the decorator method.

Let's use this decorator in our weather app:

```python title="weather03.py" hl_lines="3 23 25"
--8<-- "docs/examples/guide/workers/weather03.py"
```

The addition of `@work(exclusive=True)` converts the `update_weather` coroutine in to a regular function which creates and starts a worker.
Note that even though `update_weather` is an `async def` function, the decorator means that we don't need to use the `await` keyword when calling it.

!!! tip

    The decorator takes the same arguments as `run_worker`.

### Worker return values

When you run a worker, the return value of the function won't be available until the work has completed.
You can check the return value of a worker with the `worker.result` attribute which will initially be `None`, but will be replaced with the return value of the function when it completes.

If you need the return value you can call [worker.wait][textual.worker.Worker.wait] which is a coroutine that will wait for the work to complete.
But note that if you do this in a message handler it will also prevent the widget from updating until the worker returns.
Often a better approach is to handle [worker events](#worker-events).

### Cancelling workers

You can cancel a worker at any time before it is finished by calling [Worker.cancel][textual.worker.Worker.cancel].
This will raise an [asyncio.CancelledError] within the coroutine, and should cause it to exit prematurely.

### Worker lifetime

Workers are managed by a single [WorkerManager][textual._worker_manager.WorkerManager] instance, which you can access via `app.workers`.
This is a container like object which you can iterator over to sett all your currently active tasks.

Workers are tied to the DOM node (widget, screen, or app) where they are created.
This means that if you remove the widget or pop the screen when they are created, then the tasks will be cleaned up automatically.
Similarly if you exit the app, any running tasks will be cancelled.

Worker objects have a `state` attribute which will contain a [WorkerState][textual.worker.WorkerState] enumeration, which indicates what the worker is doing at any given time.
The `state` attribute will contain one of the following values:


| Value     | Description                                                                         |
| --------- | ----------------------------------------------------------------------------------- |
| PENDING   | The worker was created, but not yet started.                                        |
| RUNNING   | The worker is currently running.                                                    |
| CANCELLED | The worker was cancelled and is not longer running.                                 |
| ERROR     | The worker raised an exception, and `worker.error` will contain the exception.      |
| SUCCESS   | The worker completed successful, and `worker.result` will contain the return value. |

<div class="excalidraw">
--8<-- "docs/images/workers/lifetime.excalidraw.svg"
</div>

### Worker events

When a worker changes state, it sends a [Worker.StateChanged][textual.worker.Worker.StateChanged] event to the widget where the worker was created.
You can handle this message by defining a `on_worker_state_changed` event handler.
For instance, here is how we might log the state of the worker that updates the weather:

```python title="weather04.py" hl_lines="4 41 43"
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

You can create threads by applying `run_worker` or the `work` decorator to a plain (non async) method or function.
The API for thread workers is identical to async workers, but there are a few differences you need to be aware of when writing threaded code.

The first difference is that you should avoid calling methods on your UI directly, or setting reactive variables.
You can work around this with the [App.call_from_thread][textual.app.call_from_thread] method which schedules a call in the main thread.

The second difference is that you can't cancel threads in the same way as coroutines, but you *can* manually check if the worker was cancelled.

Let's demonstrate thread workers by replacing `httpx` with `urllib.request` (in the standard library). The `urllib` module is not async aware, so we will need to use threads:

```python title="weather05.py" hl_lines="1 4 27 30 34-39 42-43"
--8<-- "docs/examples/guide/workers/weather05.py"
```

The `update_weather` function doesn't have the `async` keyword, so the `@work` decorator will create a thread worker.
Note the user of [get_current_worker][textual.worker.get_current_worker] which the function uses to check if it has been cancelled or not.
