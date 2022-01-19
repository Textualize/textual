import pytest
from rich.color import Color, ColorType

from textual.css.scalar import Scalar, Unit
from textual.css.stylesheet import Stylesheet, StylesheetParseError
from textual.css.transition import Transition


class TestParseText:
    def test_foreground(self):
        css = """#some-widget {
            text: green;
        }
        """
        stylesheet = Stylesheet()
        stylesheet.parse(css)

        styles = stylesheet.rules[0].styles
        assert styles.text_color == Color.parse("green")

    def test_background(self):
        css = """#some-widget {
            text: on red;
        }
        """
        stylesheet = Stylesheet()
        stylesheet.parse(css)

        styles = stylesheet.rules[0].styles
        assert styles.text_background == Color("red", type=ColorType.STANDARD, number=1)


class TestParseOffset:
    @pytest.mark.parametrize("offset_x, parsed_x, offset_y, parsed_y", [
        ["-5.5%", Scalar(-5.5, Unit.PERCENT, Unit.WIDTH), "-30%", Scalar(-30, Unit.PERCENT, Unit.HEIGHT)],
        ["5%", Scalar(5, Unit.PERCENT, Unit.WIDTH), "40%", Scalar(40, Unit.PERCENT, Unit.HEIGHT)],
        ["10", Scalar(10, Unit.CELLS, Unit.WIDTH), "40", Scalar(40, Unit.CELLS, Unit.HEIGHT)],
    ])
    def test_composite_rule(self, offset_x, parsed_x, offset_y, parsed_y):
        css = f"""#some-widget {{
            offset: {offset_x} {offset_y};
        }}
        """
        stylesheet = Stylesheet()
        stylesheet.parse(css)

        styles = stylesheet.rules[0].styles

        assert len(stylesheet.rules) == 1
        assert stylesheet.rules[0].errors == []
        assert styles.offset.x == parsed_x
        assert styles.offset.y == parsed_y

    @pytest.mark.parametrize("offset_x, parsed_x, offset_y, parsed_y", [
        ["-5.5%", Scalar(-5.5, Unit.PERCENT, Unit.WIDTH), "-30%", Scalar(-30, Unit.PERCENT, Unit.HEIGHT)],
        ["5%", Scalar(5, Unit.PERCENT, Unit.WIDTH), "40%", Scalar(40, Unit.PERCENT, Unit.HEIGHT)],
        ["-10", Scalar(-10, Unit.CELLS, Unit.WIDTH), "40", Scalar(40, Unit.CELLS, Unit.HEIGHT)],
    ])
    def test_separate_rules(self, offset_x, parsed_x, offset_y, parsed_y):
        css = f"""#some-widget {{
            offset-x: {offset_x};
            offset-y: {offset_y};
        }}
        """
        stylesheet = Stylesheet()
        stylesheet.parse(css)

        styles = stylesheet.rules[0].styles

        assert len(stylesheet.rules) == 1
        assert stylesheet.rules[0].errors == []
        assert styles.offset.x == parsed_x
        assert styles.offset.y == parsed_y


class TestParseTransition:
    @pytest.mark.parametrize(
        "duration, parsed_duration", [
            ["5.57s", 5.57],
            ["0.5s", 0.5],
            ["1200ms", 1.2],
            ["0.5ms", 0.0005],
            ["20", 20.],
            ["0.1", 0.1],
        ]
    )
    def test_various_duration_formats(self, duration, parsed_duration):
        easing = "in_out_cubic"
        transition_property = "offset"
        css = f"""#some-widget {{
            transition: {transition_property} {duration} {easing} {duration};
        }}
        """
        stylesheet = Stylesheet()
        stylesheet.parse(css)

        styles = stylesheet.rules[0].styles

        assert len(stylesheet.rules) == 1
        assert stylesheet.rules[0].errors == []
        assert styles.transitions == {
            "offset": Transition(duration=parsed_duration, easing=easing, delay=parsed_duration)
        }

    def test_no_delay_specified(self):
        css = f"#some-widget {{ transition: offset-x 1 in_out_cubic; }}"
        stylesheet = Stylesheet()
        stylesheet.parse(css)

        styles = stylesheet.rules[0].styles

        assert stylesheet.rules[0].errors == []
        assert styles.transitions == {
            "offset-x": Transition(duration=1, easing="in_out_cubic", delay=0)
        }

    def test_unknown_easing_function(self):
        invalid_func_name = "invalid_easing_function"
        css = f"#some-widget {{ transition: offset 1 {invalid_func_name} 1; }}"

        stylesheet = Stylesheet()
        with pytest.raises(StylesheetParseError) as ex:
            stylesheet.parse(css)

        stylesheet_errors = stylesheet.rules[0].errors

        assert len(stylesheet_errors) == 1
        assert stylesheet_errors[0][0].value == invalid_func_name
        assert ex.value.errors is not None
