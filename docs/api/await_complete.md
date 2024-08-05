---
title: "textual.await_complete"
---

This module contains the `AwaitComplete` class.
An `AwaitComplete` object is returned by methods that do work in the *background*.
You can await this object if you need to know when that work has completed.
Or you can ignore it, and Textual will automatically await the work before handling the next message.

!!! note

    You are unlikely to need to explicitly create these objects yourself.


::: textual.await_complete
