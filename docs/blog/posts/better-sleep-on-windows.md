---
draft: false
date: 2022-12-30
categories:
  - DevLog
authors:
  - willmcgugan
---
# A better asyncio sleep for Windows to fix animation

I spent some time optimizing Textual on Windows recently, and discovered something which may be of interest to anyone working with async code on that platform.

<!-- more -->

Animation, scrolling, and fading had always been unsatisfactory on Windows. Textual was usable, but the lag when scrolling made apps feel far less snappy that other platforms. On macOS and Linux, scrolling is fast enough that it feels close to a native app, not something running in a terminal. Yet the Windows experience never improved, even as Textual got faster with each release.

I had chalked this up to Windows Terminal being slow to render updates. After all, the classic Windows terminal was (and still is) glacially slow. Perhaps Microsoft just weren't focusing on performance.

In retrospect, that was highly improbable. Like all modern terminals, Windows Terminal uses the GPU to render updates. Even without focussing on performance, it should be fast.

I figured I'd give it one last attempt to speed up Textual on Windows. If I failed, Windows would forever be a third-class platform for Textual apps.

It turned out that it was nothing to do with performance, per se. The issue was with a single asyncio function: `asyncio.sleep`.

Textual has a `Timer` class which creates events at regular intervals. It powers the JS-like `set_interval` and `set_timer` functions. It is also used internally to do animation (such as smooth scrolling). This Timer class calls `asyncio.sleep` to wait the time between one event and the next.

On macOS and Linux, calling `asynco.sleep` is fairly accurate. If you call `sleep(3.14)`, it will return within 1% of 3.14 seconds. This is not the case for Windows, which for historical reasons uses a timer with a granularity of 15 milliseconds. The upshot is that sleep times will be rounded up to the nearest multiple of 15 milliseconds.

This limit appears to hold true for all async primitives on Windows. If you wait for something with a timeout, it will return on a multiple of 15 milliseconds. Fortunately there is work in the CPython pipeline to make this more accurate. Thanks to [Steve Dower](https://twitter.com/zooba) for pointing this out.

This lack of accuracy in the timer meant that timer events were created at a far slower rate than intended. Animation was slower because Textual was waiting too long between updates.

Once I had figured that out, I needed an alternative to `asyncio.sleep` for Textual's Timer class. And I found one. The following version of `sleep` is accurate to well within 1%:

```python
from time import sleep as time_sleep
from asyncio import get_running_loop

async def sleep(sleep_for: float) -> None:
    """An asyncio sleep.

    On Windows this achieves a better granularity than asyncio.sleep

    Args:
        sleep_for (float): Seconds to sleep for.
    """    
    await get_running_loop().run_in_executor(None, time_sleep, sleep_for)

```

That is a drop-in replacement for sleep on Windows. With it, Textual runs a *lot* smoother. Easily on par with macOS and Linux.

It's not quite perfect. There is a little *tearing* during full "screen" updates, but performance is decent all round. I suspect when [this bug]( https://bugs.python.org/issue37871) is fixed (big thanks to [Paul Moore](https://twitter.com/pf_moore) for looking in to that), and Microsoft implements [this protocol](https://gist.github.com/christianparpart/d8a62cc1ab659194337d73e399004036) then Textual on Windows will be A+.

This Windows improvement will be in v0.9.0 of [Textual](https://github.com/Textualize/textual), which will be released in a few days.
