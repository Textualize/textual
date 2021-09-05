# Refresh system

This note describes how Textual updates widgets on-screen.

if widget has made some changes and wishes to update visuals it can call Widget.refresh. There are two flags on this method; `repaint` which will repaint just the widget, and `layout` which will re-layout the screen. A layout must be done if the widget has changed size / position / visibility. Otherwise repaint will refresh just the widget area.

A refresh won't happen immediately when `refresh()` is called, rather it sets internal flags. The `on_idle` method of Widget checks these flags. This is so that multiple changes made to the UI while processing events don't cause excessive repainting of the screen (which makes the UI slow and jumpy).

In the case of a repaint. The Widget.on_idle handler will emit (send to the parent) an UpdateMessage. This message will be handled by the parent view, which will update the widget (a particular part of the screen).

In the case of a layout. The Widget.on_idle handler will emit a LayoutMessage. This message will be handled by the parent view, which calls refresh_layout on the root view, which will layout and repaint the entire screen.
