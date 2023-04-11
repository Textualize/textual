---
title: "Why do some key combinations never make it to my app?"
alt_titles:
  - "Cmd key isn't working"
  - "Command key isn't working"
  - "Alt key isn't working"
  - "Ctrl and function key isn't working"
  - "Control and function key isn't working"
---

Textual can only ever support key combinations that are passed on by your
terminal application. Which keys get passed on can differ from terminal to
terminal, and from operating system to operating system.

Because of this it's best to stick to key combinations that are known to be
universally-supported; these include the likes of:

- Letters
- Numbers
- Numbered function keys (especially F1 through F10)
- Space
- Return
- Arrow, home, end and page keys
- Control
- Shift

When [creating bindings for your
application](https://textual.textualize.io/guide/input/#bindings) we
recommend picking keys and key combinations from the above.

Keys that aren't normally passed through by terminals include Cmd and Option
on macOS, and the Windows key on Windows.

If you need to test what [key
combinations](https://textual.textualize.io/guide/input/#keyboard-input)
work in different environments you can try them out with `textual keys`.
