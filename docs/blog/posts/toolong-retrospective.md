---
draft: false
date: 2024-02-11
categories:
  - DevLog
authors:
  - willmcgugan
---

# File magic with the Python standard library

I recently published [Toolong](https://github.com/textualize/toolong), an app for viewing log files.
There were some interesting technical challenges in building Toolong that I'd like to cover in this post.

<!-- more -->

!!! note "Python is awesome"

    This isn't specifically [Textual](https://github.com/textualize/textual/) related. These techniques could be employed in any Python project.

These techniques aren't difficult, and shouldn't be beyond anyone with an intermediate understanding of Python.
They are the kind of "if you know it you know it" knowledge that you may not need often, but can make a massive difference when you do!

## Opening large files

If you were to open a very large text file (multiple gigabyte in size) in an editor, you will almost certainly find that it takes a while. You may also find that it doesn't load at all because you don't have enough memory, or it disables features like syntax highlighting.

This is because most app will do something analogous to this:

```python
with open("access.log", "rb") as log_file:
    log_data = log_file.read()
```

All the data is read in to memory, where it can be easily processed.
This is fine for most files of a reasonable size, but when you get in to the gigabyte territory the read and any additional processing will start to use a significant amount of time and memory.

Yet Toolong can open a file of *any* size in a second or so, with syntax highlighting.
It can do this because it doesn't need to read the entire log file in to memory.
Toolong opens a file and reads only the portion of it required to display whatever is on screen at that moment.
When you scroll around the log file, Toolong reads the data off disk as required -- fast enough that you may never even notice it.

### Scanning lines

There is an additional bit of work that Toolong has to do up front in order to show the file.
If you open a large file you may see a progress bar and a message about "scanning".

Toolong needs to know where every line starts and ends in a log file, so it can display a scrollbar bar and allow the user to navigate lines in the file.
In other words it needs to know the offset of every new line (`\n`) character within the file.

This isn't a hard problem in itself.
You might have imagined a loop that reads a chunk at a time and searches for new lines characters.
And that would likely have worked just fine, but there is a bit of magic in the Python standard library that can speed that up.

The [mmap](https://docs.python.org/3/library/mmap.html) module is a real gem for this kind of thing.
A *memory mapped file* is an OS-level construct that *appears* to load a file instantaneously.
In Python you get an object which behaves like a `bytearray`, but loads data from disk when it is accessed.
The beauty of this module is that you can work with files in much the same way as if you had read the entire file in to memory, while leaving the actual reading of the file to the OS.

Here's the method that Toolong uses to scan for line breaks.
Forgive the micro-optimizations, I was going for raw execution speed here.

```python
    def scan_line_breaks(
        self, batch_time: float = 0.25
    ) -> Iterable[tuple[int, list[int]]]:
        """Scan the file for line breaks.

        Args:
            batch_time: Time to group the batches.

        Returns:
            An iterable of tuples, containing the scan position and a list of offsets of new lines.
        """
        fileno = self.fileno
        size = self.size
        if not size:
            return
        log_mmap = mmap.mmap(fileno, size, prot=mmap.PROT_READ)
        rfind = log_mmap.rfind
        position = size
        batch: list[int] = []
        append = batch.append
        get_length = batch.__len__
        monotonic = time.monotonic
        break_time = monotonic()

        while (position := rfind(b"\n", 0, position)) != -1:
            append(position)
            if get_length() % 1000 == 0 and monotonic() - break_time > batch_time:
                break_time = monotonic()
                yield (position, batch)
                batch = []
                append = batch.append
        yield (0, batch)
        log_mmap.close()
```

This code runs in a thread (actually a [worker](https://textual.textualize.io/guide/workers/)), and will generate line breaks in batches. Without batching, it risks slowing down the UI with millions of rapid events.

It's fast because most of the work is done in `rfind`, which runs at C speed, while the OS reads from the disk.

## Watching a file for changes

Toolong can tail files in realtime.
When something appends to the file, it will be read and displayed virtually instantly.
How is this done?

You can easily *poll* a file for changes, by periodically querying the size or timestamp of a file until it changes.
The downside of this is that you don't get notified immediately if a file changes between polls.
You could poll at a very fast rate, but if you were to do that you would end up burning a lot of CPU for no good reason.

There is a very good solution for this in the standard library.
The [selectors](https://docs.python.org/3/library/selectors.html) module is typically used for working with sockets (network data), but can also work with files (at least on macOS and Linux).

!!! info "Software developers are an unimaginative bunch when it comes to naming things"

    Not to be confused with CSS [selectors](https://textual.textualize.io/guide/CSS/#selectors)!    

The selectors module can tell you precisely when a file can be read.
It can do this very efficiently, because it relies on the OS to tell us when a file can be read, and doesn't need to poll.

You register a file with a `Selector` object, then call `select()` which returns as soon as there is new data available for reading.

See [watcher.py](https://github.com/Textualize/toolong/blob/main/src/toolong/watcher.py) in Toolong, which runs a thread to monitors files for changes with a selector.

!!! warning "Addendum"

    So it turns out that watching regular files for changes with selectors only works with `KqueueSelector` which is the default on macOS.
    Disappointingly, the Python docs aren't clear on this.
    Toolong will use a polling approach where this selector is unavailable.

## Textual learnings

This project was a chance for me to "dogfood" Textual.
Other Textual devs have build some cool projects ([Trogon](https://github.com/Textualize/trogon) and [Frogmouth](https://github.com/Textualize/frogmouth)), but before Toolong I had only ever written example apps for docs.

I paid particular attention to Textual error messages when working on Toolong, and improved many of them in Textual.
Much of what I improved were general programming errors, and not Textual errors per se.
For instance, if you forget to call `super()` on a widget constructor, Textual used to give a fairly cryptic error.
It's a fairly common gotcha, even for experience devs, but now Textual will detect that and tell you how to fix it.

There's a lot of other improvements which I thought about when working on this app.
Mostly quality of life features that will make implementing some features more intuitive.
Keep an eye out for those in the next few weeks.

## Found this interesting?

If you would like to talk about this post or anything Textual related, join us on the [Discord server](https://discord.gg/Enf6Z3qhVr).
