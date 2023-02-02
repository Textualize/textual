# Compound widgets

Compound widgets, like the name suggests, are widgets that are built by combining other widgets.

By using simpler widgets to build more complex widgets you have an easier time building useful applications,
as opposed to the trouble you would have to go through if you implemented everything from scratch.

This chapter will introduce you to the main concepts needed when developing compound widgets.
To that end, we will be building two compound widgets.

We will start by building an editable text widget that shows some text and then contains two buttons:
one lets us edit the text and the other confirms the changes we made to the text.
We will use this simpler compound widget to explain the concepts in a vacuum.

Then, we will build a more complex compound widget and use it in a “real” app to see the concepts applied in practice.
This widget will represent a TODO item in a TODO app and will consist of the editable text widget built previously, plus a checkbox to check the status


## `EditableText`

### Structuring your compound widget

The `EditableText` widget is a widget that contains a label to display text.
If the "edit" button is pressed, the label is switched out and the user sees an input field to edit the text.
When the "confirm" button is pressed again, the label comes back into view to display the new text.

Taking this into account, the widget `EditableText` will need to yield the following sub-widgets in its `compose` method:

 - a `Label` to display the text;
 - an `Input` to allow editing of the text;
 - a `Button` to switch to editing mode; and
 - a `Button` to switch to display mode.

Below you can find the skeleton for our widget `EditableText`, that inherits from `Static` (instead of inheriting directly from `Widget`) because `Static` caches its rendering, on top of other minor but useful things.

=== "editabletext01.py"

    ```py hl_lines="5 8-12"
    --8<-- "docs/examples/guide/compound/editabletext01.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/compound/editabletext01.py" lines=10}
    ```


### Enabling the styling of your compound widget

When you create a compound widget, and especially if you have reusability in mind, you need to set up your widget in such a way that it can be styled as users please.

This may entail documenting well the specific widgets that make up your compound widget or it may include using semantic classes that identify the purpose of the sub-widgets.

In this guide, we will add classes to each sub-widget that identify the purpose of each sub-widget.
There is an added advantage of using classes to identify the components of our compound widget, and that has to do with the fact that you don't have to commit to using a specific class for a specific widget/functionality.

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

=== "editabletext02.css"

    ```sass hl_lines="7 11 17 23 29"
    --8<-- "docs/examples/guide/compound/editabletext02.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/compound/editabletext02.py" lines=10}
    ```

!!! Tip

    The classes have very distinctive names, like `editabletext--input`, to minimise the risk of name clashing in larger applications.
    The same applies to the class `ethidden` that is used to control whether the input or the label are being shown.


### Wiring the components together

We have our four components laid out and styled but we still need to wire them in order to implement the kind of behaviour we want.

To that end, we will do the following modifications:

 - save the sub-widgets as attributes for easier retrieval later;
 - implement a property `is_editing` to determine whether we are in editing mode or not;
 - implement a handler for button presses; and
 - switch between editing and display modes when the buttons are pressed through two methods `switch_to_editing_mode` and `switch_to_display_mode`.

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

    ```py
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
