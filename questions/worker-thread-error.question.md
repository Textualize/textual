---
title: "How do I fix WorkerDeclarationError?"
alt_titles:
  - "Thread=True on Worker"
  - "Problem with threaded workers"
---

Textual version 0.31.0 requires that you set `thread=True` on the `@work` decorator if you want to run a threaded worker.

If you want a threaded worker, you would declare it in the following way:

```python
@work(thread=True)
def run_in_background():
    ...
```

If you *don't* want a threaded worker, you should make your work function `async`:

```python
@work()
async def run_in_background():
    ...
```

This change was made because it was too easy to accidentally create a threaded worker, which may produce unexpected results.
