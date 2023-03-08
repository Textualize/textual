---
draft: false
date: 2023-03-08
categories:
  - DevLog
authors:
  - willmcgugan
---

# Overhead of Python Asyncio tasks

Every widget in Textual, be it a button, tree view, or a text input, runs an [asyncio](https://docs.python.org/3/library/asyncio.html) task. There is even a task for [scrollbar corners](https://github.com/Textualize/textual/blob/e95a65fa56e5b19715180f9e17c7f6747ba15ec5/src/textual/scrollbar.py#L365) (the little space formed when horizontal and vertical scrollbars meet).

<!-- more -->

!!! info

    It may be IO that gives AsyncIO its name, but Textual doesn't do any IO of its own. Those tasks are used to power *message queues*, so that widgets (UI components) can do whatever they do at their own pace.

Its fair to say that Textual apps launch a lot of tasks. Which is why when I was trying to optimize startup (for apps with 1000s of widgets) I suspected it was task related.

I needed to know how much of an overhead it was to launch tasks. Tasks are lighter weight than threads, but how much lighter? The only way to know for certain was to profile.

The following code launches a load of *do nothing* tasks, then waits for them to shut down. This would give me an idea of how performant `create_task` is, and also a *baseline* for optimizations. I would know the absolute limit of any optimizations I make.

```python
from asyncio import create_task, wait, run
from time import process_time as time


async def time_tasks(count=100) -> float:
    """Time creating and destroying tasks."""

    async def nop_task() -> None:
        """Do nothing task."""
        pass

    start = time()
    tasks = [create_task(nop_task()) for _ in range(count)]
    await wait(tasks)
    elapsed = time() - start
    return elapsed


for count in range(100_000, 1000_000 + 1, 100_000):
    create_time = run(time_tasks(count))
    create_per_second = 1 / (create_time / count)
    print(f"{count:,} tasks \t {create_per_second:0,.0f} tasks per/s")
```

And here is the output:

```
100,000 tasks    280,003 tasks per/s
200,000 tasks    255,275 tasks per/s
300,000 tasks    248,713 tasks per/s
400,000 tasks    248,383 tasks per/s
500,000 tasks    241,624 tasks per/s
600,000 tasks    260,660 tasks per/s
700,000 tasks    244,510 tasks per/s
800,000 tasks    247,455 tasks per/s
900,000 tasks    242,744 tasks per/s
1,000,000 tasks          259,715 tasks per/s
```

!!! info

    Running on an M1 MacBook Pro.

This tells me I can create, run, and shutdown 260K tasks per second.

That's fast.

Clearly `create_task` is as close as you get to free in the Python world, and I would need to look elsewhere for optimizations. Turns out Textual spends far more time processing CSS rules than creating tasks (obvious in retrospect). I've noticed some big wins there, so the next version of Textual will be faster to start apps with a metric tonne of widgets.

But I still need to know what to do with those scrollbar corners. A task for two characters. I don't even...
