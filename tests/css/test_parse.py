import pytest
from rich.color import Color, ColorType

from textual.css.errors import UnresolvedVariableError
from textual.css.parse import substitute_references
from textual.css.scalar import Scalar, Unit
from textual.css.stylesheet import Stylesheet, StylesheetParseError
from textual.css.tokenize import tokenize
from textual.css.tokenizer import Token
from textual.css.transition import Transition
from textual.layouts.dock import DockLayout


class TestVariableReferenceSubstitution:
    def test_simple_reference(self):
        css = "$x: 1; #some-widget{border: $x;}"
        variables = substitute_references(tokenize(css, ""))
        assert list(variables) == [
            Token(name='variable_name', value='$x:', path='', code=css, location=(0, 0)),
            Token(name='whitespace', value=' ', path='', code=css, location=(0, 3)),
            Token(name='number', value='1', path='', code=css, location=(0, 4)),
            Token(name='variable_value_end', value=';', path='', code=css, location=(0, 5)),
            Token(name='whitespace', value=' ', path='', code=css, location=(0, 6)),
            Token(name='selector_start_id', value='#some-widget', path='', code=css, location=(0, 7)),
            Token(name='declaration_set_start', value='{', path='', code=css, location=(0, 19)),
            Token(name='declaration_name', value='border:', path='', code=css, location=(0, 20)),
            Token(name='whitespace', value=' ', path='', code=css, location=(0, 27)),
            Token(name='number', value='1', path='', code=css, location=(0, 4)),
            Token(name='declaration_end', value=';', path='', code=css, location=(0, 30)),
            Token(name='declaration_set_end', value='}', path='', code=css, location=(0, 31))
        ]

    def test_simple_reference_no_whitespace(self):
        css = "$x:1; #some-widget{border: $x;}"
        variables = substitute_references(tokenize(css, ""))
        assert list(variables) == [
            Token(name='variable_name', value='$x:', path='', code=css, location=(0, 0)),
            Token(name='number', value='1', path='', code=css, location=(0, 3)),
            Token(name='variable_value_end', value=';', path='', code=css, location=(0, 4)),
            Token(name='whitespace', value=' ', path='', code=css, location=(0, 5)),
            Token(name='selector_start_id', value='#some-widget', path='', code=css, location=(0, 6)),
            Token(name='declaration_set_start', value='{', path='', code=css, location=(0, 18)),
            Token(name='declaration_name', value='border:', path='', code=css, location=(0, 19)),
            Token(name='whitespace', value=' ', path='', code=css, location=(0, 26)),
            Token(name='number', value='1', path='', code=css, location=(0, 3)),
            Token(name='declaration_end', value=';', path='', code=css, location=(0, 29)),
            Token(name='declaration_set_end', value='}', path='', code=css, location=(0, 30))
        ]

    def test_undefined_variable(self):
        css = ".thing { border: $not-defined; }"
        with pytest.raises(UnresolvedVariableError):
            list(substitute_references(tokenize(css, "")))

    def test_transitive_reference(self):
        css = "$x: 1\n$y: $x\n.thing { border: $y }"
        assert list(substitute_references(tokenize(css, ""))) == [
            Token(name='variable_name', value='$x:', path='', code=css, location=(0, 0)),
            Token(name='whitespace', value=' ', path='', code=css, location=(0, 3)),
            Token(name='number', value='1', path='', code=css, location=(0, 4)),
            Token(name='variable_value_end', value='\n', path='', code=css, location=(0, 5)),
            Token(name='variable_name', value='$y:', path='', code=css, location=(1, 0)),
            Token(name='whitespace', value=' ', path='', code=css, location=(1, 3)),
            Token(name='number', value='1', path='', code=css, location=(0, 4)),
            Token(name='variable_value_end', value='\n', path='', code=css, location=(1, 6)),
            Token(name='selector_start_class', value='.thing', path='', code=css, location=(2, 0)),
            Token(name='whitespace', value=' ', path='', code=css, location=(2, 6)),
            Token(name='declaration_set_start', value='{', path='', code=css, location=(2, 7)),
            Token(name='whitespace', value=' ', path='', code=css, location=(2, 8)),
            Token(name='declaration_name', value='border:', path='', code=css, location=(2, 9)),
            Token(name='whitespace', value=' ', path='', code=css, location=(2, 16)),
            Token(name='number', value='1', path='', code=css, location=(0, 4)),
            Token(name='whitespace', value=' ', path='', code=css, location=(2, 19)),
            Token(name='declaration_set_end', value='}', path='', code=css, location=(2, 20))
        ]

    def test_multi_value_variable(self):
        css = "$x: 2 4\n$y: 6 $x 2\n.thing { border: $y }"
        assert list(substitute_references(tokenize(css, ""))) == [
            Token(name='variable_name', value='$x:', path='', code=css, location=(0, 0)),
            Token(name='whitespace', value=' ', path='', code=css, location=(0, 3)),
            Token(name='number', value='2', path='', code=css, location=(0, 4)),
            Token(name='whitespace', value=' ', path='', code=css, location=(0, 5)),
            Token(name='number', value='4', path='', code=css, location=(0, 6)),
            Token(name='variable_value_end', value='\n', path='', code=css, location=(0, 7)),
            Token(name='variable_name', value='$y:', path='', code=css, location=(1, 0)),
            Token(name='whitespace', value=' ', path='', code=css, location=(1, 3)),
            Token(name='number', value='6', path='', code=css, location=(1, 4)),
            Token(name='whitespace', value=' ', path='', code=css, location=(1, 5)),
            Token(name='number', value='2', path='', code=css, location=(0, 4)),
            Token(name='whitespace', value=' ', path='', code=css, location=(0, 5)),
            Token(name='number', value='4', path='', code=css, location=(0, 6)),
            Token(name='whitespace', value=' ', path='', code=css, location=(1, 8)),
            Token(name='number', value='2', path='', code=css, location=(1, 9)),
            Token(name='variable_value_end', value='\n', path='', code=css, location=(1, 10)),
            Token(name='selector_start_class', value='.thing', path='', code=css, location=(2, 0)),
            Token(name='whitespace', value=' ', path='', code=css, location=(2, 6)),
            Token(name='declaration_set_start', value='{', path='', code=css, location=(2, 7)),
            Token(name='whitespace', value=' ', path='', code=css, location=(2, 8)),
            Token(name='declaration_name', value='border:', path='', code=css, location=(2, 9)),
            Token(name='whitespace', value=' ', path='', code=css, location=(2, 16)),
            Token(name='number', value='6', path='', code=css, location=(1, 4)),
            Token(name='whitespace', value=' ', path='', code=css, location=(1, 5)),
            Token(name='number', value='2', path='', code=css, location=(0, 4)),
            Token(name='whitespace', value=' ', path='', code=css, location=(0, 5)),
            Token(name='number', value='4', path='', code=css, location=(0, 6)),
            Token(name='whitespace', value=' ', path='', code=css, location=(1, 8)),
            Token(name='number', value='2', path='', code=css, location=(1, 9)),
            Token(name='whitespace', value=' ', path='', code=css, location=(2, 19)),
            Token(name='declaration_set_end', value='}', path='', code=css, location=(2, 20))
        ]


class TestParseLayout:
    def test_valid_layout_name(self):
        css = "#some-widget { layout: dock; }"

        stylesheet = Stylesheet()
        stylesheet.parse(css)

        styles = stylesheet.rules[0].styles
        assert isinstance(styles.layout, DockLayout)

    def test_invalid_layout_name(self):
        css = "#some-widget { layout: invalidlayout; }"

        stylesheet = Stylesheet()
        with pytest.raises(StylesheetParseError) as ex:
            stylesheet.parse(css)

        assert ex.value.errors is not None


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
