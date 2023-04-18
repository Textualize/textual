---
title: "How can I set a translucent app background?"
alt_titles:
  - "Transparent background not working"
  - "Translucent background not working"
  - "Can't see desktop underneath terminal"
---

Some terminal emulators have a translucent background feature which allows the desktop underneath to be partially visible.

This feature is unlikely to work with Textual, as the translucency effect requires the use of ANSI background colors, which Textual doesn't use.
Textual uses 16.7 million colors where available which enables consistent colors across all platforms and additional effects which aren't possible with ANSI colors.

For more information on ANSI colors in Textual, see [Why no Ansi Themes?](#why-doesnt-textual-support-ansi-themes).
