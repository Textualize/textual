# Button

The `Button` widget creates a clickable button on screen 

## Parameters

`label`

: A renderable type to display within the button

`name`

: A string used to reference the button, this parameter is also sent with the button press event

`style`

: The style of the button, using standard textual syntax

## Reacting to clicks

To handle button presses, we need a `handle_button_pressed` function, like the following:

Where a button with a name of "10" denotes an exit and other numbers denote some value that the user has clicked

```python
# Function that activates on a button press
    async def handle_button_pressed(self, message: ButtonPressed) -> None:
        """This code is executed on a button press"""
        
        # Make sure that we are looking at a button press
        assert isinstance(message.sender, Button)
        button_name = message.sender.name

        # Make sure we are not exiting
        if int(button_name) != 10:
            # If not the exit button, then change some variable to the name of the button the user clicked
            somevalue = int(button_name)
            # You may need a refresh here depending on your needs
        else:
            # Exit
            await self.shutdown()
```

## Code

https://github.com/Textualize/textual/blob/main/src/textual/widgets/_button.py
