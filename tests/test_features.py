from __future__ import annotations

from textual.app import App


def test_features():
    app = App()
    app._features_string = ""
    assert app.features == set()
    assert app.devtools is None
    assert app.debug is False

    app = App()
    app._features_string = "devtools"
    assert app.features == {"devtools"}
    assert app.devtools is not None
    assert app.debug is False

    app = App()
    app._features_string = "devtools,debug"
    assert app.features == {"devtools", "debug"}
    assert app.devtools is not None
    assert app.debug is True

    app = App()
    app._features_string = "devtools, debug"
    assert app.features == {"devtools", "debug"}
    assert app.devtools is not None
    assert app.debug is True
