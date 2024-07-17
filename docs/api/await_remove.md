---
title: "textual.await_remove"
---


This object is returned by [`Widget.remove()`][textual.widget.Widget.remove], and other methods which remove widgets.
You can await the return value if you need to know exactly when the widgets have been removed.
If you ignore it, Textual will wait for the widgets to be removed before handling the next message.

!!! note

    You are unlikely to need to explicitly create these objects yourself.


::: textual.await_remove
