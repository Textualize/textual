from textual.app import App, ComposeResult
from textual.widgets import TextArea
from textual.widgets.text_area import Selection

TEXT = """\
def shrink(self, margin: tuple[int, int, int, int]) -> Region:
    '''Shrink a region by subtracting spacing.

    Args:
        margin: Shrink space by `(<top>, <right>, <bottom>, <left>)`.

    Returns:
        The new, smaller region.
    '''
    if not any(margin):
        return self
    top, right, bottom, left = margin
    x, y, width, height = self
    return Region(
        x=x + left,
        y=y + top,
        width=max(0, width - (left + right)),
        height=max(0, height - (top + bottom)),
    )
"""


class TextAreaExample(App):
    def compose(self) -> ComposeResult:
        text_area = TextArea()
        text_area.load_text(TEXT)
        text_area.language = "python"
        text_area.selection = Selection((0, 0), (3, 7))
        yield text_area


app = TextAreaExample()
if __name__ == "__main__":
    app.run()
