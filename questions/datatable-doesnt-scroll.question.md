---
title: "Why doesn't the `DataTable` scroll programmatically?"
alt_titles:
  - "Scroll bindings from `DataTable` not working."
  - "Datatable cursor goes off screen and doesn't scroll."
---

If scrolling in your `DataTable` is _apparently_ broken, it may be because your `DataTable` is using the default value of `height: auto`.
This means that the table will be sized to fit its rows without scrolling, which may cause the *container* (typically the screen) to scroll.
If you would like the table itself to scroll, set the height to something other than `auto`, like `100%`.

!!! note

    As of Textual v0.31.0 the `max-height` of a `DataTable` is set to `100%`, this will mean that the above is no longer the default experience.
