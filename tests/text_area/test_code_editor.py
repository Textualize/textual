import inspect

from textual.widgets import TextArea


def test_code_editor_parameters_kept_up_to_date():
    """Meta test to ensure the `TextArea.code_editor` convenience constructor
    is kept up to date with changes to the `TextArea.__init__` parameters.
    """
    text_area_params = inspect.signature(TextArea.__init__).parameters
    code_editor_params = inspect.signature(TextArea.code_editor).parameters
    expected_diffs = ["theme", "soft_wrap", "tab_behavior", "show_line_numbers"]
    for param in text_area_params:
        if param == "self":
            continue
        assert param in code_editor_params
        if param not in expected_diffs:
            assert code_editor_params[param] == text_area_params[param]
