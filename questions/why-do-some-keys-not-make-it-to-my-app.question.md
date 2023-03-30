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

When [creating bindings for your
application](https://textual.textualize.io/guide/input/#bindings) we
recommend picking keys and key combinations that are supported on as many
platforms as possible.

The easiest way to test different environments to see which
[keys](https://textual.textualize.io/guide/input/#keyboard-input) can be
detected is to use `textual keys`.
