---
draft: false
date: 2024-02-20
categories:
  - DevLog
authors:
  - willmcgugan
---

# Remote memory profiling with Memray

[Memray](https://github.com/bloomberg/memray) is a memory profiler for Python, built by some very smart devs at Bloomberg.
It is a fantastic tool to identify memory leaks in your code or other libraries (down to the C level)!

They recently added a [Textual](https://github.com/textualize/textual/) interface which looks amazing, and lets you monitor your process right from the terminal:

![Memray](https://raw.githubusercontent.com/bloomberg/memray/main/docs/_static/images/live_animated.webp)

<!-- more -->

You would typically run this locally, or over a ssh session, but it is also possible to serve the interface over the web with the help of [textual-web](https://github.com/Textualize/textual-web).
I'm not sure if even the Memray devs themselves are aware of this, but here's how.

First install Textual web (ideally with pipx) alongside Memray:

```bash
pipx install textual-web
```

Now you can serve Memray with the following command (replace the text in quotes with your Memray options):

```bash
textual-web -r "memray run --live -m http.server"
```

This will return a URL you can use to access the Memray app from anywhere.
Here's a quick video of that in action:

<iframe style="aspect-ratio: 16 /10" width="100%" src="https://www.youtube.com/embed/7lpoUBdxzus" title="Serving Memray with Textual web" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## Found this interesting?


Join our [Discord server](https://discord.gg/Enf6Z3qhVr) if you want to discuss this post with the Textual devs or community.
