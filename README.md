

[![Discord](https://img.shields.io/discord/1026214085173461072)](https://discord.gg/Enf6Z3qhVr)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/textual/1.0.0)](https://pypi.org/project/textual/)
[![PyPI version](https://badge.fury.io/py/textual.svg?)](https://badge.fury.io/py/textual)
![OS support](https://img.shields.io/badge/OS-macOS%20Linux%20Windows-red)



![textual-splash](https://github.com/user-attachments/assets/4caeb77e-48c0-4cf7-b14d-c53ded855ffd)

# Textual

<img align="right" width="250" alt="clock" src="https://github.com/user-attachments/assets/63e839c3-5b8e-478d-b78e-cf7647eb85e8" />

Build cross-platform user interfaces with a simple Python API. Run your apps in the terminal *or* a web browser.

Textual's API combines modern Python with the best of developments from the web world, for a lean app development experience.
De-coupled components and an advanced [testing](https://textual.textualize.io/guide/testing/) framework ensure you can maintain your app for the long-term.

Want some more examples? See the [examples](https://github.com/Textualize/textual/tree/main/examples) directory.

```python
"""
An App to show the current time.
"""

from datetime import datetime

from textual.app import App, ComposeResult
from textual.widgets import Digits


class ClockApp(App):
    CSS = """
    Screen { align: center middle; }
    Digits { width: auto; }
    """

    def compose(self) -> ComposeResult:
        yield Digits("")

    def on_ready(self) -> None:
        self.update_clock()
        self.set_interval(1, self.update_clock)

    def update_clock(self) -> None:
        clock = datetime.now().time()
        self.query_one(Digits).update(f"{clock:%T}")


if __name__ == "__main__":
    app = ClockApp()
    app.run()
```

> [!TIP]
> Textual is an asynchronous framework under the hood. Which means you can integrate your apps with async libraries &mdash; if you want to.
> If you don't want or need to use async, Textual won't force it on you. 



<img src="https://img.spacergif.org/spacer.gif" width="1" height="64"/>

## Widgets

Textual's library of [widgets](https://textual.textualize.io/widget_gallery/) covers everything from buttons, tree controls, data tables, inputs, text areas, and more…
Combined with a flexible [layout](https://textual.textualize.io/how-to/design-a-layout/) system, you can realize any User Interface you need.

Predefined themes ensure your apps will look good out of the box. 


<table>

<tr>

  <td>
    
  ![buttons](https://github.com/user-attachments/assets/2ac26387-aaa3-41ed-bc00-7d488600343c)
    
  </td>

  <td>
    
![tree](https://github.com/user-attachments/assets/61ccd6e9-97ea-4918-8eda-3ee0f0d3770e)
    
  </td>
  
</tr>


<tr>

  <td>
    
  ![datatables](https://github.com/user-attachments/assets/3e1f9f7a-f965-4901-a114-3c188bd17695)
    
  </td>

  <td>
    
![inputs](https://github.com/user-attachments/assets/b02aa203-7c37-42da-a1bb-2cb244b7d0d3)
    
  </td>
  
</tr>
<tr>

<td>

![listview](https://github.com/user-attachments/assets/963603bc-aa07-4688-bd24-379962ece871)

</td>

<td>

![textarea](https://github.com/user-attachments/assets/cd4ba787-5519-40e2-8d86-8224e1b7e506)
  
</td>

  
</tr>

</table>


<img src="https://img.spacergif.org/spacer.gif" width="1" height="32"/>

## Installing

Install Textual via pip:

```
pip install textual textual-dev
```

See [getting started](https://textual.textualize.io/getting_started/) for details.


<img src="https://img.spacergif.org/spacer.gif" width="1" height="32"/>

## Demo


Run the following command to see a little of what Textual can do:

```
python -m textual
```

Or try the [textual demo](https://github.com/textualize/textual-demo) *without* installing (requires [uv](https://docs.astral.sh/uv/)):

```bash
uvx --python 3.12 textual-demo
```

<img src="https://img.spacergif.org/spacer.gif" width="1" height="32"/>

## Dev Console

<img align="right" width="40%" alt="devtools" src="https://github.com/user-attachments/assets/12c60d65-e342-4b2f-9372-bae0459a7552" />


How do you debug an app in the terminal that is also running in the terminal?

The `textual-dev` package supplies a dev console that connects to your application from another terminal.
In addition to system messages and events, your logged messages and print statements will appear in the dev console.

See [the guide](https://textual.textualize.io/guide/devtools/) for other helpful tools provided by the `textual-dev` package.

<img src="https://img.spacergif.org/spacer.gif" width="1" height="32"/>

## Command Palette


Textual apps have a *fuzzy search* command palette.
Hit `ctrl+p` to open the command palette.

It is easy to extend the command palette with [custom commands](https://textual.textualize.io/guide/command_palette/) for your application.


![Command Palette](https://github.com/user-attachments/assets/94d8ec5d-b668-4033-a5cb-bf820e1b8d60)

<img src="https://img.spacergif.org/spacer.gif" width="1" height="32"/>

# Textual ❤️ Web

<img align="right" width="40%" alt="textual-serve" src="https://github.com/user-attachments/assets/a25820fb-87ae-433a-858b-ac3940169242">


Textual apps are equally at home in the browser as they are the terminal. Any Textual app may be served with `textual serve` &mdash; so you can share your creations on the web.
Here's how to serve the demo app:

```
textual serve "python -m textual"
```

In addition to serving your apps locally, you can serve apps with [Textual Web](https://github.com/Textualize/textual-web).

Textual Web's firewall-busting technology can serve an unlimited number of applications.

Since Textual apps have low system requirements, you can install them anywhere Python also runs. Turning any device into a connected device.
No desktop required!


<img src="https://img.spacergif.org/spacer.gif" width="1" height="32"/>


## Join us on Discord

Join the Textual developers and community on our [Discord Server](https://discord.gg/Enf6Z3qhVr).
