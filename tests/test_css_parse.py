import pytest
from rich.color import Color, ColorType
from rich.style import Style

from textual.css.stylesheet import Stylesheet
from textual.css.transition import Transition


def test_parse_text():
    css = """#some-widget {
        text: on red;
    }
    """
    stylesheet = Stylesheet()
    stylesheet.parse(css)

    rule = stylesheet.rules[0].styles

    assert rule.text_style == Style()
    assert rule.text_background == Color("red", type=ColorType.STANDARD, number=1)


@pytest.mark.parametrize(
    "duration, parsed_duration",
    [["5.57s", 5.57],
     ["0.5s", 0.5],
     ["1200ms", 1.2],
     ["0.5ms", 0.0005]],
)
def test_parse_transition(duration, parsed_duration):
    css = f"""#some-widget {{
        transition: offset {duration} in_out_cubic;
    }}
    """
    stylesheet = Stylesheet()
    stylesheet.parse(css)

    rule = stylesheet.rules[0].styles

    assert len(stylesheet.rules) == 1
    assert len(stylesheet.rules[0].errors) == 0
    assert rule.transitions == {
        "offset": Transition(duration=parsed_duration, easing="in_out_cubic", delay=0.0)
    }
