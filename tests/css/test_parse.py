from __future__ import annotations

import pytest

from textual.color import Color
from textual.css.errors import UnresolvedVariableError
from textual.css.parse import substitute_references
from textual.css.scalar import Scalar, Unit
from textual.css.stylesheet import Stylesheet, StylesheetParseError
from textual.css.tokenize import tokenize
from textual.css.tokenizer import ReferencedBy, Token, TokenError
from textual.css.transition import Transition
from textual.geometry import Spacing
from textual.layouts.vertical import VerticalLayout


class TestVariableReferenceSubstitution:
    def test_simple_reference(self):
        css = "$x: 1; #some-widget{border: $x;}"
        variables = substitute_references(tokenize(css, ("", "")))
        assert list(variables) == [
            Token(
                name="variable_name",
                value="$x:",
                read_from=("", ""),
                code=css,
                location=(0, 0),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(0, 3),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="1",
                read_from=("", ""),
                code=css,
                location=(0, 4),
                referenced_by=None,
            ),
            Token(
                name="variable_value_end",
                value=";",
                read_from=("", ""),
                code=css,
                location=(0, 5),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(0, 6),
                referenced_by=None,
            ),
            Token(
                name="selector_start_id",
                value="#some-widget",
                read_from=("", ""),
                code=css,
                location=(0, 7),
                referenced_by=None,
            ),
            Token(
                name="declaration_set_start",
                value="{",
                read_from=("", ""),
                code=css,
                location=(0, 19),
                referenced_by=None,
            ),
            Token(
                name="declaration_name",
                value="border:",
                read_from=("", ""),
                code=css,
                location=(0, 20),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(0, 27),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="1",
                read_from=("", ""),
                code=css,
                location=(0, 4),
                referenced_by=ReferencedBy(
                    name="x", location=(0, 28), length=2, code=css
                ),
            ),
            Token(
                name="declaration_end",
                value=";",
                read_from=("", ""),
                code=css,
                location=(0, 30),
                referenced_by=None,
            ),
            Token(
                name="declaration_set_end",
                value="}",
                read_from=("", ""),
                code=css,
                location=(0, 31),
                referenced_by=None,
            ),
        ]

    def test_simple_reference_no_whitespace(self):
        css = "$x:1; #some-widget{border: $x;}"
        variables = substitute_references(tokenize(css, ("", "")))
        assert list(variables) == [
            Token(
                name="variable_name",
                value="$x:",
                read_from=("", ""),
                code=css,
                location=(0, 0),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="1",
                read_from=("", ""),
                code=css,
                location=(0, 3),
                referenced_by=None,
            ),
            Token(
                name="variable_value_end",
                value=";",
                read_from=("", ""),
                code=css,
                location=(0, 4),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(0, 5),
                referenced_by=None,
            ),
            Token(
                name="selector_start_id",
                value="#some-widget",
                read_from=("", ""),
                code=css,
                location=(0, 6),
                referenced_by=None,
            ),
            Token(
                name="declaration_set_start",
                value="{",
                read_from=("", ""),
                code=css,
                location=(0, 18),
                referenced_by=None,
            ),
            Token(
                name="declaration_name",
                value="border:",
                read_from=("", ""),
                code=css,
                location=(0, 19),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(0, 26),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="1",
                read_from=("", ""),
                code=css,
                location=(0, 3),
                referenced_by=ReferencedBy(
                    name="x", location=(0, 27), length=2, code=css
                ),
            ),
            Token(
                name="declaration_end",
                value=";",
                read_from=("", ""),
                code=css,
                location=(0, 29),
                referenced_by=None,
            ),
            Token(
                name="declaration_set_end",
                value="}",
                read_from=("", ""),
                code=css,
                location=(0, 30),
                referenced_by=None,
            ),
        ]

    def test_undefined_variable(self):
        css = ".thing { border: $not-defined; }"
        with pytest.raises(UnresolvedVariableError):
            list(substitute_references(tokenize(css, ("", ""))))

    def test_empty_variable(self):
        css = "$x:\n* { background:$x; }"
        result = list(substitute_references(tokenize(css, ("", ""))))
        assert [(t.name, t.value) for t in result] == [
            ("variable_name", "$x:"),
            ("variable_value_end", "\n"),
            ("selector_start_universal", "*"),
            ("whitespace", " "),
            ("declaration_set_start", "{"),
            ("whitespace", " "),
            ("declaration_name", "background:"),
            ("declaration_end", ";"),
            ("whitespace", " "),
            ("declaration_set_end", "}"),
        ]

    def test_transitive_reference(self):
        css = "$x: 1\n$y: $x\n.thing { border: $y }"
        assert list(substitute_references(tokenize(css, ("", "")))) == [
            Token(
                name="variable_name",
                value="$x:",
                read_from=("", ""),
                code=css,
                location=(0, 0),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(0, 3),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="1",
                read_from=("", ""),
                code=css,
                location=(0, 4),
                referenced_by=None,
            ),
            Token(
                name="variable_value_end",
                value="\n",
                read_from=("", ""),
                code=css,
                location=(0, 5),
                referenced_by=None,
            ),
            Token(
                name="variable_name",
                value="$y:",
                read_from=("", ""),
                code=css,
                location=(1, 0),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(1, 3),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="1",
                read_from=("", ""),
                code=css,
                location=(0, 4),
                referenced_by=ReferencedBy(
                    name="x", location=(1, 4), length=2, code=css
                ),
            ),
            Token(
                name="variable_value_end",
                value="\n",
                read_from=("", ""),
                code=css,
                location=(1, 6),
                referenced_by=None,
            ),
            Token(
                name="selector_start_class",
                value=".thing",
                read_from=("", ""),
                code=css,
                location=(2, 0),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(2, 6),
                referenced_by=None,
            ),
            Token(
                name="declaration_set_start",
                value="{",
                read_from=("", ""),
                code=css,
                location=(2, 7),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(2, 8),
                referenced_by=None,
            ),
            Token(
                name="declaration_name",
                value="border:",
                read_from=("", ""),
                code=css,
                location=(2, 9),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(2, 16),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="1",
                read_from=("", ""),
                code=css,
                location=(0, 4),
                referenced_by=ReferencedBy(
                    name="y", location=(2, 17), length=2, code=css
                ),
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(2, 19),
                referenced_by=None,
            ),
            Token(
                name="declaration_set_end",
                value="}",
                read_from=("", ""),
                code=css,
                location=(2, 20),
                referenced_by=None,
            ),
        ]

    def test_multi_value_variable(self):
        css = "$x: 2 4\n$y: 6 $x 2\n.thing { border: $y }"
        assert list(substitute_references(tokenize(css, ("", "")))) == [
            Token(
                name="variable_name",
                value="$x:",
                read_from=("", ""),
                code=css,
                location=(0, 0),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(0, 3),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="2",
                read_from=("", ""),
                code=css,
                location=(0, 4),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(0, 5),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="4",
                read_from=("", ""),
                code=css,
                location=(0, 6),
                referenced_by=None,
            ),
            Token(
                name="variable_value_end",
                value="\n",
                read_from=("", ""),
                code=css,
                location=(0, 7),
                referenced_by=None,
            ),
            Token(
                name="variable_name",
                value="$y:",
                read_from=("", ""),
                code=css,
                location=(1, 0),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(1, 3),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="6",
                read_from=("", ""),
                code=css,
                location=(1, 4),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(1, 5),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="2",
                read_from=("", ""),
                code=css,
                location=(0, 4),
                referenced_by=ReferencedBy(
                    name="x", location=(1, 6), length=2, code=css
                ),
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(0, 5),
                referenced_by=ReferencedBy(
                    name="x", location=(1, 6), length=2, code=css
                ),
            ),
            Token(
                name="number",
                value="4",
                read_from=("", ""),
                code=css,
                location=(0, 6),
                referenced_by=ReferencedBy(
                    name="x", location=(1, 6), length=2, code=css
                ),
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(1, 8),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="2",
                read_from=("", ""),
                code=css,
                location=(1, 9),
                referenced_by=None,
            ),
            Token(
                name="variable_value_end",
                value="\n",
                read_from=("", ""),
                code=css,
                location=(1, 10),
                referenced_by=None,
            ),
            Token(
                name="selector_start_class",
                value=".thing",
                read_from=("", ""),
                code=css,
                location=(2, 0),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(2, 6),
                referenced_by=None,
            ),
            Token(
                name="declaration_set_start",
                value="{",
                read_from=("", ""),
                code=css,
                location=(2, 7),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(2, 8),
                referenced_by=None,
            ),
            Token(
                name="declaration_name",
                value="border:",
                read_from=("", ""),
                code=css,
                location=(2, 9),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(2, 16),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="6",
                read_from=("", ""),
                code=css,
                location=(1, 4),
                referenced_by=ReferencedBy(
                    name="y", location=(2, 17), length=2, code=css
                ),
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(1, 5),
                referenced_by=ReferencedBy(
                    name="y", location=(2, 17), length=2, code=css
                ),
            ),
            Token(
                name="number",
                value="2",
                read_from=("", ""),
                code=css,
                location=(0, 4),
                referenced_by=ReferencedBy(
                    name="y", location=(2, 17), length=2, code=css
                ),
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(0, 5),
                referenced_by=ReferencedBy(
                    name="y", location=(2, 17), length=2, code=css
                ),
            ),
            Token(
                name="number",
                value="4",
                read_from=("", ""),
                code=css,
                location=(0, 6),
                referenced_by=ReferencedBy(
                    name="y", location=(2, 17), length=2, code=css
                ),
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(1, 8),
                referenced_by=ReferencedBy(
                    name="y", location=(2, 17), length=2, code=css
                ),
            ),
            Token(
                name="number",
                value="2",
                read_from=("", ""),
                code=css,
                location=(1, 9),
                referenced_by=ReferencedBy(
                    name="y", location=(2, 17), length=2, code=css
                ),
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(2, 19),
                referenced_by=None,
            ),
            Token(
                name="declaration_set_end",
                value="}",
                read_from=("", ""),
                code=css,
                location=(2, 20),
                referenced_by=None,
            ),
        ]

    def test_variable_used_inside_property_value(self):
        css = "$x: red\n.thing { border: on $x; }"
        assert list(substitute_references(tokenize(css, ("", "")))) == [
            Token(
                name="variable_name",
                value="$x:",
                read_from=("", ""),
                code=css,
                location=(0, 0),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(0, 3),
                referenced_by=None,
            ),
            Token(
                name="token",
                value="red",
                read_from=("", ""),
                code=css,
                location=(0, 4),
                referenced_by=None,
            ),
            Token(
                name="variable_value_end",
                value="\n",
                read_from=("", ""),
                code=css,
                location=(0, 7),
                referenced_by=None,
            ),
            Token(
                name="selector_start_class",
                value=".thing",
                read_from=("", ""),
                code=css,
                location=(1, 0),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(1, 6),
                referenced_by=None,
            ),
            Token(
                name="declaration_set_start",
                value="{",
                read_from=("", ""),
                code=css,
                location=(1, 7),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(1, 8),
                referenced_by=None,
            ),
            Token(
                name="declaration_name",
                value="border:",
                read_from=("", ""),
                code=css,
                location=(1, 9),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(1, 16),
                referenced_by=None,
            ),
            Token(
                name="token",
                value="on",
                read_from=("", ""),
                code=css,
                location=(1, 17),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(1, 19),
                referenced_by=None,
            ),
            Token(
                name="token",
                value="red",
                read_from=("", ""),
                code=css,
                location=(0, 4),
                referenced_by=ReferencedBy(
                    name="x", location=(1, 20), length=2, code=css
                ),
            ),
            Token(
                name="declaration_end",
                value=";",
                read_from=("", ""),
                code=css,
                location=(1, 22),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(1, 23),
                referenced_by=None,
            ),
            Token(
                name="declaration_set_end",
                value="}",
                read_from=("", ""),
                code=css,
                location=(1, 24),
                referenced_by=None,
            ),
        ]

    def test_variable_definition_eof(self):
        css = "$x: 1"
        assert list(substitute_references(tokenize(css, ("", "")))) == [
            Token(
                name="variable_name",
                value="$x:",
                read_from=("", ""),
                code=css,
                location=(0, 0),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(0, 3),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="1",
                read_from=("", ""),
                code=css,
                location=(0, 4),
                referenced_by=None,
            ),
        ]

    def test_variable_reference_whitespace_trimming(self):
        css = "$x:    123;.thing{border: $x}"
        assert list(substitute_references(tokenize(css, ("", "")))) == [
            Token(
                name="variable_name",
                value="$x:",
                read_from=("", ""),
                code=css,
                location=(0, 0),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value="    ",
                read_from=("", ""),
                code=css,
                location=(0, 3),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="123",
                read_from=("", ""),
                code=css,
                location=(0, 7),
                referenced_by=None,
            ),
            Token(
                name="variable_value_end",
                value=";",
                read_from=("", ""),
                code=css,
                location=(0, 10),
                referenced_by=None,
            ),
            Token(
                name="selector_start_class",
                value=".thing",
                read_from=("", ""),
                code=css,
                location=(0, 11),
                referenced_by=None,
            ),
            Token(
                name="declaration_set_start",
                value="{",
                read_from=("", ""),
                code=css,
                location=(0, 17),
                referenced_by=None,
            ),
            Token(
                name="declaration_name",
                value="border:",
                read_from=("", ""),
                code=css,
                location=(0, 18),
                referenced_by=None,
            ),
            Token(
                name="whitespace",
                value=" ",
                read_from=("", ""),
                code=css,
                location=(0, 25),
                referenced_by=None,
            ),
            Token(
                name="number",
                value="123",
                read_from=("", ""),
                code=css,
                location=(0, 7),
                referenced_by=ReferencedBy(
                    name="x", location=(0, 26), length=2, code=css
                ),
            ),
            Token(
                name="declaration_set_end",
                value="}",
                read_from=("", ""),
                code=css,
                location=(0, 28),
                referenced_by=None,
            ),
        ]


class TestParseLayout:
    def test_valid_layout_name(self):
        css = "#some-widget { layout: vertical; }"

        stylesheet = Stylesheet()
        stylesheet.add_source(css)

        styles = stylesheet.rules[0].styles
        assert isinstance(styles.layout, VerticalLayout)

    def test_invalid_layout_name(self):
        css = "#some-widget { layout: invalidlayout; }"

        stylesheet = Stylesheet()
        with pytest.raises(StylesheetParseError) as ex:
            stylesheet.add_source(css)
            stylesheet.parse()

        assert ex.value.errors is not None


class TestParseText:
    def test_foreground(self):
        css = """#some-widget {
            color: green;
        }
        """
        stylesheet = Stylesheet()
        stylesheet.add_source(css)

        styles = stylesheet.rules[0].styles
        assert styles.color == Color.parse("green")

    def test_background(self):
        css = """#some-widget {
            background: red;
        }
        """
        stylesheet = Stylesheet()
        stylesheet.add_source(css)

        styles = stylesheet.rules[0].styles
        assert styles.background == Color.parse("red")


class TestParseColor:
    """More in-depth tests around parsing of CSS colors"""

    @pytest.mark.parametrize(
        "value,result",
        [
            ("rgb(1,255,50)", Color(1, 255, 50)),
            ("rgb( 1, 255,50 )", Color(1, 255, 50)),
            ("rgba( 1, 255,50,0.3 )", Color(1, 255, 50, 0.3)),
            ("rgba( 1, 255,50, 1.3 )", Color(1, 255, 50, 1.0)),
            ("hsl( 180, 50%, 50% )", Color(64, 191, 191)),
            ("hsl(180,50%,50%)", Color(64, 191, 191)),
            ("hsla(180,50%,50%,0.25)", Color(64, 191, 191, 0.25)),
            ("hsla( 180, 50% ,50%,0.25 )", Color(64, 191, 191, 0.25)),
            ("hsla( 180, 50% , 50% , 1.5 )", Color(64, 191, 191)),
        ],
    )
    def test_rgb_and_hsl(self, value, result):
        css = f""".box {{
          color: {value};
        }}
        """
        stylesheet = Stylesheet()
        stylesheet.add_source(css)

        styles = stylesheet.rules[0].styles
        assert styles.color == result


class TestParseOffset:
    @pytest.mark.parametrize(
        "offset_x, parsed_x, offset_y, parsed_y",
        [
            [
                "-5.5%",
                Scalar(-5.5, Unit.PERCENT, Unit.WIDTH),
                "-30%",
                Scalar(-30, Unit.PERCENT, Unit.HEIGHT),
            ],
            [
                "5%",
                Scalar(5, Unit.PERCENT, Unit.WIDTH),
                "40%",
                Scalar(40, Unit.PERCENT, Unit.HEIGHT),
            ],
            [
                "10",
                Scalar(10, Unit.CELLS, Unit.WIDTH),
                "40",
                Scalar(40, Unit.CELLS, Unit.HEIGHT),
            ],
        ],
    )
    def test_composite_rule(self, offset_x, parsed_x, offset_y, parsed_y):
        css = f"""#some-widget {{
            offset: {offset_x} {offset_y};
        }}
        """
        stylesheet = Stylesheet()
        stylesheet.add_source(css)

        styles = stylesheet.rules[0].styles

        assert len(stylesheet.rules) == 1
        assert stylesheet.rules[0].errors == []
        assert styles.offset.x == parsed_x
        assert styles.offset.y == parsed_y

    @pytest.mark.parametrize(
        "offset_x, parsed_x, offset_y, parsed_y",
        [
            [
                "-5.5%",
                Scalar(-5.5, Unit.PERCENT, Unit.WIDTH),
                "-30%",
                Scalar(-30, Unit.PERCENT, Unit.HEIGHT),
            ],
            [
                "5%",
                Scalar(5, Unit.PERCENT, Unit.WIDTH),
                "40%",
                Scalar(40, Unit.PERCENT, Unit.HEIGHT),
            ],
            [
                "-10",
                Scalar(-10, Unit.CELLS, Unit.WIDTH),
                "40",
                Scalar(40, Unit.CELLS, Unit.HEIGHT),
            ],
        ],
    )
    def test_separate_rules(self, offset_x, parsed_x, offset_y, parsed_y):
        css = f"""#some-widget {{
            offset-x: {offset_x};
            offset-y: {offset_y};
        }}
        """
        stylesheet = Stylesheet()
        stylesheet.add_source(css)

        styles = stylesheet.rules[0].styles

        assert len(stylesheet.rules) == 1
        assert stylesheet.rules[0].errors == []
        assert styles.offset.x == parsed_x
        assert styles.offset.y == parsed_y


class TestParseOverflow:
    def test_multiple_enum(self):
        css = "#some-widget { overflow: hidden auto; }"
        stylesheet = Stylesheet()
        stylesheet.add_source(css)

        styles = stylesheet.rules[0].styles

        assert len(stylesheet.rules) == 1
        assert styles.overflow_x == "hidden"
        assert styles.overflow_y == "auto"


class TestParseTransition:
    @pytest.mark.parametrize(
        "duration, parsed_duration",
        [
            ["5.57s", 5.57],
            ["0.5s", 0.5],
            ["1200ms", 1.2],
            ["0.5ms", 0.0005],
            ["20", 20.0],
            ["0.1", 0.1],
        ],
    )
    def test_various_duration_formats(self, duration, parsed_duration):
        easing = "in_out_cubic"
        transition_property = "offset"
        delay = duration
        css = f"""#some-widget {{
            transition: {transition_property} {duration} {easing} {delay};
        }}
        """
        stylesheet = Stylesheet()
        stylesheet.add_source(css)

        styles = stylesheet.rules[0].styles

        assert len(stylesheet.rules) == 1
        assert stylesheet.rules[0].errors == []
        assert styles.transitions == {
            "offset": Transition(
                duration=parsed_duration, easing=easing, delay=parsed_duration
            )
        }

    def test_no_delay_specified(self):
        css = f"#some-widget {{ transition: offset-x 1 in_out_cubic; }}"
        stylesheet = Stylesheet()
        stylesheet.add_source(css)

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
            stylesheet.add_source(css)
            stylesheet.parse()

        rules = stylesheet._parse_rules(css, "foo")
        stylesheet_errors = rules[0].errors

        assert len(stylesheet_errors) == 1
        assert stylesheet_errors[0][0].value == invalid_func_name
        assert ex.value.errors is not None


class TestParseOpacity:
    @pytest.mark.parametrize(
        "css_value, styles_value",
        [
            ["-0.2", 0.0],
            ["0.4", 0.4],
            ["1.3", 1.0],
            ["-20%", 0.0],
            ["25%", 0.25],
            ["128%", 1.0],
        ],
    )
    def test_opacity_to_styles(self, css_value, styles_value):
        css = f"#some-widget {{ text-opacity: {css_value} }}"
        stylesheet = Stylesheet()
        stylesheet.add_source(css)

        assert stylesheet.rules[0].styles.text_opacity == styles_value
        assert not stylesheet.rules[0].errors

    def test_opacity_invalid_value(self):
        css = "#some-widget { text-opacity: 123x }"
        stylesheet = Stylesheet()

        with pytest.raises(StylesheetParseError):
            stylesheet.add_source(css)
            stylesheet.parse()
        rules = stylesheet._parse_rules(css, "foo")
        assert rules[0].errors


class TestParseMargin:
    def test_margin_partial(self):
        css = "#foo {margin: 1; margin-top: 2; margin-right: 3; margin-bottom: -1;}"
        stylesheet = Stylesheet()
        stylesheet.add_source(css)
        assert stylesheet.rules[0].styles.margin == Spacing(2, 3, -1, 1)


class TestParsePadding:
    def test_padding_partial(self):
        css = "#foo {padding: 1; padding-top: 2; padding-right: 3; padding-bottom: -1;}"
        stylesheet = Stylesheet()
        stylesheet.add_source(css)
        assert stylesheet.rules[0].styles.padding == Spacing(2, 3, -1, 1)


class TestParseTextAlign:
    @pytest.mark.parametrize(
        "valid_align", ["left", "start", "center", "right", "end", "justify"]
    )
    def test_text_align(self, valid_align):
        css = f"#foo {{ text-align: {valid_align} }}"
        stylesheet = Stylesheet()
        stylesheet.add_source(css)
        assert stylesheet.rules[0].styles.text_align == valid_align

    def test_text_align_invalid(self):
        css = "#foo { text-align: invalid-value; }"
        stylesheet = Stylesheet()
        with pytest.raises(StylesheetParseError):
            stylesheet.add_source(css)
            stylesheet.parse()
        rules = stylesheet._parse_rules(css, "foo")
        assert rules[0].errors


class TestTypeNames:
    def test_type_no_number(self):
        stylesheet = Stylesheet()
        stylesheet.add_source("TestType {}")
        assert len(stylesheet.rules) == 1

    def test_type_with_number(self):
        stylesheet = Stylesheet()
        stylesheet.add_source("TestType1 {}")
        assert len(stylesheet.rules) == 1

    def test_type_starts_with_number(self):
        stylesheet = Stylesheet()
        stylesheet.add_source("1TestType {}")
        with pytest.raises(TokenError):
            stylesheet.parse()

    def test_combined_type_no_number(self):
        for separator in " >,":
            stylesheet = Stylesheet()
            stylesheet.add_source(f"StartType {separator} TestType {{}}")
            assert len(stylesheet.rules) == 1

    def test_combined_type_with_number(self):
        for separator in " >,":
            stylesheet = Stylesheet()
            stylesheet.add_source(f"StartType {separator} TestType1 {{}}")
            assert len(stylesheet.rules) == 1

    def test_combined_type_starts_with_number(self):
        for separator in " >,":
            stylesheet = Stylesheet()
            stylesheet.add_source(f"StartType {separator} 1TestType {{}}")
            with pytest.raises(TokenError):
                stylesheet.parse()


def test_parse_bad_pseudo_selector():
    """Check unknown selector raises a token error."""

    bad_selector = """\
Widget:foo{
    border: red;
}
    """

    stylesheet = Stylesheet()
    stylesheet.add_source(bad_selector, None)

    with pytest.raises(TokenError) as error:
        stylesheet.parse()

    assert error.value.start == (1, 7)


def test_parse_bad_pseudo_selector_with_suggestion():
    """Check unknown pseudo selector raises token error with correct position."""

    bad_selector = """
Widget:blu {
    border: red;
}
"""

    stylesheet = Stylesheet()
    stylesheet.add_source(bad_selector, None)

    with pytest.raises(TokenError) as error:
        stylesheet.parse()

    assert error.value.start == (2, 7)
