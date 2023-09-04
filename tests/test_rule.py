import pytest

from textual.widgets import Rule
from textual.widgets.rule import InvalidLineStyle, InvalidRuleOrientation


def test_invalid_rule_orientation():
    with pytest.raises(InvalidRuleOrientation):
        Rule(orientation="invalid orientation!")


def test_invalid_rule_line_style():
    with pytest.raises(InvalidLineStyle):
        Rule(line_style="invalid line style!")


def test_invalid_reactive_rule_orientation_change():
    rule = Rule()
    with pytest.raises(InvalidRuleOrientation):
        rule.orientation = "invalid orientation!"


def test_invalid_reactive_rule_line_style_change():
    rule = Rule()
    with pytest.raises(InvalidLineStyle):
        rule.line_style = "invalid line style!"
