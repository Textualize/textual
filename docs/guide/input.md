# Input

This chapter will discuss how to make your app respond to input in the form of key presses and mouse actions.

!!! quote

    More Input!

    &mdash; Johnny Five

## Key events

The most fundamental way to receive input in via [Key](./events/key) events. Let's take a closer look at key events with an app that will display key events as you type.

=== "key01.py"

    ```python title="key01.py" hl_lines="12-13"
    --8<-- "docs/examples/guide/input/key01.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/input/key01.py", press="T,e,x,t,u,a,l,!,_"}
    ```

Note the key event handler which 
