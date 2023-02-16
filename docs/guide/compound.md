# Compound widgets

## Overview

--8<-- "docs/snippets/compound_widget_overview.md"

This guide will introduce you to the main concepts needed when developing compound widgets.
To that end, we will be building some compound widgets and then we will use them in an app.

We will start by building an editable text widget that shows some text and then contains two buttons:
one lets us edit the text and the other confirms the changes we made to the text.
We will use this simpler compound widget to illustrate the points made above.

Then, we will subclass that widget to create a more specialised editable text widget that is specifically used for dates.

Finally, we will use both those widgets to build yet another compound widget which will be the main building block of a TODO tracking app.
By building this app we will be able to demonstrate how the communication between compound widgets and applications works.


## `EditableText`

### Structuring your compound widget

The `EditableText` widget is a widget that contains a label to display text.
If the "edit" button is pressed, the label is switched out and the user sees an input field to edit the text.
When the "confirm" button is pressed, the label comes back into view to display the new text.

Taking this into account, the widget `EditableText` will need to yield the following sub-widgets in its `compose` method:

 - a `Label` to display the text;
 - an `Input` to allow editing of the text;
 - a `Button` to switch to editing mode; and
 - a `Button` to switch to display mode.

Below, you can find the skeleton for our widget `EditableText`.
We inherit from `Static`, instead of from `Widget`, because `Static` does some extra work for us, like caching the rendering.

=== "editabletext01.py"

    ```py hl_lines="5 8-12"
    --8<-- "docs/examples/guide/compound/editabletext01.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/compound/editabletext01.py" lines=10}
    ```


### Enabling the styling of your compound widget

When you create a compound widget, and especially if you have reusability in mind, you need to set up your widget in such a way that it can be styled by users.
This may entail documenting well the specific widgets that make up your compound widget or it may include using semantic classes that identify the purpose of the sub-widgets.

In this guide, we will add classes to each sub-widget that identify the purpose of each sub-widget.
There is an added advantage of using classes to identify the components of our compound widget, and that has to do with the fact that you don't have to commit to using a specific class for a specific sub-widget/functionality.

On top of adding classes that identify the purpose of each sub-widget, we will also use a class to hide either the input or the label, depending on whether we are currently editing or displaying text.

After adding the classes to our widgets, we can style them.

!!! Warning

    The more appropriate thing to do would be to add the default styling of our compound widget in the attribute `DEFAULT_CSS` of the widget itself.
    However, that would make the code snippets in this guide much longer and unwieldy.
    Because of that, we will put the default styling for the compound widget in a separate CSS file for now.

=== "editabletext02.py"

    ```py hl_lines="12 14 15 16"
    --8<-- "docs/examples/guide/compound/editabletext02.py"
    ```

    1. The default styling of our compound widget should go here.
    2. We need to plug in the CSS file with the default style of our compound widget.

=== "editabletext_defaultcss.css"

    ```sass hl_lines="7 11 18 24 30"
    --8<-- "docs/examples/guide/compound/editabletext_defaultcss.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/compound/editabletext02.py" lines=10}
    ```

!!! Tip

    The classes have verbose names, like `editabletext--input`, to minimise the risk of name clashing in larger applications.
    The same applies to the class `ethidden` that is used to control whether the input or the label is being shown and to control which button is displayed.


### Wiring the components together

We have our four components laid out and styled but we still need to wire them in order to implement the kind of behaviour we want.

To that end, we will do the following modifications:

 - save the sub-widgets as attributes for easier retrieval later;
 - implement a property `is_editing` to determine whether we are in editing mode or not;
 - implement a handler for button presses; and
 - switch between editing and display modes when the buttons are pressed through two methods `switch_to_editing_mode` and `switch_to_display_mode`.


=== "editabletext03.py"

    ```py hl_lines="35 39 45 57"
    --8<-- "docs/examples/guide/compound/editabletext03.py"
    ```

    1. The property `is_editing` checks if the internal `Input` widget is being shown or not.
    2. When we press the edit/confirm button, we check in which mode we are in and switch to the other one.

We implement the button handler in terms of two auxiliary methods because those two methods will provide the interface for users to programmatically change the mode the widget is in.

!!! Tip

    When creating a compound widget, use methods to add the ability for the users (for example, in apps) to control the compound widget programmatically.


### Communicating with the compound widget

When you need to communicate with the compound widget, for example to manipulate its state, you should try to do that through methods or reactive attributes documented for that effect.

Thus, when you are implementing a compound widget, you need to think of the methods that the user will need, because we don't want users to mess with the internals of the compound widget.

In our `EditableText` example, we have two "public" methods that users are welcome to use: `switch_to_display_mode` and `switch_to_edit_mode`.

For an example use case, we will create a small app that uses some `EditableText` widgets and we will use `switch_to_edit_mode` to ensure all `EditableText` instances are ready to be edited when the app launches:

=== "editabletext04_app.py"

    ```py hl_lines="18"
    --8<-- "docs/examples/guide/compound/editabletext04_app.py"
    ```

    1. We use a "public method" to tell each `EditableText` widget to switch to editing mode.

=== "editabletext04.py"

    ```py
    --8<-- "docs/examples/guide/compound/editabletext04.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/compound/editabletext04_app.py"}
    ```

In the output above, you will see that the three `EditableText` widgets are in edit mode because you can see the placeholder text in the internal `Input` widgets.


### Posting custom messages

A compound widget must define messages that are posted at the appropriate times to allow user apps / screens to interact with the compound widget.
In the case of our widget `EditableText`, those messages will be:

 - `EditableText.Display`, posted when the widget switches into display mode; and
 - `EditableText.Edit`, posted when the widget switches into edit mode.

Furthermore, when handling the message `Button.Pressed` from the sub-widget `Button`, we need to use the method [`.stop`][textual.message.Message.stop] to prevent it from bubbling.
If we do not, app implementers may inadvertently handle button presses that are internal to the widget `EditableText`.

This brings is the final change we will make to the widget `EditableText`:

=== "editabletext.py"

    ```py hl_lines="53-54 56-57 80 100 116"
    --8<-- "docs/examples/guide/compound/editabletext.py"
    ```

    1. Posted when the widget switches to display mode.
    2. Posted when the widget switches to edit mode.
    3. We prevent the message `Button.Pressed` from bubbling up the DOM hierarchy.
    4. We post the custom event `EditableText.Display` so that container apps / screens can act appropriately.
    5. We post the custom event `EditableText.Edit` so that container apps / screens can act appropriately.


## Intermission

On our way to understanding how to define and work with compound widgets, we have implemented `EditableText`.
The next few sections will build on top of that compound widget to build a basic TODO tracking app.
In order to build this app, we will build two more compound widgets:

 1. `DatePicker` – does exactly the same thing as an `EditableText`, but to write down dates; and
 2. `TodoItem` – represents a task to be completed in the TODO app.

These two widgets will use the patterns highlighted in the previous sections to communicate with the app.

## `DatePicker`

We implement a `DatePicker` widget at the expense of the widget `EditableText`, but programmers do not need to know that.
This means, we do not want the messages `EditableText.Display` and `EditableText.Edit` to be posted when using a `DatePicker`.

In the widget `DatePicker`, we define more appropriate messages to post when the date is selected and cleared.
Thus, when we receive a message `Display` or `Edit` from the superclass, we stop it from bubbling with the method [`.stop`][textual.message.Message.stop] and post our custom `DatePicker` messages instead:

```py hl_lines="12 15 22 30"
--8<-- "docs/examples/guide/compound/date_picker_messages.py"
```

1. The message `DateCleared` is to be used when the date is edited and completely erased.
2. The message `Selected` is sent when the user inputs a valid date and confirms it.
3. We handle the message `EditableText.Display` from the superclass to prevent it from bubbling and then we post the appropriate message from `DatePicker`.
4. We handle the message `EditableText.Edit` from the superclass to prevent it from bubbling.


On top of doing this custom message handling, we also modify the placeholder text in the underlying `Input` widget, we add a bell sound when the user tries to input a date that cannot be parsed, and we add a property `date` to make it easier to access the date of the `DatePicker`:

```py hl_lines="24 29-31 46"
--8<-- "docs/examples/guide/compound/date_picker.py"
```

!!! Tip

    When creating a widget by inheriting from another widget, be sure to determine whether or not you want the super class's messages to be available to be handled by other apps.


## `TodoItem`

The implementation of `TodoItem` puts together an `EditableText`, a `DatePicker`, and some other built-in widgets to build a more complex compound widget.
This implementation shows the same techniques discussed previously, namely:

 - Posting custom messages to communicate with apps or screens that might contain this widget. For example, when the item is marked as done we emit a message `TodoItem.Done`.
 - Intercepting messages from sub-widgets and posting other messages with richer context.
 For example, when the date of the item is changed, we emit a custom message `TodoItem.DueDateChanged` instead of letting the message `DatePicker.Selected` bubble up.
 This is good because:
    - it is semantically richer than letting the event `DatePicker.Selected` bubble up;
    - it gives access to the whole compound widget if users wish to know when a TODO item due date changes; and
    - it unburdens the user from tracking what are the sub-widgets that `TodoItem` is composed of.
 - Creating methods that allow containing apps and screens to interact with the widget without having to make assumptions about the widget's internals. For example, we provide a property attribute `date` to access the due date and methods to manipulate the item's status message (`reset_status` and `set_status_message`).

We compose the widget

=== "Output"

    ```{.textual path="docs/examples/guide/compound/todo_item_demo.py" lines=8 press="S,o,m,e,t,h,i,n,g, ,t,o, ,d,o,."}
    ```

=== "todo_item.py"

    ```py hl_lines="17 39 48 53 83-84 93 98 142 148 170-172"
    --8<-- "docs/examples/guide/compound/todo_item_without_css.py"
    ```

    1. The default styling should go here but we omit it for the sake of brevity.
    2. We use this custom message `DueDateChanged`, instead of `DatePicker.Selected`, for when the app user changes the date by which this todo item is due.
    3. We use this custom message to let the container app / screen know that the todo item has had its date cleared.
    4. We use this custom message to let the container app / screen know that the todo item has been marked off as completed.
    5. We use methods from the compound widgets to communicate with them.
    6. This is an example of a sub-widget message that is intercepted and replaced with a richer alternative.
    7. This is a more complex example of a sub-widget message that is intercepted and replaced with a richer alternative, while also letting the widget know that it needs to update itself.
    8. The property attribute `date` enables programmers to interact with the due date of the todo item without having to assume anything about the internals of the widget.
    9. This method resets the status message to an indication of how many days are left till the due date of the item.
    10. This method allows programmers to set custom status messages in the todo item.

=== "todo_item_css.css"

    ```sass
    --8<-- "docs/examples/guide/compound/todo_item_css.css"
    ```

=== "todo_item_demo.py"

    ```py
    --8<-- "docs/examples/guide/compound/todo_item_demo.py"
    ```

!!! Tip

    Whenever relevant, intercept messages from _sub-widgets_ and/or _superclasses_ and post new ones with more context.

For example, in the case of the `TodoItem` widget, it makes sense to post messages like `TodoItem.DueDateChanged` because it will let the container app / screen know which TODO item had its date changed.
If we just used the original message `DatePicker.Selected`, we would not have direct access to the TODO item that had its date changed.

As another example, consider two behaviors that the TODO item has to handle:

 - when the user adds or changes a description to a TODO item; and
 - when the user adds or changes the due date of the TODO item.

These two scenarios are easy to distinguish because `DatePicker` posts the messages `DatePicker.DateCleared` and `DatePicker.Selected`, instead of using the original messages `EditableText.Display` and `EditableText.Edit`.


## TODO App

Now we use the compound widget `TodoItem` to create a simple TODO tracker app.
Our application will allow creating new TODO items, sorting them by due date, and checking them off as complete.

After creating a couple of TODO items, this is what the app looks like:

=== "Output"

    <!--
    1. Create TODO item with description "Update this example"
    n,U,p,d,a,t,e, ,t,h,i,s, ,e,x,a,m,p,l,e,tab,enter,
    2. Change its date to 31-12-2099
    tab,3,1,-,1,2,-,2,0,9,9,tab,enter,
    3. Collapse it
    shift+tab,shift+tab,shift+tab,enter,
    4. Create TODO item with description "Spend time with family!"
    n,S,p,e,n,d, ,t,i,m,e, ,w,i,t,h, ,f,a,m,i,l,y,!,tab,enter,
    5. Change its date to 25-12-1997
    tab,2,5,-,1,2,-,1,9,9,7,tab,enter,
    6. Create empty TODO item
    n
    -->

    ```{.textual path="docs/examples/guide/compound/todo.py" press="n,U,p,d,a,t,e, ,t,h,i,s, ,e,x,a,m,p,l,e,tab,enter,tab,3,1,-,1,2,-,2,0,9,9,tab,enter,shift+tab,shift+tab,shift+tab,enter,n,S,p,e,n,d, ,t,i,m,e, ,w,i,t,h, ,f,a,m,i,l,y,!,tab,enter,tab,2,5,-,1,2,-,1,9,9,7,tab,enter,n"}
    ```

The source code for the app is shown below.
Notice how:

 1. We use the methods defined by `TodoItem` to communicate with the TODO items. For example, instead of reaching for the status label defined in `TodoItem`, we use the method `set_status_message` to set the status message when we create a new item.
 2. We use handlers to figure out when the app needs to react to changes that happened to the widget. For example, we use `on_todo_item_due_date_changed` to sort the TODO item by date and the `on_todo_item_done` to clear the TODO item from its container.

This is the full app source code:

```py hl_lines="28 31-43"
--8<-- "docs/examples/guide/compound/todo.py"
```

1. We call a method on the compound widget `TodoItem` to communicate with it.
2. We define a series of handlers that the `TodoItem` widget uses to communicate with its container app / screen.
