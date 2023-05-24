# Screens

This chapter covers Textual's screen API. We will discuss how to create screens and switch between them.

## What is a screen?

Screens are containers for widgets that occupy the dimensions of your terminal. There can be many screens in a given app, but only one screen is active at a time.

Textual requires that there be at least one screen object and will create one implicitly in the App class. If you don't change the screen, any widgets you [mount][textual.widget.Widget.mount] or [compose][textual.widget.Widget.compose] will be added to this default screen.

<div class="excalidraw">
--8<-- "docs/images/dom1.excalidraw.svg"
</div>

## Creating a screen

You can create a screen by extending the [Screen][textual.screen.Screen] class which you can import from `textual.screen`. The screen may be styled in the same way as other widgets, with the exception that you can't modify the screen's dimensions (as these will always be the size of your terminal).

Let's look at a simple example of writing a screen class to simulate Window's [blue screen of death](https://en.wikipedia.org/wiki/Blue_screen_of_death).

=== "screen01.py"

    ```python title="screen01.py" hl_lines="18-24 29"
    --8<-- "docs/examples/guide/screens/screen01.py"
    ```

=== "screen01.css"

    ```sass title="screen01.css"
    --8<-- "docs/examples/guide/screens/screen01.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/screens/screen01.py" press="b"}
    ```

If you run this you will see an empty screen. Hit the ++b++ key to show a blue screen of death. Hit ++escape++ to return to the default screen.

The `BSOD` class above defines a screen with a key binding and compose method. These should be familiar as they work in the same way as apps.

The app class has a new `SCREENS` class variable. Textual uses this class variable to associate a name with screen object (the name is used to reference screens in the screen API). Also in the app is a key binding associated with the action `"push_screen('bsod')"`. The screen class has a similar action `"pop_screen"` bound to the ++escape++ key. We will cover these actions below.

## Named screens

You can associate a screen with a name by defining a `SCREENS` class variable in your app, which should be a `dict` that maps names on to `Screen` objects. The name of the screen may be used interchangeably with screen objects in much of the screen API.

You can also _install_ new named screens dynamically with the [install_screen][textual.app.App.install_screen] method. The following example installs the `BSOD` screen in a mount handler rather than from the `SCREENS` variable.

=== "screen02.py"

    ```python title="screen02.py" hl_lines="31-32"
    --8<-- "docs/examples/guide/screens/screen02.py"
    ```

=== "screen02.css"

    ```sass title="screen02.css"
    --8<-- "docs/examples/guide/screens/screen02.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/screens/screen02.py" press="b"}
    ```

Although both do the same thing, we recommend `SCREENS` for screens that exist for the lifetime of your app.

### Uninstalling screens

Screens defined in `SCREENS` or added with [install_screen][textual.app.App.install_screen] are _installed_ screens. Textual will keep these screens in memory for the lifetime of your app.

If you have installed a screen, but you later want it to be removed and cleaned up, you can call [uninstall_screen][textual.app.App.uninstall_screen].

## Screen stack

Textual apps keep a _stack_ of screens. You can think of this screen stack as a stack of paper, where only the very top sheet is visible. If you remove the top sheet, the paper underneath becomes visible. Screens work in a similar way.

!!! note

    You can also make parts of the top screen translucent, so that deeper screens show through. See [Screen opacity](#screen-opacity).

The active screen (top of the stack) will render the screen and receive input events. The following API methods on the App class can manipulate this stack, and let you decide which screen the user can interact with.

### Push screen

The [push_screen][textual.app.App.push_screen] method puts a screen on top of the stack and makes that screen active. You can call this method with the name of an installed screen, or a screen object.

<div class="excalidraw">
--8<-- "docs/images/screens/push_screen.excalidraw.svg"
</div>

#### Action

You can also push screens with the `"app.push_screen"` action, which requires the name of an installed screen.

### Pop screen

The [pop_screen][textual.app.App.pop_screen] method removes the top-most screen from the stack, and makes the new top screen active.

!!! note

    The screen stack must always have at least one screen. If you attempt to remove the last screen, Textual will raise a [ScreenStackError][textual.app.ScreenStackError] exception.

<div class="excalidraw">
--8<-- "docs/images/screens/pop_screen.excalidraw.svg"
</div>


When you pop a screen it will be removed and deleted unless it has been installed or there is another copy of the screen on the stack.

#### Action

You can also pop screens with the `"app.pop_screen"` action.

### Switch screen

The [switch_screen][textual.app.App.switch_screen] method replaces the top of the stack with a new screen.

<div class="excalidraw">
--8<-- "docs/images/screens/switch_screen.excalidraw.svg"
</div>

Like [pop_screen](#pop-screen), if the screen being replaced is not installed it will be removed and deleted.

#### Action

You can also switch screens with the `"app.switch_screen"` action which accepts the name of the screen to switch to.


## Screen opacity

If a screen has a background color with an *alpha* component, then the background color will be blended with the screen beneath it.
For example, if the top-most screen has a background set to `rgba(0,0,255,0.5)` then anywhere in the screen not occupied with a widget will display the *second* screen from the top, tinted with 50% blue.


<div class="excalidraw">
--8<-- "docs/images/screens/screen_alpha.excalidraw.svg"
</div>


!!! note

    Although parts of other screens may be made visible with background alpha, only the top-most is *active* (can respond to mouse and keyboard).

One use of background alpha is to style *modal dialogs* (see below).


## Modal screens

Screens may be used to create modal dialogs, where the main interface is temporarily disabled (but still visible) while the user is entering information.

The following example pushes a screen when you hit the ++q++ key to ask you if you really want to quit.
From the quit screen you can click either Quit to exit the app immediately, or Cancel to dismiss the screen and return to the main screen.

=== "Output"

    ```{.textual path="docs/examples/guide/screens/modal01.py"}
    ```

=== "Output (after pressing ++q++)"

    ```{.textual path="docs/examples/guide/screens/modal01.py" press="q"}
    ```

=== "modal01.py"

    ```python title="modal01.py"
    --8<-- "docs/examples/guide/screens/modal01.py"
    ```

=== "modal01.css"

    ```sass title="modal01.css"
    --8<-- "docs/examples/guide/screens/modal01.css"
    ```


Note the `request_quit` action in the app which pushes a new instance of `QuitScreen`.
This makes the quit screen active. If you click Cancel, the quit screen calls [pop_screen][textual.app.App.pop_screen] to return the default screen. This also removes and deletes the `QuitScreen` object.

There are two flaws with this modal screen, which we can fix in the same way.

The first flaw is that the app adds a new quit screen every time you press ++q++, even when the quit screen is still visible.
Consequently if you press ++q++ three times, you will have to click Cancel three times to get back to the main screen.
This is because bindings defined on App are always checked, and we call `push_screen` for every press of ++q++.

The second flaw is that the modal dialog doesn't *look* modal.
There is no indication that the main interface is still there, waiting to become active again.

We can solve both those issues by replacing our use of [Screen][textual.screen.Screen] with [ModalScreen][textual.screen.ModalScreen].
This screen sub-class will prevent key bindings on the app from being processed.
It also sets a background with a little alpha to allow the previous screen to show through.

Let's see what happens when we use `ModalScreen`.


=== "Output"

    ```{.textual path="docs/examples/guide/screens/modal02.py"}
    ```

=== "Output (after pressing ++q++)"

    ```{.textual path="docs/examples/guide/screens/modal02.py" press="q"}
    ```

=== "modal02.py"

    ```python title="modal02.py" hl_lines="3 15"
    --8<-- "docs/examples/guide/screens/modal02.py"
    ```

=== "modal01.css"

    ```sass title="modal01.css"
    --8<-- "docs/examples/guide/screens/modal01.css"
    ```

Now when we press ++q++, the dialog is displayed over the main screen.
The main screen is darkened to indicate to the user that it is not active, and only the dialog will respond to input.

## Returning data from screens

It is a common requirement for screens to be able to return data.
For instance, you may want a screen to show a dialog and have the result of that dialog processed *after* the screen has been popped.

To return data from a screen, call [`dismiss()`][textual.screen.Screen.dismiss] on the screen with the data you wish to return.
This will pop the screen and invoke a callback set when the screen was pushed (with [`push_screen`][textual.app.App.push_screen]).

Let's modify the previous example to use `dismiss` rather than an explicit `pop_screen`.

=== "modal03.py"

    ```python title="modal03.py" hl_lines="15 27-30 47-50 52"
    --8<-- "docs/examples/guide/screens/modal03.py"
    ```

    1. See below for an explanation of the `[bool]`

=== "modal01.css"

    ```sass title="modal01.css"
    --8<-- "docs/examples/guide/screens/modal01.css"
    ```

In the `on_button_pressed` message handler we call `dismiss` with a boolean that indicates if the user has chosen to quit the app.
This boolean is passed to the `check_quit` function we provided when `QuitScreen` was pushed.

Although this example behaves the same as the previous code, it is more flexible because it has removed responsibility for exiting from the modal screen to the caller.
This makes it easier for the app to perform any cleanup actions prior to exiting, for example.

Returning data in this way can help keep your code manageable by making it easy to re-use your `Screen` classes in other contexts.

### Typing screen results

You may have noticed in the previous example that we changed the base class to `ModalScreen[bool]`.
The addition of `[bool]` adds typing information that tells the type checker to expect a boolean in the call to `dismiss`, and that any callback set in `push_screen` should also expect the same type. As always, typing is optional in Textual, but this may help you catch bugs.
