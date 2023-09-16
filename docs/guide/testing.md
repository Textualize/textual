# Testing

Writing test code is an important part of software development.
This chapter will cover how to write tests your Textual apps.

## Do you need to write tests?

The short answer is "no", you don't *need* to write tests.

In practice however, it is almost always a good idea to write tests.
Writing code that is completely bug free is virtually impossible, even for experienced developers.
If you want to have confidence that your application will run as you intended it to, then you should write tests.
Your test code will help you find bugs early, and alert to if you later add code that breaks some other part of your app.

## Testing frameworks for Textual

Textual doesn't require any particular test framework.
You can use any test framework you are familiar with, but for examples in this chapter we will be using [pytest](https://docs.pytest.org/).


## Testing apps

You can often test Textual code in the same way as any other app, and use similar techniques.
But when testing user interface interactions, you may need to use Textual's dedicated test features.

Let's write a simple Textual app so we can demonstrate how to test it.
The following app shows three buttons labelled "red", "green", and "blue".
Clicking one of those buttons or pressing a corresponding ++r++, ++g++, and ++b++ key will change the background color.

=== "rgb.py"

    ```python
    --8<-- "docs/examples/guide/testing/rgb.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/testing/rgb.py"}
    ```

If you were to run this app, you could manually check that is behaving as described.
When an app gets more complicated, it can very laborious to test every possible combination of inputs.
We will write tests to automate this process.

To test our simple app we will use the [`run_test()`][textual.app.App.run_test] method on the `App` class.
This replaces the usual call to [`run()`][textual.app.App.run] and will run the app in *headless* mode, which will prevent Textual from updating the terminal but otherwise work in the same way.

The `run_test()` method is an *async context manager* which returns a [`Pilot`][textual.pilot.Pilot] object.
You can use this object to interact with the app as you were operating it with a keyboard and mouse.

Let's look at the tests for the example above:

```python title="test_rgb.py"
--8<-- "docs/examples/guide/testing/test_rgb.py"
```

1. The `run_test()` method requires that it run in a coroutine, so test must use the `async` keyword.
2. This runs the app and returns a Pilot instance we can use to interact with it.
3. Simulates pressing the ++r++ key.
4. This checks that pressing the ++r++ key has resulted in the background color changing.
5. Simulates clicking on the widget with an `id` of `red` (the button labelled "Red").

There are two tests defined in `test_rgb.py`.
One to tests keys and one to test button clicks.
Both tests first construct an instance of the app and call `run_test()` to get a Pilot object.
The `test_keys` function simulates key presses with [`Pilot.press`][textual.pilot.Pilot.press], and `test_buttons` simulates button clicks with [`Pilot.click`][textual.pilot.Pilot.click].

After simulating interaction, Textual tests will typically check the state has been updated with an `assert` statement.
The `pytest` module will record any failures of these assert statements.

If you run the tests with `pytest test_rgb.py` you should get 2 passes, which will confirm that the user will be able to click buttons or press the keys to change the background color.

If you later update this app, and accidentally break this functionality, one or more of your tests will fail.
Knowing which test has failed will help you quickly track down where your code was broken.

## Simulating key presses

We've seen how the [`press`][textual.pilot.Pilot] method simulates keys.
You can also supply multiple keys to simulate the user typing in to the app.
Here's an example of simulating the user typing the word "hello".

```python
await pilot.press("h", "e", "l", "l", "o")
```

Each string creates a single keypress.
You an also use the name for non-printable keys (such as "enter") and the "ctrl+" modifier.
These are the same identifiers as used for key events, which you can experiment with by running `textual keys`.

## Simulating clicks

We can simulate mouse clicks in a similar way with [`Pilot.click`][textual.pilot.Pilot.click].
If you supply a css selector you can tell Textual which widget to click.

!!! note

    If there is another widget in front of the widget you want to click, you may end up clicking an entirely different widget.
    This is generally what you want, because a real user would experience the same thing.

### Clicking the screen

If you don't supply a CSS selector, then the click will be relative to the screen.
So `await pilot.click()` will simulate a click at (0, 0).

### Click offsets

If you supply an `offset` value, it will be added to the coordinates of the simulated click.
For example `await pilot.click(offset=(10, 5))` would simulate a click at the coordinates (10, 5).

If you combine this with a selector, then the offset will be relative to the widget.
For example `await pilot.click(Button, offset(0, -1))` would click the line above a button.

### Modifier keys

You can simulate keys that are pressed with modifier keys, by setting the `shift`, `meta`, or `control` parameters.
For example `await pilot.click("#slider", control=True)` would simulate clicking a widget with an id of "slider" while holding the control key.

## Waiting for animation

If you have an animation in your app, you may want to wait until it has completed before checking the state.

You can do this with [`Pilot.wait_for_animation`][textual.pilot.Pilot.wait_for_animation], or with [`Pilot.wait_for_scheduled_animations`][textual.pilot.Pilot.wait_for_scheduled_animations] which also wait for any scheduled animations (called with a delay).

## Changing the screen size

The default size of a simulated app is (80, 24).
You may want to test what happens when the app has a different size.
To do this, set the `size` parameter of [`run_test`][textual.app.App.run_test] to a different size.
For example, here is how you would simulate a terminal resized to 100 columns and 50 lines:

```python
async with app.run_test(size=(100, 50)) as pilot:
    ...
```

## Pausing the pilot

Some actions in a Textual app won't change the state immediately.
For instance messages may take a moment to bubble from the widget that sent them.
If you were to post a message and immediately `assert` you may find that it fails because the message hasn't yet been processed.

You can generally solve this by calling [`pause()`][textual.pilot.Pilot.pause] which will wait for all pending messages to be processed.
You can also supply a `delay` parameter, which will insert a delay prior to waiting for pending messages.
