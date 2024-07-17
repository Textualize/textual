---
title: "textual.await_complete"
---

This object is returned by methods that do work in the *background*.
You can await the return value if you need to know when that work has completed.
If you ignore it, Textual will wait for the work to be done before handling the next message.

!!! note

    You are unlikely to need to explicitly create these objects yourself.


::: textual.await_complete
