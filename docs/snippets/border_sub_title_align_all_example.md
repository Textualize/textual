This example shows all border title and subtitle alignments, together with some examples of how (sub)titles can have custom markup.
Open the code tabs to see the details.

=== "Output"

    ```{.textual path="docs/examples/styles/border_sub_title_align_all.py"}
    ```

=== "border_sub_title_align_all.py"

    ```py hl_lines="6 21-22 27-28 33 40"
    --8<-- "docs/examples/styles/border_sub_title_align_all.py"
    ```

    1. Auxiliary method to create a label and set its title and subtitle.
    2. The title and subtitle support markup.
    3. It can handle unclosed markup tags.
    4. The markup can specify colors for the background and foreground colors.
    5. Links in markup also work.

=== "border_sub_title_align_all.css"

    ```sass hl_lines="14 21 30 41"
    --8<-- "docs/examples/styles/border_sub_title_align_all.css"
    ```

    1. When the title or subtitle is too long, it is wrapped and the alignment does not have any effect.
    2. The default title alignment is `left`.
    3. The default subtitle alignment is `right`.
    4. If the border is not set, or set to `hidden`/`none`, the title and subtitle are not displayed.
