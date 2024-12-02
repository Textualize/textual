
[![Discord](https://img.shields.io/discord/1026214085173461072)](https://discord.gg/Enf6Z3qhVr)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/textual/0.87.1)](https://pypi.org/project/textual/)
[![PyPI version](https://badge.fury.io/py/textual.svg)](https://badge.fury.io/py/textual)
![OS support](https://img.shields.io/badge/OS-macOS%20Linux%20Windows-red)



# Textual

Build cross-platform user interfaces with a simple Python API.

Run your apps in the terminal *or* a web browser.


## Widgets

Textual's library of builtin [widgets](https://textual.textualize.io/widget_gallery/) covers everything from buttons, tree controls, data tables, inputs, text areas, and more…

Predefined themes means that your apps will look good out of the box. 



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

With a (growing) library of widgets and a flexible [layout](https://textual.textualize.io/how-to/design-a-layout/) system, you can build apps as easily as you can CLIs.

Textual's intuitive Python API makes building gorgeous terminal / web interfaces a joy.


## Testing

Textual's [testing framework](https://textual.textualize.io/guide/testing/) automates keys and mouse clicks / movement.
Allowing you to write tests for user interactions.

Additionally, [pytest-text-snapshot](https://github.com/Textualize/pytest-textual-snapshot) can catch visual regressions long before your code goes in to production.



## Installing

Install Textual via pip:

```
pip install textual textual-dev
```

See [getting started](https://textual.textualize.io/getting_started/) for details.



## Demo

Run the following command to see a little of what Textual can do:

```
python -m textual
```

Or try the [textual demo](https://github.com/textualize/textual-demo) *without* installing (requires [uv](https://docs.astral.sh/uv/)):

```bash
uvx --python 3.12 textual-demo
```


## Textual ❤️ Web

Textual apps are equally at home in the browser as they are the terminal.

Any Textual app may be served with "textual serve" &mdash; so you cah share your creations on the web.

Here's how to serve the demo app:

```
textual serve "python -m textual"
```

In addition to serving your apps locally, you can serve apps with [Textual-Web](https://github.com/Textualize/textual-web).

Textual Web's firewall-busting technology can serve an unlimited number of applications on the web.
Turning any device in to a connected device.

Since Textual apps have low system requirements, you can install them anywhere Python also runs.
No desktop required.

## Documentation

Head over to the [Textual documentation](http://textual.textualize.io/) to start building!

## Join us on Discord

Join the Textual developers and community on our [Discord Server](https://discord.gg/Enf6Z3qhVr).
