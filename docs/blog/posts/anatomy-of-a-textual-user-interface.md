---
draft: false
date: 2024-09-15
categories:
  - DevLog
authors:
  - willmcgugan
---

# Anatomy of a Textual User Interface

!!! note "My bad 🤦"

    The date is wrong on this post&mdash;it was actually published on the 2nd of September 2024.
    I don't want to fix it, as that would break the URL.  

I recently wrote a [TUI](https://en.wikipedia.org/wiki/Text-based_user_interface) to chat to an AI agent in the terminal.
I'm not the first to do this (shout out to [Elia](https://github.com/darrenburns/elia) and [Paita](https://github.com/villekr/paita)), but I *may* be the first to have it reply as if it were the AI from the Aliens movies?

Here's a video of it in action:



<iframe width="100%" style="aspect-ratio:1512 / 982"  src="https://www.youtube.com/embed/hr5JvQS4d_w" title="Mother AI" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Now let's dissect the code like Bishop dissects a facehugger.

<!-- more -->

## All right, sweethearts, what are you waiting for? Breakfast in bed?

At the top of the file we have some boilerplate:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "llm",
#     "textual",
# ]
# ///
from textual import on, work
from textual.app import App, ComposeResult
from textual.widgets import Header, Input, Footer, Markdown
from textual.containers import VerticalScroll
import llm

SYSTEM = """Formulate all responses as if you where the sentient AI named Mother from the Aliens movies."""
```

The text in the comment is a relatively new addition to the Python ecosystem.
It allows you to specify dependencies inline so that tools can setup an environment automatically.
The format of the comment was developed by [Ofek Lev](https://github.com/ofek) and first implemented in [Hatch](https://hatch.pypa.io/latest/blog/2024/05/02/hatch-v1100/#python-script-runner), and has since become a Python standard via [PEP 0723](https://peps.python.org/pep-0723/) (also authored by Ofek). 

!!! note

    PEP 0723 is also implemented in [uv](https://docs.astral.sh/uv/guides/scripts/#running-scripts).

I really like this addition to Python because it means I can now share a Python script without the recipient needing to manually setup a fresh environment and install dependencies.

After this comment we have a bunch of imports: [textual](https://github.com/textualize/textual) for the UI, and [llm](https://llm.datasette.io/en/stable/) to talk to ChatGPT (also supports other LLMs).

Finally, we define `SYSTEM`, which is the *system prompt* for the LLM.

## Look, those two specimens are worth millions to the bio-weapons division.

Next up we have the following:

```python

class Prompt(Markdown):
    pass


class Response(Markdown):
    BORDER_TITLE = "Mother"
```

These two classes define the widgets which will display text the user enters and the response from the LLM.
They both extend the builtin [Markdown](https://textual.textualize.io/widgets/markdown/) widget, since LLMs like to talk in that format.

## Well, somebody's gonna have to go out there. Take a portable terminal, go out there and patch in manually.

Following on from the widgets we have the following:

```python
class MotherApp(App):
    AUTO_FOCUS = "Input"

    CSS = """
    Prompt {
        background: $primary 10%;
        color: $text;
        margin: 1;        
        margin-right: 8;
        padding: 1 2 0 2;
    }

    Response {
        border: wide $success;
        background: $success 10%;   
        color: $text;             
        margin: 1;      
        margin-left: 8; 
        padding: 1 2 0 2;
    }
    """
```

This defines an app, which is the top-level object for any Textual app.

The `AUTO_FOCUS` string is a classvar which causes a particular widget to receive input focus when the app starts. In this case it is the `Input` widget, which we will define later.

The classvar is followed by a string containing CSS.
Technically, TCSS or *Textual Cascading Style Sheets*, a variant of CSS for terminal interfaces.

This isn't a tutorial, so I'm not going to go in to a details, but we're essentially setting properties on widgets which define how they look.
Here I styled the prompt and response widgets to have a different color, and tried to give the response a retro tech look with a green background and border.

We could express these styles in code.
Something like this:

```python
self.styles.color = "red"
self.styles.margin = 8
```

Which is fine, but CSS shines when the UI get's more complex.

## Look, man. I only need to know one thing: where they are.

After the app constants, we have a method called `compose`:

```python
    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="chat-view"):
            yield Response("INTERFACE 2037 READY FOR INQUIRY")
        yield Input(placeholder="How can I help you?")
        yield Footer()
```

This method adds the initial widgets to the UI. 

`Header` and `Footer` are builtin widgets.

Sandwiched between them is a `VerticalScroll` *container* widget, which automatically adds a scrollbar (if required). It is pre-populated with a single `Response` widget to show a welcome message (the `with` syntax places a widget within a parent widget). Below that is an `Input` widget where we can enter text for the LLM.

This is all we need to define the *layout* of the TUI.
In Textual the layout is defined with styles (in the same was as color and margin).
Virtually any layout is possible, and you never have to do any math to calculate sizes of widgets&mdash;it is all done declaratively.

We could add a little CSS to tweak the layout, but the defaults work well here.
The header and footer are *docked* to an appropriate edge.
The `VerticalScroll` widget is styled to consume any available space, leaving room for widgets with a defined height (like our `Input`).

If you resize the terminal it will keep those relative proportions.

## Look into my eye.

The next method is an *event handler*.


```python
    def on_mount(self) -> None:
        self.model = llm.get_model("gpt-4o")
```

This method is called when the app receives a Mount event, which is one of the first events sent and is typically used for any setup operations.

It gets a `Model` object got our LLM of choice, which we will use later.

Note that the [llm](https://llm.datasette.io/en/stable/) library supports a [large number of models](https://llm.datasette.io/en/stable/openai-models.html), so feel free to replace the string with the model of your choice.

## We're in the pipe, five by five.

The next method is also a message handler:

```python
    @on(Input.Submitted)
    async def on_input(self, event: Input.Submitted) -> None:
        chat_view = self.query_one("#chat-view")
        event.input.clear()
        await chat_view.mount(Prompt(event.value))
        await chat_view.mount(response := Response())
        response.anchor()
        self.send_prompt(event.value, response)
```

The decorator tells Textual to handle the `Input.Submitted` event, which is sent when the user hits return in the Input.

!!! info "More on event handlers"

    There are two ways to receive events in Textual: a naming convention or the decorator.
    They aren't on the base class because the app and widgets can receive arbitrary events.

When that happens, this method clears the input and adds the prompt text to the `VerticalScroll`.
It also adds a `Response` widget to contain the LLM's response, and *anchors* it.
Anchoring a widget will keep it at the bottom of a scrollable view, which is just what we need for a chat interface.

Finally in that method we call `send_prompt`.

## We're on an express elevator to hell, going down!

Here is `send_prompt`:

```python
    @work(thread=True)
    def send_prompt(self, prompt: str, response: Response) -> None:
        response_content = ""
        llm_response = self.model.prompt(prompt, system=SYSTEM)
        for chunk in llm_response:
            response_content += chunk
            self.call_from_thread(response.update, response_content)
```

You'll notice that it is decorated with `@work`, which turns this method in to a *worker*.
In this case, a *threaded* worker. Workers are a layer over async and threads, which takes some of the pain out of concurrency.

This worker is responsible for sending the prompt, and then reading the response piece-by-piece.
It calls the Markdown widget's `update` method which replaces its content with new Markdown code, to give that funky streaming text effect.


## Game over man, game over!

The last few lines creates an app instance and runs it:

```python
if __name__ == "__main__":
    app = MotherApp()
    app.run()
```

You may need to have your [API key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key) set in an environment variable.
Or if you prefer, you could set in the `on_mount` function with the following:

```python
self.model.key = "... key here ..."
```

## Not bad, for a human.

Here's the [code for the Mother AI](https://gist.github.com/willmcgugan/648a537c9d47dafa59cb8ece281d8c2c).

Run the following in your shell of choice to launch mother.py (assumes you have [uv](https://docs.astral.sh/uv/) installed):

```base
uv run mother.py
```

## You know, we manufacture those, by the way.

Join our [Discord server](https://discord.gg/Enf6Z3qhVr) to discuss more 80s movies (or possibly TUIs).
