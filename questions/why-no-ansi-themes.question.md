---
title: "Why doesn't Textual support ANSI themes?"
alt_titles:
  - "Textual should use system terminal colors for cyan, etc"
  - "ANSI theme colors not working"
---

Textual will not generate escape sequences for the 16 themeable *ANSI* colors.

This is an intentional design decision we took for the following reasons:

- Not everyone has a carefully chosen ANSI color theme. Color combinations which may look fine on your system, may be unreadable on another machine. There is very little an app author or Textual can do to resolve this. Asking users to simply pick a better theme is not a good solution, since not all users will know how.
- ANSI colors can't be manipulated in the way Textual can do with other colors. Textual can blend colors and produce light and dark shades from an original color, which is used to create more readable text and user interfaces. Color blending will also be used to power future accessibility features.

Textual has a design system which guarantees apps will be readable on all platforms and terminals, and produces better results than ANSI colors.

Textual now includes multiple built-in themes, including themes inspired by ANSI-style color palettes such as `ansi-dark` and `ansi-light`, while still maintaining its design-system approach for readability and accessibility. Users can also customize source colors on a per-app or per-system basis to better integrate with their preferred terminal appearance.

!!! tip "Changed in version 0.80.0"

    Textual added an `ansi_color` boolean to App. If you set this to `True`, then Textual will not attempt to convert ANSI colors. Note that you will lose transparency effects if you enable this setting.
