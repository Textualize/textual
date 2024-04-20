---
draft: true
date: 2024-04-20
categories:
  - DevLog
authors:
  - willmcgugan
---

# Behind the Curtain of Inline Terminal Applications

Textual recently added the ability to run *inline* terminal apps.
You can see this in action if you run the [calculator example](https://github.com/Textualize/textual/blob/main/examples/calculator.py):

![Inline Calculator](../images/calcinline.png)

The application appears directly under the prompt, rather than occupying the full height of the screen&mdash;which is more typical of TUI applications.
You can interact with the calculator using keys *or* the mouse.
When you press ++ctrl+c++ the calculator disappears and returns you to the prompt.

Here's another app that creates an inline code editor:

=== "Video"

    <div class="video-wrapper">
        <iframe width="852" height="525" src="https://www.youtube.com/embed/Dt70oSID1DY" title="Inline app" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>


=== "inline.py"
    ```python 
    from textual.app import App, ComposeResult
    from textual.widgets import TextArea


    class InlineApp(App):
        CSS = """
        TextArea {
            height: auto;
            max-height: 50vh;
        }
        """

        def compose(self) -> ComposeResult:
            yield TextArea(language="python")


    if __name__ == "__main__":
        InlineApp().run(inline=True)

    ```

This post will cover some of what goes on under the hood to make such inline apps work.


## Programming the terminal

Firstly, let's recap how you program the terminal.
Broadly speaking, the terminal is a device for displaying text.
You write (or print) text to the terminal which typically appears at the end of a continually expanding text buffer.
In addition to text you can also send [escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code), which are short sequences of characters that instruct the terminal to do things such as change the text color, scroll, or other more exotic things.

We only need a few of these escape codes to implement inline apps.

!!! note

    I will gloss over the exact characters used for these escape codes.
    It's enough to know that they exist for now.
    If you implement any of this yourself, refer to the [wikipedia article](https://en.wikipedia.org/wiki/ANSI_escape_code). 

## Rendering frames

The first step is to display the app, which is simply text (possibly with escape sequences to change color and style).
The lines are terminated with a newline character (`"\n"`), *except* for the very last line (otherwise we get a blank line a the end which we don't need).
Rather than a final newline, we write an escape code that moves the *cursor* back to it's prior position.

The cursor is where text will be written.
It's the same cursor you see as you type.
Normally it will be at the end of the text in the terminal, but it can be moved around terminal with escape codes.
It can be made invisible (as in Textual apps), but the terminal will keep track of the cursor, even if it can not be seen.

Because we move the cursor back to its original starting position, when we write a subsequent frame it overwrites the previous frame.
Here's a diagram that shows what happens.

!!! note

    I've drawn the cursor in red, although it isn't typically visible.


<div class="excalidraw">
--8<-- "docs/blog/images/inline1.excalidraw.svg"
</div>


There is an additional consideration that comes in to play when the output has less lines than the previous frame.
If we were to write a shorter frame, it wouldn't fully overwrite the previous frame.
We would be left with a few lines of a previous frame that wouldn't update.

The solution to this problem is to write an escape code that clears lines from the cursor downwards before we write a smaller frame.

## Cursor input

The cursor tells the terminal where any text will be written by the app, but it also assumes this will be where the user enters text.
If you enter CJK (Chinese Japanese Korean) text in to the terminal, you will typically see a floating control that points where new text will be written. If you are on a Mac, the emoji entry dialog (++ctrl+cmd+space++) will also point at the current cursor position. To make this work in a sane way, we need to move the terminal's cursor to where any new text will appear.

<div class="excalidraw">
--8<-- "docs/blog/images/inline2.excalidraw.svg"
</div>

This only really impacts text entry (such as the [Input](https://textual.textualize.io/widget_gallery/#input) and [TextArea](https://textual.textualize.io/widget_gallery/#textarea) widgets).

## Mouse control

Inline apps in Textual also support mouse input.
This works in almost the same way as fullscreen apps.
There is an escape code to enable mouse input which sends encoded mouse coordinates to the app via standard input (in much the same way as you would read keys).

The only real challenge with using the mouse in inline apps is that the mouse coordinates are relative to the top left of the terminal window (*not* the top left of our frame).
To work around this difference, we need to detect where the cursor is relative to the terminal.

The only way I have discovered to do this, is to query the cursor position from the terminal, which we can do by sending an escape sequence then reading the cursor position from standard input. Once we have this information we can work out the mouse position relative to our frame, so that the app knows where you are clicking.

## tl;dr

[Escapes codes](https://en.wikipedia.org/wiki/ANSI_escape_code).

## Found this interesting?

If you are interested in Textual, join our [Discord server](https://discord.gg/Enf6Z3qhVr).

Or follow me for more terminal shenanigans.

- [@willmcgugan](https://twitter.com/willmcgugan)
- [mastodon.social/@willmcgugan](https://mastodon.social/@willmcgugan)
