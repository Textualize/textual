# Compound widgets

Compound widgets, like the name suggests, are widgets that are built out of putting together other widgets.

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

This compound widget
