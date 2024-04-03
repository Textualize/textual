This example shows all border title and subtitle alignments, together with some examples of how (sub)titles can have custom markup.
Open the code tabs to see the details of the code examples.

=== "Output"

    ```{.textual path="docs/examples/styles/border_sub_title_align_all.py"}
    ```

=== "border_sub_title_align_all.py"

    ```py hl_lines="6 20 26 32 41 42 44 47 53 59 65"
    --8<-- "docs/examples/styles/border_sub_title_align_all.py"
    ```

    1. Border (sub)titles can contain nested markup.
    2. Long (sub)titles get truncated and occupy as much space as possible.
    3. (Sub)titles can be stylised with Rich markup.
    4. An empty (sub)title isn't displayed.
    5. The markup can even contain Rich links.
    6. If the widget does not have a border, the title and subtitle are not shown.
    7. When the side borders are not set, the (sub)title will align with the edge of the widget.
    8. The title and subtitle are aligned on the left and very long, so they get truncated and we can still see the rightmost character of the border edge.
    9. The title and subtitle are centered and very long, so they get truncated and are centered with one character of padding on each side.
    10. The title and subtitle are aligned on the right and very long, so they get truncated and we can still see the leftmost character of the border edge.
    11. An auxiliary function to create labels with border title and subtitle.

=== "border_sub_title_align_all.tcss"

    ```css hl_lines="12 16 30 34 41 46"
    --8<-- "docs/examples/styles/border_sub_title_align_all.tcss"
    ```

    1. The default alignment for the title is `left` and the default alignment for the subtitle is `right`.
    2. Specifying an alignment when the (sub)title is too long has no effect. (Although, it will have an effect if the (sub)title is shortened or if the widget is widened.)
    3. Setting the alignment does not affect empty (sub)titles.
    4. If the border is not set, or set to `none`/`hidden`, the (sub)title is not shown.
    5. If the (sub)title alignment is on a side which does not have a border edge, the (sub)title will be flush to that side.
    6. Naturally, (sub)title positioning is affected by padding.
