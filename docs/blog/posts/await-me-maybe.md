---
draft: false
date: 2023-03-15
categories:
  - DevLog
authors:
  - willmcgugan
---

# No-async async with Python

A (reasonable) criticism of async is that it tends to proliferate in your code. In order to `await` something, your functions must be `async` all the way up the call-stack. This tends to result in you making things `async` just to support that one call that needs it or, worse, adding `async` just-in-case. Given that going from `def` to `async def` is a breaking change there is a strong incentive to go straight there.

Before you know it, you have adopted a policy of "async all the things".

<!-- more -->

Textual is an async framework, but doesn't *require* the app developer to use the `async` and `await` keywords (but you can if you need to). This post is about how Textual accomplishes this async-agnosticism.

!!! info

    See this [example](https://textual.textualize.io/guide/widgets/#attributes-down) from the docs for an async-less Textual app.


## An apology

But first, an apology! In a previous post I said Textual "doesn't do any IO of its own". This is not accurate. Textual responds to keys and mouse events (**I**nput) and writes content to the terminal (**O**utput).

Although Textual clearly does do IO, it uses `asyncio` mainly for *concurrency*. It allows each widget to update its part of the screen independently from the rest of the app.

## Await me (maybe)

The first no-async async technique is the "Await me maybe" pattern, a term first coined by [Simon Willison](https://simonwillison.net/2020/Sep/2/await-me-maybe/). This is particularly applicable to callbacks (or in Textual terms, message handlers).

The `await_me_maybe` function below can run a callback that is either a plain old function *or* a coroutine (`async def`). It does this by awaiting the result of the callback if it is awaitable, or simply returning the result if it is not.


```python
import asyncio
import inspect


def plain_old_function():
    return "Plain old function"

async def async_function():
    return "Async function"


async def await_me_maybe(callback):
    result = callback()
    if inspect.isawaitable(result):
        return await result
    return result


async def run_framework():
    print(
        await await_me_maybe(plain_old_function)
    )
    print(
        await await_me_maybe(async_function)
    )


if __name__ == "__main__":
    asyncio.run(run_framework())
```

## Optionally awaitable

The "await me maybe" pattern is great when an async framework calls the app's code. The app developer can choose to write async code or not. Things get a little more complicated when the app wants to call the framework's API. If the API has *asynced all the things*, then it would force the app to do the same.

Textual's API consists of regular methods for the most part, but there are a few methods which are optionally awaitable. These are *not* coroutines (which must be awaited to do anything).

In practice, this means that those API calls initiate something which will complete a short time later. If you discard the return value then it won't prevent it from working. You only need to `await` if you want to know when it has finished.

The `mount` method is one such method. Calling it will add a widget to the screen:

```python
def on_key(self):
    # Add MyWidget to the screen
    self.mount(MyWidget("Hello, World!"))
```

In this example we don't care that the widget hasn't been mounted immediately, only that it will be soon.

!!! note

    Textual awaits the result of mount after the message handler, so even if you don't *explicitly* await it, it will have been completed by the time the next message handler runs.

We might care if we want to mount a widget then make some changes to it. By making the handler `async` and awaiting the result of mount, we can be sure that the widget has been initialized before we update it:

```python
async def on_key(self):
    # Add MyWidget to the screen
    await self.mount(MyWidget("Hello, World!"))
    # add a border
    self.query_one(MyWidget).styles.border = ("heavy", "red")
```

Incidentally, I found there were very few examples of writing awaitable objects in Python. So here is the code for `AwaitMount` which is returned by the `mount` method:

```python
class AwaitMount:
    """An awaitable returned by mount() and mount_all()."""

    def __init__(self, parent: Widget, widgets: Sequence[Widget]) -> None:
        self._parent = parent
        self._widgets = widgets

    async def __call__(self) -> None:
        """Allows awaiting via a call operation."""
        await self

    def __await__(self) -> Generator[None, None, None]:
        async def await_mount() -> None:
            if self._widgets:
                aws = [
                    create_task(widget._mounted_event.wait(), name="await mount")
                    for widget in self._widgets
                ]
                if aws:
                    await wait(aws)
                    self._parent.refresh(layout=True)

        return await_mount().__await__()
```

## Summing up

Textual did initially "async all the things", which you might see if you find some old Textual code. Now async is optional.

This is not because I dislike async. I'm a fan! But it does place a small burden on the developer (more to type and think about). With the current API you generally don't need to write coroutines, or remember to await things. But async is there if you need it.

We're finding that Textual is increasingly becoming a UI to things which are naturally concurrent, so async was a good move. Concurrency can be a tricky subject, so we're planning some API magic to take the pain out of running tasks, threads, and processes. Stay tuned!

Join us on our [Discord server](https://discord.gg/Enf6Z3qhVr) if you want to talk about these things with the Textualize developers.
